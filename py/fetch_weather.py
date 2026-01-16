import json
import requests
import time
import os
import math

# Configuration
INPUT_FILE = os.path.join("src", "data", "campgrounds_enriched.json")
OUTPUT_FILE = os.path.join("src", "data", "weather_forecast.json")
BATCH_SIZE = 50  # Open-Meteo allows batching
API_URL = "https://api.open-meteo.com/v1/forecast"

# WMO Weather Code Mapping
# Based on Open-Meteo documentation
WEATHER_CODES = {
    0: {"label": "晴天", "icon": "clear-day"},
    1: {"label": "多雲時晴", "icon": "partly-cloudy-day"},
    2: {"label": "多雲", "icon": "cloudy"},
    3: {"label": "陰天", "icon": "overcast"},
    45: {"label": "霧", "icon": "fog"},
    48: {"label": "霧凇", "icon": "fog"},
    51: {"label": "毛毛雨", "icon": "drizzle"},
    53: {"label": "毛毛雨", "icon": "drizzle"},
    55: {"label": "毛毛雨", "icon": "drizzle"},
    56: {"label": "凍雨", "icon": "sleet"},
    57: {"label": "凍雨", "icon": "sleet"},
    61: {"label": "小雨", "icon": "rain"},
    63: {"label": "中雨", "icon": "rain"},
    65: {"label": "大雨", "icon": "rain"},
    66: {"label": "凍雨", "icon": "sleet"},
    67: {"label": "凍雨", "icon": "sleet"},
    71: {"label": "小雪", "icon": "snow"},
    73: {"label": "中雪", "icon": "snow"},
    75: {"label": "大雪", "icon": "snow"},
    77: {"label": "雪粒", "icon": "snow"},
    80: {"label": "陣雨", "icon": "rain"},
    81: {"label": "陣雨", "icon": "rain"},
    82: {"label": "強陣雨", "icon": "rain"},
    85: {"label": "陣雪", "icon": "snow"},
    86: {"label": "強陣雪", "icon": "snow"},
    95: {"label": "雷雨", "icon": "thunderstorm"},
    96: {"label": "雷雨伴隨冰雹", "icon": "thunderstorm"},
    99: {"label": "雷雨伴隨冰雹", "icon": "thunderstorm"},
}

def get_weather_info(code):
    return WEATHER_CODES.get(code, {"label": "未知", "icon": "cloudy"})

def fetch_weather():
    print("Loading campground data...")
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        network_data = json.load(f)

    # Filter out entries without valid coordinates
    campgrounds = [c for c in network_data if c.get("lat") and c.get("lng")]
    
    print(f"Found {len(campgrounds)} campgrounds with coordinates.")
    
    weather_data = {}
    
    # Process in batches
    total_batches = math.ceil(len(campgrounds) / BATCH_SIZE)
    
    for i in range(total_batches):
        batch = campgrounds[i * BATCH_SIZE : (i + 1) * BATCH_SIZE]
        lats = [str(c["lat"]) for c in batch]
        lngs = [str(c["lng"]) for c in batch]
        
        params = {
            "latitude": ",".join(lats),
            "longitude": ",".join(lngs),
            "daily": "weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "timezone": "auto"
        }
        
        try:
            print(f"Fetching batch {i+1}/{total_batches}...")
            response = requests.get(API_URL, params=params)
            response.raise_for_status()
            results = response.json()
            
            # Open-Meteo returns a list of results if multiple coordinates are provided
            # If only one, it returns a single object.
            # However, since we batch, it should return a list, but wait.
            # If batch size is 1, it returns object.
            # If batch size > 1, it returns list of objects.
            # Actually, Open-Meteo API for multiple points returns a list of JSON objects.
            
            # Handle the case where the batch loop continues but maybe batch size was small (shouldn't happen with logic above unless len=1)
            response_list = results if isinstance(results, list) else [results]

            for idx, item in enumerate(response_list):
                camp_name = batch[idx]["name"]
                daily = item.get("daily", {})
                
                # Construct simplified forecast
                forecast = []
                times = daily.get("time", [])
                codes = daily.get("weathercode", [])
                max_temps = daily.get("temperature_2m_max", [])
                min_temps = daily.get("temperature_2m_min", [])
                precip_probs = daily.get("precipitation_probability_max", [])
                
                for k in range(len(times)):
                    w_code = codes[k]
                    w_info = get_weather_info(w_code)
                    
                    forecast.append({
                        "date": times[k],
                        "max_temp": round(max_temps[k]),
                        "min_temp": round(min_temps[k]),
                        "rain_prob": precip_probs[k],
                        "weather_code": w_code,
                        "label": w_info["label"],
                        "icon": w_info["icon"]
                    })
                
                weather_data[camp_name] = forecast
                
            # Respect rate limits
            time.sleep(1)
            
        except Exception as e:
            print(f"Error fetching batch {i+1}: {e}")
            # Continue to next batch instead of crashing
            continue

    print(f"Saving weather data to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(weather_data, f, ensure_ascii=False, indent=2)
    
    print("Done!")

if __name__ == "__main__":
    fetch_weather()
