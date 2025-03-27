import asyncio
from typing import Sequence

from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from data_models.state import ArticleStatus, ArticlesPreprocessingState
from data_models.articles_preprocessing import ArticleSections, SectionContent
from prompts.articles_preprocessing_prompts import extract_articles_sections_prompt, extract_specified_section_prompt


# TODO: we need to determine if article has sections or not
# TODO 2: we need to specify more keywords of things that we should omit. We should describe more accurately what are references and bibliography
def initialize_articles_preprocessing_node(state: ArticlesPreprocessingState) -> ArticlesPreprocessingState:

    # TODO: deduplicate articles!!!!!

    state["processed_articles"] = []
    state["current_article"] = None
    state["work_state"] = {}
    for article in state["arxiv_articles"].articles:
        state["work_state"][article.id] = "unprocessed"
    return state

async def orchestrator_node(state: ArticlesPreprocessingState) -> ArticlesPreprocessingState:
    article = next((a for a in state["arxiv_articles"].articles if state["work_state"].get(a.id) == ArticleStatus.UNPROCESSED), None)
    state["current_article"] = article
    return state

async def get_aticle_structure_node(state: ArticlesPreprocessingState) -> ArticlesPreprocessingState:
    try:
        article_content = state["current_article"].content
        model = ChatOpenAI(model="gpt-4o-mini")

        prompt_template = ChatPromptTemplate.from_messages([
                ("system", extract_articles_sections_prompt),
                ("user", "{user_input}")
        ])
            
        chain = prompt_template | model | PydanticOutputParser(pydantic_object=ArticleSections)
        
        response: ArticleSections = await chain.ainvoke({"user_input": f'Article to extract titles from: {article_content}'})
        state["current_article_sections"] = response.sections 
    except Exception as ex:
        print(ex)
    finally:
        return state

async def get_article_content_chunks(state: ArticlesPreprocessingState) -> ArticlesPreprocessingState:
    try:
        # article_sections: Sequence[str] = []
        # TODO: check which model to use
        model = ChatOpenAI(model="gpt-4o-mini")

        prompt_template = ChatPromptTemplate.from_messages([
                ("system", extract_specified_section_prompt),
                ("user", "{user_input}")
        ])
            
        chain = prompt_template | model | PydanticOutputParser(pydantic_object=SectionContent)

        # TODO: add table math equasion processing
        tasks = [
            chain.ainvoke({"user_input": f'Section to extract title: {section.title}'})
            for section in state["current_article_sections"] if section.type == "text"
        ]
        responses = await asyncio.gather(*tasks)
        article_sections = [r.section_content for r in responses]

        # TODO: add title and abstract 
        article = state["current_article"]
        article.content_paragraphs = article_sections
        state["processed_articles"].append(article)
        state["work_state"][state["current_article"].id] = ArticleStatus.COMPLETED
    except Exception as ex:
        print(ex)
    finally:
        return state

def finalize_articles_preprocessing_node(state: ArticlesPreprocessingState) -> ArticlesPreprocessingState:
    state["arxiv_articles"].articles = state["processed_articles"]
    return state

def should_continue_articles_preprocessing(state: ArticlesPreprocessingState) -> str:
    if state["current_article"]:
        return "get_aticle_structure_node"
    return "finalize_articles_preprocessing_node"

def create_articles_preprocessing_graph() -> StateGraph:
    articles_preprocessing_graph = StateGraph(ArticlesPreprocessingState)
    articles_preprocessing_graph.add_node("initialize_articles_preprocessing_node", initialize_articles_preprocessing_node)
    articles_preprocessing_graph.add_node("orchestrator_node", orchestrator_node)
    articles_preprocessing_graph.add_node("get_aticle_structure_node", get_aticle_structure_node)
    articles_preprocessing_graph.add_node("get_article_content_chunks_node", get_article_content_chunks)
    articles_preprocessing_graph.add_node("finalize_articles_preprocessing_node", finalize_articles_preprocessing_node)

    articles_preprocessing_graph.add_edge(START, "initialize_articles_preprocessing_node")
    articles_preprocessing_graph.add_edge("initialize_articles_preprocessing_node", "orchestrator_node")
    articles_preprocessing_graph.add_edge("orchestrator_node", "get_aticle_structure_node")
    articles_preprocessing_graph.add_edge("get_aticle_structure_node", "get_article_content_chunks_node")
    articles_preprocessing_graph.add_edge("get_article_content_chunks_node", "orchestrator_node")

    articles_preprocessing_graph.add_conditional_edges("orchestrator_node",
                                                       should_continue_articles_preprocessing, 
                                                       ["get_aticle_structure_node", "finalize_articles_preprocessing_node"])
    
    articles_preprocessing_graph.add_edge("finalize_articles_preprocessing_node", END)

    articles_preprocessing_graph = articles_preprocessing_graph.compile()
    return articles_preprocessing_graph
