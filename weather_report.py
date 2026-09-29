# -*- coding: utf-8 -*-
"""
날씨 예보 프로그램 (Open-Meteo API 사용)
- 사용자에게 지역을 입력받음 (기본값: 서울)
- 오늘, 내일, 모레까지 3일간의 날씨를 오전 6시, 오후 3시 기준으로 표시
- Open-Meteo API 사용 (인증키 불필요, 무료)

GitHub 날씨 리포트 주소: https://github.com/<내-아이디>/<저장소-이름>   # <- 본인 주소로 반드시 수정!
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


def main():
    city = input(f"지역을 입력하세요 (기본값: {DEFAULT_CITY}): ").strip() or DEFAULT_CITY
    name, lat, lon = get_coordinates(city)
    print(f"📍 {name} (위도: {lat:.4f}, 경도: {lon:.4f})")
    data = fetch_weather(lat, lon)
    print("예보 데이터 수신 완료:", len(data["hourly"]["time"]), "개 시간 데이터")


if __name__ == "__main__":
    main()