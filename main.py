import asyncio
import nest_asyncio

from PIL import Image
from io import BytesIO

from data_models.state import ResearchState
from graph.research_graph import create_research_graph
from utils.api_config_loader import config_api_keys
from utils.yaml_config_loader import load_research_from_yaml

async def main():
    research_graph = create_research_graph()

    # Uncomment the following lines to visualize and debug the graph structure
    # mermaid_code = research_graph.get_graph(xray=True).draw_mermaid()
    # print(mermaid_code)
    # image = Image.open(BytesIO(research_graph.get_graph(xray=True).draw_mermaid_png()))
    # image.show()
    
    research_state = ResearchState(
        research=load_research_from_yaml("research_config.yaml")
    )
    
    config = {"configurable": {"thread_id": "6"}, "recursion_limit": 10000}
    await research_graph.ainvoke(input=research_state, config=config)
    print("Graph execution complete.")

if __name__ == "__main__":
    nest_asyncio.apply()
    config_api_keys()
    asyncio.run(main())