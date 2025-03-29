from data_models.state import ResearchState
from graph.research_data_preparation_graph import create_research_data_preparation_graph
from graph.knowledge_construction_graph import create_kg_construction_graph

from langgraph.graph import StateGraph, START, END


async def init_node(state: ResearchState) -> ResearchState:
    return state

def should_construct_knowledge_graph(state: ResearchState) -> str:
    if state["research"].kg_construction_needed:
        return "create_kg_construction_node"
    return "research_data_preparation_node"

def create_research_graph() -> StateGraph:
    research_graph = StateGraph(ResearchState)

    research_graph.add_node("init_node", init_node)
    research_graph.add_node("create_kg_construction_node", create_kg_construction_graph())
    research_graph.add_node("research_data_preparation_node", create_research_data_preparation_graph())

    research_graph.add_edge(START, "init_node")
    research_graph.add_edge("create_kg_construction_node", "research_data_preparation_node")
    research_graph.add_edge("research_data_preparation_node", END)

    research_graph.add_conditional_edges("init_node",
                                         should_construct_knowledge_graph,
                                         ["create_kg_construction_node", "research_data_preparation_node"])

    print("Research graph constructed and compiled successfully!")
    return research_graph.compile()