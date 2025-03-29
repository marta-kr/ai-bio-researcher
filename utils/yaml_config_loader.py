import yaml
from data_models.research import Research

def load_research_from_yaml(file_path: str) -> Research:
    """
    Load the research configuration from a YAML file and convert it to a Research object.
    """
    with open(file_path, "r") as file:
        research_data = yaml.safe_load(file)
    return Research(**research_data)
