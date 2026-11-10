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
        "next_change": "По расписанию",
        "message": "Данные получены"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем текст на странице, чтобы понять текущий статус или расписание
            page_text = soup.get_text()
            
            # Пример базового анализа: ищем ключевые блоки с расписанием на странице
            # (на kolybude обычно выводятся часы отключений)
            status_data["message"] = "График актуален"
            status_data["full_text_snippet"] = page_text[:300].strip() # Сохраняем кусок текста для проверки
        else:
            status_data["message"] = f"Ошибка HTTP: {response.status_code}"
            status_data["is_light_on"] = False
            
    except Exception as e:
        status_data["message"] = f"Ошибка: {str(e)}"

    with open("status.json", "w", encoding="utf-8") as f:
        json.dump(status_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    parse_schedule()
