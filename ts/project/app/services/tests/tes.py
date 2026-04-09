import asyncio
from async_vectorizer import AsyncTextVectorizer
from vectorizer import TextVectorizer
from async_qdrant_db import AsyncVectorStorage
from qdrant_db import VectorStorage

# Выносим профили в отдельную константу, чтобы использовать в обоих тестах
PROFILES = [
    {"id": 1, "text": "Люблю аниме, видеоигры, сидеть дома по вечерам", "payload": {"city": "Moscow", "age": 20, "gender": "female"}},
    {"id": 2, "text": "Обожаю клубы, тусовки, громкую музыку и бары", "payload": {"city": "Moscow", "age": 22, "gender": "female"}},
    {"id": 3, "text": "Смотрю аниме, делаю косплей, рисую арты", "payload": {"city": "SPB", "age": 19, "gender": "female"}},
    {"id": 4, "text": "Спортсмен, бегаю по утрам, ЗОЖ, турники", "payload": {"city": "Moscow", "age": 25, "gender": "male"}},
]

def run_sync_tests(model):
    print("\n" + "="*50)
    print("🚀 ЗАПУСК СИНХРОННЫХ ТЕСТОВ")
    print("="*50)
    
    storage = VectorStorage(collection_name="test_collection_sync")
    print("--- 1. Инициализация и очистка базы ---")
    storage.setup_collection()

    print("--- 2. Наполнение базы профилями ---")
    for p in PROFILES:
        vector = model.get_embedding(p["text"])
        storage.upsert_vector(p["id"], vector, p["payload"])

    print("--- 3. Тест обычного поиска ---")
    print("Запрос: 'видеоигры'")
    pos_vec = model.get_embedding('видеоигры')
    print(storage.recommend(positive=pos_vec, negative=None, limit=2))
    print("\n")

    print("--- 4. Тест поиска с жесткими фильтрами ---")
    print("Запрос: 'анимешница', Фильтры: Питер, возраст 18-20")
    pos_vec = model.get_embedding('анимешница')
    print(storage.recommend(positive=pos_vec, filters={"city": "SPB", "age": "18:20"}, limit=2))
    print("\n")

    print("--- 5. Тест Recommend (Positive + Negative) ---")
    print("Позитив: 'аниме', Негатив: 'тусовки'")
    pos_vec = model.get_embedding('аниме')
    neg_vec = model.get_embedding('тусовки')
    print(storage.recommend(positive=pos_vec, negative=neg_vec))
    print("\n")


async def run_async_tests(model):
    print("\n" + "="*50)
    print("⚡ ЗАПУСК АСИНХРОННЫХ ТЕСТОВ")
    print("="*50)
    
    storage = AsyncVectorStorage(collection_name="test_collection_async")
    
    print("--- 1. Инициализация и очистка базы ---")
    await storage.setup_collection()

    print("--- 2. Наполнение базы профилями ---")
    for p in PROFILES:
        vector = await model.get_embedding(p["text"])
        await storage.upsert_vector(p["id"], vector, p["payload"])

    print("--- 3. Тест обычного поиска ---")
    print("Запрос: 'видеоигры'")
    pos_vec = await model.get_embedding('видеоигры')
    a = await storage.recommend(positive=pos_vec, negative=None, limit=2)
    print(a)

    
    print("\n")

    print("--- 4. Тест поиска с жесткими фильтрами ---")
    print("Запрос: 'анимешница', Фильтры: Питер, возраст 18-20")
    pos_vec = await model.get_embedding('анимешница')
    print(await storage.recommend(positive=pos_vec, filters={"city": "SPB", "age": "18:20"}, limit=2))
    print("\n")

    print("--- 5. Тест Recommend (Positive + Negative) ---")
    print("Позитив: 'аниме', Негатив: 'тусовки'")
    pos_vec = await model.get_embedding('аниме')
    neg_vec = await model.get_embedding('тусовки')
    print(await storage.recommend(positive=pos_vec, negative=neg_vec))
    print("\n")


if __name__ == "__main__":
    # Инициализируем модель векторизации один раз (обычно модели тяжелые)
    shared_model = AsyncTextVectorizer()
    
    # Шаг 1: Запускаем синхронные тесты в обычном потоке
    run_sync_tests(TextVectorizer())
    
    # Шаг 2: Запускаем асинхронные тесты через Event Loop
    asyncio.run(run_async_tests(shared_model))