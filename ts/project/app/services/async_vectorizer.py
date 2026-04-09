from transformers import AutoModel, AutoTokenizer
import torch
import torch.nn.functional as F
import asyncio


class AsyncTextVectorizer:
    def __init__(self, model_name: str = "cointegrated/rubert-tiny2"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).eval()

    def _get_embedding_sync(self, text: str) -> list[float]:
        tensors = self.tokenizer(text, padding=True, truncation=True, return_tensors='pt')

        with torch.no_grad():
            outputs = self.model(**tensors)
            cls_embedding = outputs.last_hidden_state[:, 0, :]
            cls_embedding = F.normalize(cls_embedding) 
            return cls_embedding[0].tolist()

    async def get_embedding(self, text: str) -> list[float]:
        return await asyncio.to_thread(self._get_embedding_sync, text)
