import json
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
from bs4 import BeautifulSoup

def parse_schedule():
    url = "https://kolybude.com/ru/poltava/stepne-poltavska-dilnytsia"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    now_kyiv = datetime.now(ZoneInfo("Europe/Kyiv")).strftime("%Y-%m-%d %H:%M")
    
    status_data = {
        "updated_at": now_kyiv,
        "is_light_on": True,
        "next_change": "По расписанию",
        "message": "Данные получены"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Очищаем текст от лишних пустых строк и пробелов
            clean_text = " ".join(soup.get_text().split())
            
            status_data["message"] = "График актуален"
            status_data["full_text_snippet"] = clean_text[:300]
        else:
            status_data["message"] = f"Ошибка HTTP: {response.status_code}"
            status_data["is_light_on"] = False
            
    except Exception as e:
        status_data["message"] = f"Ошибка: {str(e)}"
        status_data["is_light_on"] = False

    with open("status.json", "w", encoding="utf-8") as f:
        json.dump(status_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    parse_schedule()
