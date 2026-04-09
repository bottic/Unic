from fastapi import APIRouter, Depends, HTTPException

from schemas.api_models import UpsertRequest, UpsertResponse
from services.async_qdrant_db import AsyncVectorStorage
from services.async_vectorizer import AsyncTextVectorizer
from deps import get_storage, get_vector_maker


router = APIRouter(prefix="/api/v1", tags=["Insert"])

@router.post("/insert", response_model=UpsertResponse)
async def insert(
    data: UpsertRequest,
    storage: AsyncVectorStorage = Depends(get_storage),
    vector_maker: AsyncTextVectorizer = Depends(get_vector_maker),
):
    if await storage.check_vector_exists(data.id):
        raise HTTPException(status_code=400, detail="Point with this id already exists")

    try:
        vector = await vector_maker.get_embedding(data.text)
        result = await storage.upsert_vector(id=data.id, vector=vector, payload=data.payload)
        return UpsertResponse(status=result.status, info=result.info, id=result.id, payload=result.payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))