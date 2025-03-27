from langchain_openai import ChatOpenAI

def get_o1_mini_model():
    return ChatOpenAI(
        model="o1-mini",
    )
def get_o3_mini_model():
    return ChatOpenAI(
        model="o3-mini",
    )