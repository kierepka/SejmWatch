from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class Evidence(BaseModel):
    document_id: str
    page: int = Field(ge=1)
    quote: str = Field(min_length=3)
    url: Optional[str] = None


class Claim(BaseModel):
    claim: str
    affected_entities: List[str] = []
    change_type: Literal[
        "added", "removed", "modified", "deadline_changed", "unknown"
    ]
    previous_value: Optional[str] = None
    current_value: Optional[str] = None
    evidence: List[Evidence] = Field(min_length=1)
    confidence: Literal["high", "medium", "low"]


class Answer(BaseModel):
    answer: str
    evidence: List[Evidence] = Field(min_length=1)
    confidence: Literal["high", "medium", "low"]

