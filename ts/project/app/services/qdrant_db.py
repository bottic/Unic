from typing import Optional
from qdrant_client import QdrantClient
from qdrant_client import models




class VectorStorage:
    def __init__(
        self,
        url: str = "http://localhost:6333",
        collection_name: str = "test_collection",
        vector_size: int = 312,
    ):
        self.collection_name = collection_name
        self.client = QdrantClient(url)
        self.vector_size = vector_size

    def setup_collection(self):
        if not self.client.collection_exists(collection_name=self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=self.vector_size, distance=models.Distance.DOT),
            )

    def upsert_vector(self, id:int, vector:list, payload:dict) -> dict:
        """Update or insert vector"""
        try:
            operation_info =  self.client.upsert(
            collection_name=self.collection_name,
            wait=True,
            # wait=False, для асинхронности
            points=[
                models.PointStruct(id=id, vector=vector, payload=payload),
                ]
            )
        except Exception as e:
            return {'status':'error', 'info':e, 'id':id, 'payload':payload, 'vector':vector}
        
        if operation_info.status == 'completed':
            return {'status':'completed', 'info':operation_info, 'id':id, 'payload':payload, 'vector':vector}
        else:
            return {'status':'error', 'info':operation_info, 'id':id, 'payload':payload, 'vector':vector}

    def _drop(self):
        self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=self.vector_size, distance=models.Distance.DOT),
            )

    """TODO сказать Андрею чтоб передавал диапазон возраста как 'age':'19:21' добавить в позитив тех кого пользователь лайкнул, а в негатив того, ктого он дизлайкнул"""
    def recommend(self, positive:list, negative:Optional[list] = None, filters: Optional[dict[str, str]] = None, limit: int = 1) -> list:

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
            search_result = self.client.query_points(
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
            return  {'points':search_result.points, 'status': 'completed', 'error':None}
        except Exception as e:
            """TODO Подумать как обрабатывать ошибку"""
            search = self.client.query_points(
                collection_name=self.collection_name,
                query=positive,
                limit=limit,
            )

            return {'points':search.points, 'status': 'error', 'error':e}
