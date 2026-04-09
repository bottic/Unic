import asyncio
import datetime
from ai_query_parser import AIQueryParser, AsyncAIQueryParser

test_queries = [
    "ищу геймера, только не тусовщицу",
    "хочу найти спокойную девушку, без вредных привычек, чтобы вместе смотреть аниме",
    "люблю спорт и горы"
]

def run_sync_test(model_name: str):
    print("=== Тестирование СИНХРОННОГО парсера ===")
    parser = AIQueryParser(model_name=model_name)
    
    for query in test_queries:
        print(f"\nЗапрос: '{query}'")
        start = datetime.datetime.now()

        response = parser.parse(query)
        
        print(f"Результат: {response}")
        print(f"Время выполнения: {datetime.datetime.now() - start}")

async def run_async_test(model_name: str):
    print("\n=== Тестирование АСИНХРОННОГО парсера ===")
    parser = AsyncAIQueryParser(model_name=model_name)
    
    for query in test_queries:
        print(f"\nЗапрос: '{query}'")
        start = datetime.datetime.now()
        
        response = await parser.parse(query)
        
        print(f"Результат: {response}")
        print(f"Время выполнения: {datetime.datetime.now() - start}")

if __name__ == "__main__":
    MODEL_NAME = 'gemma4:e4b' 

    run_sync_test(MODEL_NAME)
    
    print("\n" + "="*40 + "\n")

    asyncio.run(run_async_test(MODEL_NAME))