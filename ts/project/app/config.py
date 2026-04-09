from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection_name: str = "test_collection"
    vector_size: int = 312
    model_name: str = "gemma4:e4b"
    vectorizer_model_name: str = "cointegrated/rubert-tiny2"
    ollama_url: str = "http://localhost:11434"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


settings = Settings()