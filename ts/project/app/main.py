from fastapi import FastAPI
from contextlib import asynccontextmanager

from services.async_qdrant_db import AsyncVectorStorage
from services.async_vectorizer import AsyncTextVectorizer
from services.async_ai_query_parser import AsyncAIQueryParser

from config import settings

from routers import insert_router, update_router, recommend_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    vector_maker = AsyncTextVectorizer(model_name=settings.vectorizer_model_name)
    storage = AsyncVectorStorage(url=settings.qdrant_url, vector_size=settings.vector_size, collection_name=settings.qdrant_collection_name)
    await storage.setup_collection()
    query_parser = AsyncAIQueryParser(model_name=settings.model_name, ollama_url=settings.ollama_url)

    app.state.storage = storage
    app.state.vector_maker = vector_maker
    app.state.query_parser = query_parser
    yield


app = FastAPI(title="AI Dating Service", version="1.0.0", lifespan=lifespan)

app.include_router(insert_router.router)
app.include_router(update_router.router)
app.include_router(recommend_router.router)
