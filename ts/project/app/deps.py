from fastapi import Request

from services.async_qdrant_db import AsyncVectorStorage
from services.async_vectorizer import AsyncTextVectorizer
from services.async_ai_query_parser import AsyncAIQueryParser


def get_storage(request: Request) -> AsyncVectorStorage:
    return request.app.state.storage


def get_vector_maker(request: Request) -> AsyncTextVectorizer:
    return request.app.state.vector_maker


def get_query_parser(request: Request) -> AsyncAIQueryParser:
    return request.app.state.query_parser
