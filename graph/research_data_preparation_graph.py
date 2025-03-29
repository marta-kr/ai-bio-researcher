import asyncio
from typing import Sequence

from kg_rag.rag_provider import RagProvider
from lightrag.base import QueryParam

from data_models.research import KnowledgeGraphQueries, ResearchKnowledge, ResearchKnowledgeExplorationStage, ResearcherResponse, RetrievedKnowledge
from data_models.state import ResearchDataPreparationState
from prompts.research_data_preparation_prompts import researcher_prommpt

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI

from lightrag.llm.openai import openai_embed, o3_mini
from lightrag import LightRAG

rag = None

async def init_node(state: ResearchDataPreparationState) -> ResearchDataPreparationState:
    state["research_knowledge"] = ResearchKnowledge(knowledge=[])
    state["current_kgrag_queries"] = KnowledgeGraphQueries(queries=[])
    state["exploration_stage"] = ResearchKnowledgeExplorationStage.NEED_KG_SEARCH

    rag = RagProvider.get_o3_instance()

    return state

async def researcher_node(state: ResearchDataPreparationState) -> ResearchDataPreparationState:
    try:
        current_knowledge = state["research_knowledge"].prepare_knowledge_for_researcher()
        print(f"Current knowledge: {current_knowledge}")
        messages = [
            HumanMessage(content=researcher_prommpt.format(research_title=state['research'].topic, research_description=state["research"].description, current_knowledge=current_knowledge))
            ]
        prompt_template = ChatPromptTemplate.from_messages(messages)
        o3_mini_model = ChatOpenAI(
        model="o3-mini"
        )
        chain = (
            prompt_template |
            o3_mini_model |
            PydanticOutputParser(pydantic_object=ResearcherResponse)
        )

        response: ResearcherResponse = await chain.ainvoke({})
        state["current_kgrag_queries"].queries = response.queries
        state["exploration_stage"] = response.stage_transition

        if response.stage_transition == ResearchKnowledgeExplorationStage.KNOWLEDGE_READY:
            print("Knowledge is ready for hypothesis generation.")
        else:
            print("Further exploration is needed.")
        return state
    except Exception as e:
        print(f"Error research queries: {e}")
    return state

async def expert_kgrag_node(state: ResearchDataPreparationState) -> ResearchDataPreparationState:
    # TODO: run in parallel
    queries_results: Sequence[RetrievedKnowledge] = []
    for query in state["current_kgrag_queries"].queries:
        response = rag.query(
            query,
            param=QueryParam(mode="mix")
        )
        print(f'Rag query: {query} \n Rag response: {response}')
        result = RetrievedKnowledge(
            query=query,
            retrieved_knowledge=response
        )
        queries_results.append(result)
    state["research_knowledge"].knowledge.extend(queries_results)
    state["current_kgrag_queries"] = KnowledgeGraphQueries(queries=[])
    return state


async def expert_hmdb_node(state: ResearchDataPreparationState) -> ResearchDataPreparationState:
    return state

async def reasoning_paths_provider_node(state: ResearchDataPreparationState) -> ResearchDataPreparationState:
    return state

def achieved_good_knowledge_representation(state: ResearchDataPreparationState) -> str:
    if state["exploration_stage"] == ResearchKnowledgeExplorationStage.NEED_KG_SEARCH:
        return "expert_kgrag_node"
    # TODO: uncomment when we have the HMDB search implemented
    # if state["exploration_stage"] == ResearchKnowledgeExplorationStage.NEED_HMDB_SEARCH:
    #     return "expert_hmdb_node"
    return END

def create_research_data_preparation_graph() -> StateGraph:
    graph = StateGraph(ResearchDataPreparationState)

    graph.add_node("init_node", init_node)
    graph.add_node("researcher_node", researcher_node)
    graph.add_node("expert_kgrag_node", expert_kgrag_node)
    graph.add_node("expert_hmdb_node", expert_hmdb_node)
    graph.add_node("reasoning_paths_provider_node", reasoning_paths_provider_node)

    graph.add_edge(START, "init_node")
    graph.add_edge("init_node", "researcher_node")
    graph.add_edge("expert_kgrag_node", "reasoning_paths_provider_node")
    graph.add_edge("expert_hmdb_node", "reasoning_paths_provider_node")
    graph.add_edge("reasoning_paths_provider_node", "researcher_node")
    
    graph.add_conditional_edges("researcher_node", 
                                achieved_good_knowledge_representation,
                                ["expert_kgrag_node", "expert_hmdb_node", END])
    
    return graph.compile()
