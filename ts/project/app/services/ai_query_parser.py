
from ollama import Client
import json


"""TODO посмотреть что можно сделать с думающей(чтоб выводить в чат что она думает)"""
class AIQueryParser:
    def __init__(self, model_name:str = "gemma4:e4b"):
        self.model_name = model_name
        self.prompt = """
        Ты — AI-помощник для дейтинг-приложения. Твоя единственная задача — извлечь из текстового запроса пользователя его предпочтения.
        
        ПРАВИЛА:
        1. ВСЕГДА переводи сленг, профессии и действия в существительные и хобби. (например: "геймер" -> "видеоигры, компьютерные игры", "айтишник" -> "IT, программирование").
        2. Извлеки то, что пользователь ищет (позитив).
        3. Извлеки то, чего пользователь категорически избегает (негатив). Сюда попадают слова после "не", "без", "кроме" и тп.
        4. Если негативных пожеланий нет, оставь поле пустым.
        
        ФОРМАТ ОТВЕТА:
        Верни строго строку JSON формата. Без лишнего текста, без приветствий. Без markdown-блоков. 
        Структура в ответе JSON:
        {"positive": "строка с позитивными признаками","negative": "строка с негативными признаками или пустая строка"}


        """
        self.client = Client()
        
    """TODO: Нужно обернуть в обработку ошибок и добавить логирование"""
    def parse(self, query:str):
        try:
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {'role': 'system', 'content': self.prompt},
                    {'role': 'user', 'content': query}
                ],
                format='json',
                think=False,
                options={'keep_alive': '1h'} 
            )
            parsed_response = json.loads(response['message']['content'])

            return {
                "status": "complited",
                "info": parsed_response,
                "positive": parsed_response.get("positive", ""),
                "negative": parsed_response.get("negative", "")
            }
        except Exception as e:
            print(f"ERROR_LLM'{query}': {e}")
            return {"status": "error", "info": str(e), "positive": query, "negative": ""}
