from typing import Sequence
from data_models.research import KnowledgeGraphQueries, RetrievedKnowledge
from data_models.state import ResearchDataPreparationState, ToolExecutionState
from external.LightRAG.lightrag.base import QueryParam

from langgraph.types import Send
from langgraph.graph import StateGraph, END

from kg_rag.rag_provider import RagProvider


rag = None

def tools_init_node(state: ToolExecutionState):
    rag = RagProvider.get_o3_instance()
    return state

async def kg_rag_node(state: ToolExecutionState) -> ToolExecutionState:
    # TODO: make it work on a new state object
    # queries_results: Sequence[RetrievedKnowledge] = []
    # for query in state["current_kgrag_queries"].queries:
    #     response = rag.query(
    #         query,
    #         param=QueryParam(mode="mix")
    #     )
    #     print(f'Rag query: {query} \n Rag response: {response}')
    #     result = RetrievedKnowledge(
    #         query=query,
    #         retrieved_knowledge=response
    #     )
    #     queries_results.append(result)
    # state["research_knowledge"].knowledge.extend(queries_results)
    # state["current_kgrag_queries"] = KnowledgeGraphQueries(queries=[])
    return state

def txgemma_node(state: ToolExecutionState) -> ToolExecutionState:
    pass

def kegg_node(state: ToolExecutionState) -> ToolExecutionState:
    pass

def reasoning_node(state: ToolExecutionState) -> ToolExecutionState:
    pass

def indra_node(state: ToolExecutionState) -> ToolExecutionState:
    pass

def diffdock_node(state: ToolExecutionState) -> ToolExecutionState:
    pass

def allen_brain_atlas_node(state: ToolExecutionState) -> ToolExecutionState:
    pass

def uniprot_node(state: ToolExecutionState) -> ToolExecutionState:
    pass

def esm3_node(state: ToolExecutionState) -> ToolExecutionState:
    pass

def evo2_node(state: ToolExecutionState) -> ToolExecutionState:
    pass

def tools_decision(state: ToolExecutionState):
    return Send("TxGemma", {})

def create_tools_subgraph() -> StateGraph:
    # TODO: change state object to the tools use unly
    tools_graph = StateGraph(ToolExecutionState)
    
    tools_graph.add_node("init_node", tools_init_node)
    tools_graph.add_node("TxGemma", txgemma_node)
    tools_graph.add_node("KEGG", kegg_node)
    tools_graph.add_node("reasoning", reasoning_node)
    tools_graph.add_node("INDRA", indra_node)
    tools_graph.add_node("DiffDock", diffdock_node)
    tools_graph.add_node("kg_rag", kg_rag_node)
    # Domain-Specific Tool Nodes:
    tools_graph.add_node("UniProt", uniprot_node)
    tools_graph.add_node("ESM3", esm3_node)
    tools_graph.add_node("Evo2", evo2_node)
    
    tools_graph.add_conditional_edges(
         "init_node",
         tools_decision,
         ["TxGemma", "KEGG", "reasoning", "INDRA", "DiffDock", "kg_rag",
          "UniProt", "ESM3", "Evo2"]
    )
    
    for tool in ["TxGemma", "KEGG", "reasoning", "INDRA", "DiffDock",
                 "kg_rag", "UniProt", "ESM3", "Evo2"]:
        tools_graph.add_edge(tool, END)
    
    tools_graph.set_entry_point("init_node")
    return tools_graph.compile()