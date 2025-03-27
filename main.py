import asyncio
import os
import nest_asyncio

from data_models.research import Research
from data_models.state import ResearchState
from graph.research_graph import create_research_graph

# TODO: move to the config file
def config_api_keys():
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

    if OPENAI_API_KEY is None:
        OPENAI_API_KEY = input("Please enter your OpenAI API key: ")
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

async def main():
    research_graph = create_research_graph()

    # Uncomment the following lines to visualize the graph
    # from PIL import Image
    # from io import BytesIO
    # image = Image.open(BytesIO(research_graph.get_graph(xray=True).draw_mermaid_png()))
    # image.show()
    
    # TODO: move this to any JSON or YAML file
    research = Research(
        topic="""Multifactorial Influences on Nervous System Repair in Autoimmune and Neurological Disorders""",
        description="""This research project aims to explore various factors influencing the repair of the nervous system and the progression of autoimmune diseases. It will investigate the interplay between micronutrients (such as alpha lipoic acid, vitamin D, and B vitamins), environmental and lifestyle factors, and pharmacological interventions on disease mechanisms and metabolic pathways. The study will focus on autoimmune diseases like type 1 diabetes and multiple sclerosis, where distinct pathological processes cause nervous system damage, and will also consider other conditions such as long COVID and other autoimmune disorders that result in nervous system impairment. An extensive literature search will be conducted using databases like Arxiv and PubMed, with queries designed to capture both direct aspects of the topic and underlying interdisciplinary connections across medicine, biology, and bioinformatics."""
    )
    
    research_state = ResearchState(
        research=research
    )
    
    config = {"configurable": {"thread_id": "6"}, "recursion_limit": 10000}
    await research_graph.ainvoke(input=research_state, config=config)
    print("Graph execution complete.")

if __name__ == "__main__":
    nest_asyncio.apply()
    config_api_keys()
    asyncio.run(main())