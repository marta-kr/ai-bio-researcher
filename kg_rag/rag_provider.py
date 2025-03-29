from typing import Any
from external.LightRAG.lightrag.lightrag import LightRAG
from external.LightRAG.lightrag.llm.openai import o3_mini, openai_embed, gpt_4o_mini_complete


class RagProvider:
    _o3_instance = None
    _gpt_instance = None
    WORKING_DIR = 'ai-bio-researcher/kg_rag/db'

    @classmethod
    def get_o3_instance(cls) -> LightRAG:
        if cls._o3_instance is None:
            cls._o3_instance = LightRAG(
                working_dir=cls.WORKING_DIR,
                embedding_func=openai_embed,
                llm_model_func=o3_mini
            )
        return cls._o3_instance
    
    @classmethod
    def get_gpt_instance(cls, addon_params: dict[str, Any]) -> LightRAG:
        if cls._gpt_instance is None:
            cls._gpt_instance = LightRAG(
                working_dir=cls.WORKING_DIR,
                embedding_func=openai_embed,
                llm_model_func=gpt_4o_mini_complete,
                addon_params=addon_params
            )
        return cls._gpt_instance