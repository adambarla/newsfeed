from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


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
