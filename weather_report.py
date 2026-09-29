# -*- coding: utf-8 -*-
"""
날씨 예보 프로그램 (Open-Meteo API 사용)
- 사용자에게 지역을 입력받음 (기본값: 서울)
- 오늘, 내일, 모레까지 3일간의 날씨를 오전 6시, 오후 3시 기준으로 표시
- Open-Meteo API 사용 (인증키 불필요, 무료)

GitHub 날씨 리포트 주소: https://github.com/edi0oa/weather-report
"""

import json
from datetime import datetime

import requests  # 설치: pip install requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

DEFAULT_CITY = "서울"
FORECAST_DAYS = 3                 # 2일 이상 자유
DAY_LABELS = ["오늘", "내일", "모레", "글피", "그글피", "3일 뒤", "4일 뒤"]
TARGET_HOURS = [(6, "오전", "🌅"), (15, "오후", "🌇")]

# WMO 날씨 코드 -> 한글 설명
WEATHER_CODES = {
    0: "맑음", 1: "주로 맑음", 2: "부분적으로 흐림", 3: "흐림",
    45: "안개", 48: "서리 안개",
    51: "약한 이슬비", 53: "이슬비", 55: "강한 이슬비",
    56: "약한 어는 이슬비", 57: "강한 어는 이슬비",
    61: "약한 비", 63: "비", 65: "강한 비",
    66: "약한 어는 비", 67: "강한 어는 비",
    71: "약한 눈", 73: "눈", 75: "강한 눈", 77: "싸락눈",
    80: "약한 소나기", 81: "소나기", 82: "강한 소나기",
    85: "약한 눈 소나기", 86: "강한 눈 소나기",
    95: "뇌우", 96: "약한 우박 동반 뇌우", 99: "강한 우박 동반 뇌우",
}


def get_coordinates(city):
    """지역 이름 -> (표시 이름, 위도, 경도)"""
    params = {"name": city, "count": 1, "language": "ko", "format": "json"}
    res = requests.get(GEOCODING_URL, params=params, timeout=10)
    res.raise_for_status()
    results = res.json().get("results")
    if not results:
        raise ValueError(f"'{city}' 지역을 찾을 수 없습니다.")
    r = results[0]
    return r.get("name", city), r["latitude"], r["longitude"]


def fetch_weather(lat, lon):
    """Open-Meteo에서 시간별/일별 예보 가져오기"""
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m,"
                  "precipitation_probability,weather_code,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min",
        "wind_speed_unit": "ms",
        "timezone": "auto",
        "forecast_days": FORECAST_DAYS,
    }
    res = requests.get(FORECAST_URL, params=params, timeout=10)
    res.raise_for_status()
    return res.json()


def build_report(city, lat, lon, data):
    """API 응답 -> 출력/저장용 딕셔너리"""
    hourly = data["hourly"]
    index = {t: i for i, t in enumerate(hourly["time"])}
    daily = data["daily"]

    days = []
    for d, date_str in enumerate(daily["time"]):
        slots = []
        for hour, ampm, icon in TARGET_HOURS:
            i = index.get(f"{date_str}T{hour:02d}:00")
            if i is None:
                continue
            slots.append({
                "icon": icon,
                "time": f"{ampm} {hour:02d}:00",
                "weather": WEATHER_CODES.get(hourly["weather_code"][i], "알 수 없음"),
                "temperature": round(hourly["temperature_2m"][i]),
                "precipitation_probability": hourly["precipitation_probability"][i],
                "humidity": hourly["relative_humidity_2m"][i],
                "wind_speed": round(hourly["wind_speed_10m"][i]),
            })
        days.append({
            "label": DAY_LABELS[d],
            "date": datetime.strptime(date_str, "%Y-%m-%d").strftime("%m.%d."),
            "slots": slots,
            "temp_min": round(daily["temperature_2m_min"][d]),
            "temp_max": round(daily["temperature_2m_max"][d]),
        })
    return {
        "city": city,
        "latitude": lat,
        "longitude": lon,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "days": days,
    }


def print_report(report):
    big = "=" * 70
    small = "-" * 55
    print()
    print(big)
    print(f"🌤️ {report['city']} 날씨 예보 (오전 6 시 / 오후 3 시 기준)")
    print(big)
    for day in report["days"]:
        print(f"\n📅 {day['label']} ({day['date']})")
        print(small)
        for s in day["slots"]:
            print(f"\n  {s['icon']} {s['time']}")
            print(f"    날씨: {s['weather']}")
            print(f"    기온: {s['temperature']} °C")
            print(f"    강수확률: {s['precipitation_probability']}%")
            print(f"    습도: {s['humidity']}%")
            print(f"    풍속: {s['wind_speed']} m/s")
        print(f"\n  🌡️ 일일 기온: 최저 {day['temp_min']} °C / 최고 {day['temp_max']} °C")
        print()
        print(big)


def save_json(report):
    filename = f"weather_{report['city']}_{datetime.now():%Y%m%d_%H%M%S}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"💾 저장 완료: {filename}")


def main():
    print("🌤️ 날씨 예보 프로그램 (Open-Meteo API)")
    print("-" * 45)
    print(f"오전 6 시, 오후 3 시 기준으로 {FORECAST_DAYS} 일간 날씨를 제공합니다.")
    print("-" * 45)

    city = input(f"\n날씨를 확인할 지역을 입력하세요 (기본값: {DEFAULT_CITY}): ").strip()
    if not city:
        city = DEFAULT_CITY

    try:
        name, lat, lon = get_coordinates(city)
        print(f"\n📍 {name} (위도: {lat:.4f}, 경도: {lon:.4f}) 의 날씨 정보를 가져옵니다...")
        report = build_report(name, lat, lon, fetch_weather(lat, lon))
    except (requests.RequestException, ValueError) as e:
        print(f"\n❌ 날씨 정보를 가져오지 못했습니다: {e}")
        return

    print_report(report)

    if input("\n날씨 정보를 JSON 파일로 저장하시겠습니까? (y/n): ").strip().lower() == "y":
        save_json(report)


if __name__ == "__main__":
    main()