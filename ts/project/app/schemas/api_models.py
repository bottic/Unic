from pydantic import BaseModel
from typing import Optional, Any


class RecommendationRequest(BaseModel):
    query: str
    limit: int = 1
    filters: Optional[dict[str, str]] = None

class RecommendationResponse(BaseModel):
    status: str
    info: Any
    points: list[Any]

class UpsertRequest(BaseModel):
    id: int
    text: str
    payload: dict[str, Any]

class UpsertResponse(BaseModel):
    status: str
    info: Any
    id: int
    payload: dict[str, Any]


# --- Внутренние модели (возвращаются сервисами, не клиенту напрямую) ---

class UpsertResult(BaseModel):
    """Результат операции upsert из VectorStorage"""
    status: str
    info: Any
    id: int
    payload: dict[str, Any]

class RecommendResult(BaseModel):
    """Результат операции recommend из VectorStorage"""
    status: str
    info: Any
    points: list[Any]

class ParseResult(BaseModel):
    """Результат парсинга запроса из AIQueryParser"""
    status: str
    info: Any
    positive: str
    negative: str