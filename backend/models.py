from typing import Literal

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    query: str = Field(min_length=1, max_length=5000)
    mode: Literal["rag", "agent"] = "rag"
    top_k: int = Field(default=3, ge=1, le=10)
    strategy: Literal["fixed", "sentence"] = "fixed"


class AskResponse(BaseModel):
    mode: str
    answer: str
    sources: list[dict] = Field(default_factory=list)
    refused: bool = False
    citations_valid: bool | None = None
