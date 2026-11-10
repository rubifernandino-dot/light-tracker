import json
from datetime import datetime

def generate_status():
    # Заготовка под статус отключений
    data = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "is_light_on": True, # True - свет есть, False - света нет
        "next_change": "15:00", # Время следующего переключения
        "message": "Свет есть по графику."
    }
    
    with open("status.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    generate_status()
