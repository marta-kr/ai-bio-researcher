import uuid
from pydantic import BaseModel, Field, HttpUrl
from typing import Sequence, Optional
from datetime import date
from enum import Enum

class ArxivSearchQuery(BaseModel):
    """A single query to be sent to the arXiv API."""
    query: str

class ArxivSearchQueries(BaseModel):
    """A sequence of search queries."""
    queries: Sequence[ArxivSearchQuery]

class ArxivArticle(BaseModel):
    """A downloaded arXiv article with its metadata."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    summary: str
    content: str
    content_paragraphs: Sequence[str]
    date_published: date
    pdf_url: HttpUrl

class ArxivArticles(BaseModel):
    """A collection of downloaded arXiv articles."""
    articles: Sequence[ArxivArticle]

    def get_article_by_id(self, article_id: str) -> Optional[ArxivArticle]:
        return next((article for article in self.articles if article.id == article_id), None)

class Research(BaseModel):
    """Initial research project data"""
    topic: str
    description: str

class RetrievedKnowledge(BaseModel):
    query: str
    retrieved_knowledge: str

class ResearchKnowledge(BaseModel):
    knowledge: Sequence[RetrievedKnowledge]

    # TODO: move str to prompts file
    def prepare_knowledge_for_researcher(self) -> str:
        if not self.knowledge:
            return "No knowledge was retrieved yet. You can start asking for knowledge from scratch. Begin with high-level questions to get an overview of the availiable data in regards to the current research topics (e.g., “What are the main pathways through which vitamin B influences neuronal health?”). You are quering a knowledge graph so ask such combination of questions that will allow you to see what strategies of asking questions might be helpful to explore the knowledge space."
        # TODO: add additional conditional that if the knowledge exceeds certain length it should be summarized
        structured_knowledge = "You already retrieved some knowledge. You will receive a list of your queries to the knowledge graph and the corresponding knowledge. If you decide to retrieve more data from the knowledge graph at this point, you can use this information to ask more specific questions or to explore the knowledge space further. Please take a notice on how shaping queries impacts the results to create a better strategy to explore the knowledge space completly in regards to the research toipic. Here is the list of your queries and the corresponding knowledge:\n\n"
        for knowledge in self.knowledge:
            structured_knowledge += f"Query: {knowledge.query}\nKnowledge: {knowledge.retrieved_knowledge}\n"
        return structured_knowledge
            
class KnowledgeGraphQueries(BaseModel):
    queries: Sequence[str]

class ResearchKnowledgeExplorationStage(Enum):
    NEED_KG_SEARCH = "need_kg_search"
    NEED_HMDB_SEARCH = "need_hmdb_search"
    KNOWLEDGE_READY = "knowledge_ready"

class ResearcherResponse(BaseModel):
    """A response from the researcher."""
    queries: Sequence[str]
    stage_transition: ResearchKnowledgeExplorationStage
