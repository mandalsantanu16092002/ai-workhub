
from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)


class AnswerSource(BaseModel):
    chunk_index: int
    page_number: int | None
    excerpt: str
    similarity: float


class AskResponse(BaseModel):
    answer: str
    sources: list[AnswerSource]


class GeneratedAnswer(BaseModel):
    answer: str

