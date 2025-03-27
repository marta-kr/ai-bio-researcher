import asyncio
from typing import Sequence
import arxiv

from data_models.research import ArxivArticle, ArxivSearchQueries, ArxivArticles
from data_models.state import KnowledgeGraphConstructionState
from graph.articles_preprocessing_graph import create_articles_preprocessing_graph
from graph.research_data_preparation_graph import create_research_data_preparation_graph
from prompts.research_prompts import generate_arxiv_queries_prompt
from utils.pdf import load_pdf_content

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI

from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
from lightrag import LightRAG

WORKING_DIR = 'ai-bio-researcher/kg_rag/db'

# TODO: init state variables for articles
async def generate_arxiv_queries(state: KnowledgeGraphConstructionState) -> KnowledgeGraphConstructionState:
  try:
    print("Generating queries...")

    messages = [
        HumanMessage(content=generate_arxiv_queries_prompt.format(topic=state['research'].topic, description=state["research"].description))
        ]
    prompt_template = ChatPromptTemplate.from_messages(messages)
    o3_mini_model = ChatOpenAI(
       model="o3-mini"
    )
    chain = (
        prompt_template |
        o3_mini_model |
        PydanticOutputParser(pydantic_object=ArxivSearchQueries)
    )

    response: ArxivSearchQueries = await chain.ainvoke({})
    state['arxiv_search_queries'] = response
    for query in state["arxiv_search_queries"].queries:
       print(query.query)
    return state
  except Exception as e:
    print(f"Error generating queries: {e}")
  return state

async def fetch_and_process_articles_for_query(query: str, max_results: int = 8, full_content: bool = True) -> Sequence[ArxivArticle]:
    """
    For a given search query, fetch articles from arXiv.

    This function uses the arxiv library to search for papers based on the query,
    downloads each article's PDF (if full_content is True) and extracts its text,
    and returns a list of ArxivArticle objects.
    """
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )

    articles: Sequence[ArxivArticle] = []
    for result in search.results():
        content = await load_pdf_content(result.pdf_url) if full_content else ""

        article = ArxivArticle(
            title=result.title,
            summary=result.summary,
            content=content,
            content_paragraphs=[],
            date_published=result.published.date(),
            pdf_url=result.pdf_url
        )
        articles.append(article)
        print(f"Downloaded article title: {result.title} for query: {query}")
    return articles

async def download_arxiv_articles(state: KnowledgeGraphConstructionState) -> KnowledgeGraphConstructionState:
    """
    Node that processes all search queries in the state's arxiv_search_queries,
    downloads the articles for each query in parallel, and saves the results
    in the state's arxive_articles field.
    """
    all_articles: Sequence[ArxivArticle] = []
    queries = [q.query for q in state['arxiv_search_queries'].queries]

    for query in queries:
        print(f"Query: {query}")

    # mock
    # queries = [
    #     "regenerative interventions in multiple sclerosis",
    #     "alpha lipoic acid for nervous system repair in autoimmune diseases"
    #     ]
    
    tasks = [fetch_and_process_articles_for_query(query) for query in queries]

    # Await all tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for query, articles in zip(queries, results):
        if isinstance(articles, Exception):
            print(f"Query '{query}' generated an exception: {articles}")
        else:
            all_articles.extend(articles)

    state['arxiv_articles'] = ArxivArticles(articles=all_articles)
    return state

async def construct_knowledge_graph(state: KnowledgeGraphConstructionState) -> KnowledgeGraphConstructionState:
    rag = LightRAG(
    working_dir=WORKING_DIR,
    embedding_func=openai_embed,
    llm_model_func=gpt_4o_mini_complete,
    addon_params=
    {
       "entity_types": ["disease", "symptom", "drug", "gene", "biological process", "biological system", "cell", "tissue", "organ", "sub-cellular component", "protein", "organism", "experimental procedure", "computational method/algorithm", "health intervention", "scientific tool", "medical device"],
       "example_number": 2
    }
  )
 
    all_articles: Sequence[str] = (article.content for article in state["arxiv_articles"].articles) 

    rag.insert(all_articles)
    return state

def create_kg_construction_graph() -> StateGraph:
    research_graph = StateGraph(KnowledgeGraphConstructionState)
    research_graph.add_node("generate_arxiv_queries", generate_arxiv_queries)
    research_graph.add_node("download_arxiv_articles", download_arxiv_articles)
    # research_graph.add_node("articles_preprocessing", create_articles_preprocessing_graph())
    research_graph.add_node("construct_knowledge_graph", construct_knowledge_graph)

    research_graph.add_edge(START, "generate_arxiv_queries")
    research_graph.add_edge("generate_arxiv_queries", "download_arxiv_articles")
    research_graph.add_edge("download_arxiv_articles", "construct_knowledge_graph")
    # research_graph.add_edge("download_arxiv_articles", "articles_preprocessing")
    # research_graph.add_edge("articles_preprocessing", "construct_knowledge_graph")
    research_graph.add_edge("construct_knowledge_graph", END)

    # print("Research graph constructed and compiled successfully!")
    return research_graph.compile()