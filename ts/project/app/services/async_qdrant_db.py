from typing import Optional
from qdrant_client import AsyncQdrantClient
from qdrant_client import models

from schemas.api_models import UpsertResult, RecommendResult


class AsyncVectorStorage:
    def __init__(
        self,
        url: str = "http://localhost:6333",
        collection_name: str = "test_collection",
        vector_size: int = 312,
    ):
        self.collection_name = collection_name
        self.client = AsyncQdrantClient(url)
        self.vector_size = vector_size

    async def setup_collection(self):
        if not await self.client.collection_exists(collection_name=self.collection_name):
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=self.vector_size, distance=models.Distance.DOT),
            )

    async def upsert_vector(self, id: int, vector: list, payload: dict) -> UpsertResult:
        """Update or insert vector"""
        try:
            operation_info = await self.client.upsert(
                collection_name=self.collection_name,
                wait=True,
                points=[
                    models.PointStruct(id=id, vector=vector, payload=payload),
                ]
            )
        except Exception as e:
            return UpsertResult(status='error', info=str(e), id=id, payload=payload)
        
        if operation_info.status == 'completed':
            return UpsertResult(status='completed', info=str(operation_info), id=id, payload=payload)
        else:
            return UpsertResult(status='error', info=str(operation_info), id=id, payload=payload)

    async def _drop(self):
        await self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=self.vector_size, distance=models.Distance.DOT),
            )

    """TODO сказать Андрею чтоб передавал диапазон возраста как 'age':'19:21'"""
    async def recommend(self, positive: list, negative: Optional[list] = None, filters: Optional[dict[str, str]] = None, limit: Optional[int] = 1) -> RecommendResult:

        match_fields = []
        if filters:
            for key, value in filters.items():
                if key == 'age':
                    value = value.split(':')
                    gte = int(value[0])
                    lte = int(value[1])
                    match_fields.append(models.FieldCondition(key=key, range=models.Range(gte=gte, lte=lte)))
                else:
                    match_fields.append(models.FieldCondition(key=key, match=models.MatchValue(value=value)))

        query_filter = models.Filter(must=match_fields) if match_fields else None

        try:
            search_result = await self.client.query_points(
                collection_name=self.collection_name,
                query=models.RecommendQuery(
                    recommend=models.RecommendInput(
                        positive=[positive],
                        negative=[negative] if negative else [],
                    )
                ),
                query_filter=query_filter,
                with_payload=True,
                limit=limit,
            )

            return RecommendResult(status='completed', info='completed', points=search_result.points)
        except Exception as e:
            search = await self.client.query_points(
                collection_name=self.collection_name,
                query=positive,
                limit=limit,
            )

            return RecommendResult(
                status='error',
                info={
                    'error': str(e),
                    'positive': positive,
                    'negative': negative,
                    'filters': filters,
                    'limit': limit
                },
                points=search.points
            )
                    
    async def check_vector_exists(self, point_id: int) -> bool:
        """
        Проверяет, существует ли вектор с заданным ID в коллекции.
        """
        results = await self.client.retrieve(
            collection_name=self.collection_name,
            ids=[point_id],
            with_payload=False, 
            with_vectors=False  
        )
        
        return len(results) > 0