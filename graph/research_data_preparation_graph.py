import asyncio
from typing import Sequence

from graph.tools_execution_graph import create_tools_subgraph

from data_models.research import KnowledgeGraphQueries, ResearchKnowledge, ResearchKnowledgeExplorationStage
from data_models.state import ResearchDataPreparationState

from langgraph.types import Send
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI

async def init_node(state: ResearchDataPreparationState) -> ResearchDataPreparationState:
    state["research_knowledge"] = ResearchKnowledge(knowledge=[])
    state["current_kgrag_queries"] = KnowledgeGraphQueries(queries=[])
    state["exploration_stage"] = ResearchKnowledgeExplorationStage.NEED_KG_SEARCH

    return state

def knowledge_space_manager_node(state: ResearchDataPreparationState) -> ResearchDataPreparationState:
    pass

def knowledge_aggregator_conflict_resolver_node(state: ResearchDataPreparationState) -> ResearchDataPreparationState:
    pass

def clinical_expert_node(state: ResearchDataPreparationState) -> ResearchDataPreparationState:
    pass

def molecular_expert_node(state: ResearchDataPreparationState) -> ResearchDataPreparationState:
    pass

def immunology_expert_node(state: ResearchDataPreparationState) -> ResearchDataPreparationState:
    pass

def genetics_expert_node(state: ResearchDataPreparationState) -> ResearchDataPreparationState:
    pass

def omics_expert_node(state: ResearchDataPreparationState) -> ResearchDataPreparationState:
    pass

def concatenation_node(state: ResearchDataPreparationState) -> ResearchDataPreparationState:
    pass

def decide_expert_nodes(state):
    """
    Reads the manager's decision from the shared state.
    
    Expected state format:
        state["manager_decision"] = {
            "molecular_expert": 1,
            "immunology_expert": 2,
            "clinical_expert": 0,
            # ... other experts
        }
    
    Returns a list of Send objects, each specifying the destination node and
    additional parameters (if needed). For multiple instances of an expert,
    a unique suffix is appended.
    """
    decision = state.get("manager_decision", {})
    sends = []
    for expert, count in decision.items():
        if count > 0:
            for i in range(count):
                node_name = expert if count == 1 else f"{expert}#{i+1}"
                sends.append(Send(node_name, {}))
    return sends

def clinical_expert_decisions(state: ResearchDataPreparationState):
    return Send("clinical_expert", {})

def molecular_expert_decisions(state: ResearchDataPreparationState):
    return Send("molecular_expert", {})

def immunology_expert_decisions(state: ResearchDataPreparationState):
    return Send("immunology_expert", {})

def genetics_expert_decisions(state: ResearchDataPreparationState):
    return Send("genetics_expert", {})

def omics_expert_decisions(state: ResearchDataPreparationState):
    return Send("omics_expert", {})


def create_research_data_preparation_graph() -> StateGraph:
    graph = StateGraph(ResearchDataPreparationState)
    
    graph.add_node("init_node", init_node)
    graph.add_node("knowledge_space_manager", knowledge_space_manager_node)
    graph.add_node("aggregator", concatenation_node)
    
    graph.add_node("clinical_expert", clinical_expert_node)
    graph.add_node("molecular_expert", molecular_expert_node)
    graph.add_node("immunology_expert", immunology_expert_node)
    graph.add_node("genetics_expert", genetics_expert_node)
    graph.add_node("omics_expert", omics_expert_node)
    
    tools_subgraph = create_tools_subgraph()
    graph.add_node("tools", tools_subgraph)
    
    graph.add_edge(START, "init_node")
    graph.add_edge("init_node", "knowledge_space_manager")
    
    experts_list = [
        "clinical_expert", 
        "molecular_expert", 
        "immunology_expert", 
        "genetics_expert", 
        "omics_expert"
    ]
    graph.add_conditional_edges(
        "knowledge_space_manager",
        decide_expert_nodes,
        experts_list + [END]
    )
    
    graph.add_conditional_edges(
        "clinical_expert", 
        clinical_expert_decisions, 
        ["tools", "aggregator"]
    )
    graph.add_conditional_edges(
        "molecular_expert", 
        molecular_expert_decisions, 
        ["tools", "aggregator"]
    )
    graph.add_conditional_edges(
        "immunology_expert", 
        immunology_expert_decisions, 
        ["tools", "aggregator"]
    )
    graph.add_conditional_edges(
        "genetics_expert", 
        genetics_expert_decisions, 
        ["tools", "aggregator"]
    )
    graph.add_conditional_edges(
        "omics_expert", 
        omics_expert_decisions, 
        ["tools", "aggregator"]
    )
    
    graph.add_edge("tools", "aggregator")
    graph.add_edge("aggregator", "knowledge_space_manager")
    
    return graph.compile()
