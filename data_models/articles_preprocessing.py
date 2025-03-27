from enum import Enum
from typing import Sequence

from pydantic import BaseModel


class ArticleSectionType(str, Enum):
    TEXT = "text"
    TABLE = "table"
    
class ArticleSection(BaseModel):
    title: str
    type: ArticleSectionType

class ArticleSections(BaseModel):
    sections: Sequence[ArticleSection]

class SectionContent(BaseModel):
    section_content: str