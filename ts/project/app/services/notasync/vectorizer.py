from transformers import AutoModel, AutoTokenizer
import torch
import torch.nn.functional as F

class TextVectorizer:
    def __init__(self, model_name: str = "cointegrated/rubert-tiny2"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).eval()


    def get_embedding(self, text: str) -> list[float]:
        tensors = self.tokenizer(text, padding=True, truncation=True, return_tensors='pt')

        with torch.no_grad():
            outputs = self.model(**tensors)
            cls_embedding = outputs.last_hidden_state[:, 0, :]
            cls_embedding = F.normalize(cls_embedding) # Нормализуем векторы по длине
            return cls_embedding[0].tolist()
