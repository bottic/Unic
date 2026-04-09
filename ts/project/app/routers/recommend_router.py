from fastapi import APIRouter, Depends, HTTPException

from schemas.api_models import RecommendationRequest, RecommendationResponse
from services.async_qdrant_db import AsyncVectorStorage
from services.async_vectorizer import AsyncTextVectorizer
from services.async_ai_query_parser import AsyncAIQueryParser
from deps import get_storage, get_vector_maker, get_query_parser


router = APIRouter(prefix="/api/v1", tags=["Recommend"])

@router.post("/recommend", response_model=RecommendationResponse)
async def recommend(
    data: RecommendationRequest,
    storage: AsyncVectorStorage = Depends(get_storage),
    vector_maker: AsyncTextVectorizer = Depends(get_vector_maker),
    query_parser: AsyncAIQueryParser = Depends(get_query_parser),
):
    parsed_query = await query_parser.parse(data.query)
    if parsed_query.status == "error":
        raise HTTPException(status_code=500, detail={
            "info": parsed_query.info,
            "query": parsed_query.positive})
    
    try:
        pos_vector = await vector_maker.get_embedding(parsed_query.positive)
        neg_vector = await vector_maker.get_embedding(parsed_query.negative) if parsed_query.negative else None
    except Exception as e:
        raise HTTPException(status_code=500, detail={'info': "Error in vectorizer", "error": str(e)}) 

    result = await storage.recommend(
        positive=pos_vector, 
        negative=neg_vector,
        filters=data.filters,
        limit=data.limit)
        
    return RecommendationResponse(status=result.status, info=result.info, points=result.points)
