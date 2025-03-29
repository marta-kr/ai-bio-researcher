import os


def config_api_keys():
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

    if OPENAI_API_KEY is None:
        OPENAI_API_KEY = input("Please enter your OpenAI API key: ")
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY