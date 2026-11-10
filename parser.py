import json
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
from bs4 import BeautifulSoup
import re

def parse_schedule():
    url = "https://kolybude.com/ru/poltava/stepne-poltavska-dilnytsia"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    now_kyiv = datetime.now(ZoneInfo("Europe/Kyiv")).strftime("%Y-%m-%d %H:%M")
    
    status_data = {
        "updated_at": now_kyiv,
        "is_light_on": True,
        "queue": "3.2",
        "outages": [],
        "duration": "Без света 14 ч",
        "message": "Расписание обновлено"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            page_text = soup.get_text()
            
            # Ищем текст продолжительности отключения
            duration_match = re.search(r"Без света\s*\d+\s*ч", page_text)
            if duration_match:
                status_data["duration"] = duration_match.group(0)
            
            # Ищем все интервалы времени отключений
            times = re.findall(r"\d{2}:\d{2}\s*[-–—]\s*\d{2}:\d{2}", page_text)
            if times:
                unique_times = []
                for t in times:
                    normalized = t.replace("–", "-").replace("—", "-")
                    if normalized not in unique_times:
                        unique_times.append(normalized)
                status_data["outages"] = unique_times[:4] # Берем 4 основных интервала
            
            # Проверяем статус света на текущий момент
            current_hour_min = datetime.now(ZoneInfo("Europe/Kyiv")).strftime("%H:%M")
            is_off = False
            for time_range in status_data["outages"]:
                parts = time_range.split("-")
                if len(parts) == 2:
                    if parts[0].strip() <= current_hour_min <= parts[1].strip():
                        is_off = True
                        break
            
            status_data["is_light_on"] = not is_off
            
    except Exception as e:
        status_data["message"] = f"Ошибка: {str(e)}"

    with open("status.json", "w", encoding="utf-8") as f:
        json.dump(status_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    parse_schedule()
