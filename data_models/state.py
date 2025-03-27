from enum import Enum
from typing import Dict, Optional, Sequence
from data_models.research import ArxivArticle, ArxivSearchQueries, ArxivArticles, KnowledgeGraphQueries, Research, ResearchKnowledge, ResearchKnowledgeExplorationStage
from data_models.articles_preprocessing import ArticleSection
from typing_extensions import TypedDict

class ResearchState(TypedDict):
    research: Research

class KnowledgeGraphConstructionState(TypedDict):
    research: Research

    arxiv_search_queries: ArxivSearchQueries
    arxiv_articles: ArxivArticles

class ArticleStatus(str, Enum):
    UNPROCESSED = "unprocessed"
    COMPLETED = "completed"

class ArticlesPreprocessingState(TypedDict):
    arxiv_articles: ArxivArticles

    work_state: Dict[str, ArticleStatus]
    current_article: Optional[ArxivArticle]
    current_article_sections: Sequence[ArticleSection]
    current_article_sections_content: Sequence[str]

    processed_articles: Sequence[ArxivArticle]

class ResearchDataPreparationState(TypedDict):
    research: Research

    exploration_stage: ResearchKnowledgeExplorationStage
    research_knowledge : ResearchKnowledge
    current_kgrag_queries: KnowledgeGraphQueries

