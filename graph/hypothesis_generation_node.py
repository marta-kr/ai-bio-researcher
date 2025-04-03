from data_models.state import HypothesisGenerationState
from graph.tools_execution_graph import create_tools_subgraph

from langgraph.types import Send
from langgraph.graph import StateGraph, START, END


def init_node(state: HypothesisGenerationState) -> HypothesisGenerationState:
    return state

def initial_brainstorming_node(state: HypothesisGenerationState) -> HypothesisGenerationState:
    return state

def main_hypothesis_agent_node(state: HypothesisGenerationState) -> HypothesisGenerationState:
    return state

def opportunity_agent_node(state: HypothesisGenerationState) -> HypothesisGenerationState:
    return state

def critic_agent_node(state: HypothesisGenerationState) -> HypothesisGenerationState:
    return state

def knowledge_cross_evaluation_agent_node(state: HypothesisGenerationState) -> HypothesisGenerationState:
    return state

def hypothesis_evaluation_node(state: HypothesisGenerationState) -> HypothesisGenerationState:
    return state

def final_reflections_and_refinement_node(state: HypothesisGenerationState) -> HypothesisGenerationState:
    return state

def write_report_node(state: HypothesisGenerationState) -> HypothesisGenerationState:
    return state

def aggregate_reports_node(state: HypothesisGenerationState) -> HypothesisGenerationState:
    return state

def initial_brainstorming_decisions(state: HypothesisGenerationState):
    return Send("initial_brainstorming", {})

def knowledge_cross_evaluation_decisions(state: HypothesisGenerationState):
    return Send("knowledge_cross_evaluation", {})

def create_hypothesis_generation_graph() -> StateGraph:
    graph = StateGraph(HypothesisGenerationState)

    graph.add_node("init_node", init_node)
    graph.add_node("initial_brainstorming_node", initial_brainstorming_node)

    graph.add_node("main_hypothesis_agent", main_hypothesis_agent_node)
    graph.add_node("opportunity_agent", opportunity_agent_node)
    graph.add_node("critic_agent", critic_agent_node)
    graph.add_node("knowledge_cross_evaluation_agent", knowledge_cross_evaluation_agent_node)
    graph.add_node("hypothesis_evaluation", hypothesis_evaluation_node)
    graph.add_node("final_reflections_and_refinement", final_reflections_and_refinement_node)
    graph.add_node("write_report", write_report_node)
    graph.add_node("aggregate_reports", aggregate_reports_node)

    tools_subgraph = create_tools_subgraph()
    graph.add_node("hypothesis_evaluation_tools", tools_subgraph)

    graph.add_edge("init_node", "initial_brainstorming_node")

    graph.add_conditional_edges(
        "initial_brainstorming_node", 
        initial_brainstorming_decisions, 
        ["main_hypothesis_agent", "opportunity_agent", "critic_agent", "knowledge_cross_evaluation_agent"]
    )

    graph.add_edge("main_hypothesis_agent", "initial_brainstorming_node")
    graph.add_edge("opportunity_agent", "initial_brainstorming_node")
    graph.add_edge("critic_agent", "initial_brainstorming_node")
    graph.add_edge("hypothesis_evaluation_tools", "knowledge_cross_evaluation_agent")

    graph.add_conditional_edges(
        "knowledge_cross_evaluation_agent", 
        knowledge_cross_evaluation_decisions, 
        ["hypothesis_evaluation_tools", "hypothesis_evaluation", "final_reflections_and_refinement"]
    )

    graph.add_edge("hypothesis_evaluation_tools", "knowledge_cross_evaluation_agent")
    graph.add_edge("hypothesis_evaluation", "knowledge_cross_evaluation_agent")
    graph.add_edge("final_reflections_and_refinement", "write_report")
    graph.add_edge("write_report", "aggregate_reports")
    graph.add_edge("aggregate_reports", END)

    graph.set_entry_point("init_node")

    return graph.compile()

