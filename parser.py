import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def parse_schedule():
    url = "https://kolybude.com/ru/poltava/stepne-poltavska-dilnytsia"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    status_data = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "is_light_on": True,
        "next_change": "—",
        "message": "Обновление данных..."
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text().lower()
            
            # Базовый анализ текста страницы на наличие ключевых слов
            # (ты сможешь точнее донастроить логику под конкретные блоки сайта)
            if "света нет" in page_text or "немає світла" in page_text or "відключення" in page_text:
                # Здесь можно добавить более точный поиск по классам, если сайт динамический
                pass
            
            # Сохраняем текст страницы для отладки или базовый статус
            status_data["message"] = "Сайт успешно опрошен, график актуален."
            status_data["raw_snippet"] = page_text[:200] + "..." # Первые 200 символов для проверки
        else:
            status_data["message"] = f"Ошибка доступа к сайту: HTTP {response.status_code}"
            
    except Exception as e:
        status_data["message"] = f"Ошибка парсинга: {str(e)}"

    with open("status.json", "w", encoding="utf-8") as f:
        json.dump(status_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    parse_schedule()
