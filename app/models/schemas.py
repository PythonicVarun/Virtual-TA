from typing import List, Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    image: Optional[str] = None


class Link(BaseModel):
    url: str
    text: str


class ChatResponse(BaseModel):
    answer: str
    links: List[Link]
