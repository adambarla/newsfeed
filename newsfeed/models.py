from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, JSON, Column


@dataclass
class RawArticle:
    url: str
    title: str
    content: str
    source: str
    published_at: datetime
    author: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    image_url: Optional[str] = None


class NewsCategory(str, Enum):
    CYBERSECURITY = "Cybersecurity"
    AI_EMERGING_TECH = "Artificial Intelligence & Emerging Tech"
    SOFTWARE_DEVELOPMENT = "Software & Development"
    HARDWARE_DEVICES = "Hardware & Devices"
    TECH_INDUSTRY_BUSINESS = "Tech Industry & Business"
    OTHER = "Other"


class ProcessedArticle(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    url: str = Field(index=True, unique=True)
    title: str
    content: str
    category: NewsCategory
    source: str
    published_at: datetime
    created_at: datetime = Field(default_factory=datetime.now)

    # Storing tags and other metadata as JSON
    # SQLite doesn't have a native array type, so we use JSON
    metadata_fields: dict = Field(default_factory=dict, sa_column=Column(JSON))

    # We won't store the embedding directly in the main SQL table for now,
    # or strictly as a column, usually it's in the vector store.
    # But if we wanted to simple store it:
    # embedding: Optional[List[float]] = Field(default=None, sa_column=Column(JSON))
