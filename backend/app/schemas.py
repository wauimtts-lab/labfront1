from typing import List, Optional

from pydantic import BaseModel


class Exhibit(BaseModel):
    id: str
    name: str
    author: str
    year: int
    type: str
    epoch: str
    style: str
    themes: List[str]
    museum: str
    hall: Optional[str] = None
    description: str


class AskRequest(BaseModel):
    query: str


class AskResponse(BaseModel):
    answer: str
    sources: List[str] = []
