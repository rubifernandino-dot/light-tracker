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
    
    now_kyiv = datetime.now(ZoneInfo("Europe/Kyiv"))
    updated_str = now_kyiv.strftime("%d.%m в %H:%M")
    
    status_data = {
        "updated_at": now_kyiv.strftime("%Y-%m-%d %H:%M"),
        "is_light_on": True,
        "queue": "3.2",
        "outages": [],
        "duration": "По графику",
        "message": "Расписание обновлено"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            page_text = soup.get_text()
            
            duration_match = re.search(r"Без света\s*\d+\s*ч", page_text)
            if duration_match:
                status_data["duration"] = duration_match.group(0)
            
            times = re.findall(r"\d{2}:\d{2}\s*[-–—]\s*\d{2}:\d{2}", page_text)
            if times:
                unique_times = []
                for t in times:
                    normalized = t.replace("-", " – ").replace("–", " – ").replace("—", " – ")
                    normalized = re.sub(r"\s+", " ", normalized).strip()
                    if normalized not in unique_times:
                        unique_times.append(normalized)
                status_data["outages"] = unique_times[:6]
            
            current_hour_min = now_kyiv.strftime("%H:%M")
            is_off = False
            for time_range in status_data["outages"]:
                parts = time_range.split("–")
                if len(parts) == 2:
                    if parts[0].strip() <= current_hour_min <= parts[1].strip():
                        is_off = True
                        break
            status_data["is_light_on"] = not is_off
    except Exception as e:
        status_data["message"] = f"Ошибка: {str(e)}"

    with open("status.json", "w", encoding="utf-8") as f:
        json.dump(status_data, f, ensure_ascii=False, indent=2)

    # Генерируем HTML-блоки интервалов с иконкой молнии
    zap_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="#f2564d" stroke="#f2564d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"></path></svg>'
    
    intervals_html = ""
    for interval in status_data["outages"]:
        intervals_html += f'<div class="time-item">{zap_svg}<span>{interval}</span></div>'
    
    if not intervals_html:
        intervals_html = '<div class="time-item">Отключений не найдено</div>'

    html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="300">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
  body {{ background: transparent; padding: 4px; }}
  .card {{ background: #ffffff; border-radius: 18px; padding: 14px; border: 1px solid rgba(60,70,120,0.12); box-shadow: 0 4px 12px rgba(40,50,110,0.06); }}
  .header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }}
  .icon-box {{ width: 38px; height: 38px; border-radius: 11px; background: linear-gradient(180deg, #5aa9ff, #007aff); display: grid; place-items: center; color: white; flex-shrink: 0; }}
  .title {{ font-size: 16px; font-weight: 700; color: #111827; }}
  .updated {{ font-size: 12px; color: #6b7280; margin-top: 2px; }}
  .inner-box {{ background: #f6f7fb; border-radius: 12px; padding: 12px; }}
  .top-row {{ display: flex; justify-content: space-between; align-items: center; }}
  .badge-queue {{ background: #ffd60a; color: #111827; font-weight: 700; font-size: 13px; padding: 4px 12px; border-radius: 7px; }}
  .badge-duration {{ background: rgba(255,59,48,0.10); color: #a3000f; font-weight: 600; font-size: 12px; padding: 4px 10px; border-radius: 999px; }}
  .divider {{ height: 1px; background: rgba(60,70,120,0.10); margin: 10px 0; }}
  .times-grid {{ display: flex; flex-wrap: wrap; column-gap: 18px; row-gap: 8px; }}
  .time-item {{ display: inline-flex; align-items: center; gap: 6px; font-size: 15px; font-weight: 600; color: #111827; font-variant-numeric: tabular-nums; }}
</style>
</head>
<body>
  <div class="card">
    <div class="header">
      <div class="icon-box">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"></rect><path d="M21 9H3"></path><path d="M21 15H3"></path></svg>
      </div>
      <div>
        <div class="title">График (Степное)</div>
        <div class="updated">Обновлено {updated_str}</div>
      </div>
    </div>
    <div class="inner-box">
      <div class="top-row">
        <span class="badge-queue">{status_data["queue"]}</span>
        <span class="badge-duration">{status_data["duration"]}</span>
      </div>
      <div class="divider"></div>
      <div class="times-grid">
        {intervals_html}
      </div>
    </div>
  </div>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    parse_schedule()
