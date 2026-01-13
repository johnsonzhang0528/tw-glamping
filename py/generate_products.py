import os
import json
import time
import requests
from datetime import datetime
from google import genai

import re

# ================= 設定區 =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(BASE_DIR, "..", "src", "data", "products.json")
API_KEY = "AIzaSyB2O9xhxWEVwEEt9GpOss-YhW5JQX2Hf2s" # 主帳號
MODEL_NAME = "gemma-3-27b-it"

client = genai.Client(api_key=API_KEY) if API_KEY else None

def get_current_season_context():
    month = datetime.now().month
    if month in [11, 12, 1, 2]:
        return "冬季/寒流/過年露營", "保暖、圍爐、火鍋、厚睡袋、煤油暖爐"
    elif month in [3, 4, 5]:
        return "春季/賞櫻/梅雨季", "賞花、防雨天幕、輕量化帳篷、野餐墊、防水噴霧"
    elif month in [6, 7, 8]:
        return "夏季/暑假/玩水", "消暑、移動式冷氣、大型戲水池、強力風扇、防蚊液"
    else:
        return "秋季/賞楓/舒適", "氛圍燈串、美學露營、焚火台、手沖咖啡組"

def generate_trending_products():
    print("🛒 啟動商品趨勢分析模組...")
    
    if not client:
        print("❌ No API Key found. Skipping product generation.")
        return
        
    season, keywords = get_current_season_context()
    print(f"🌡️ 當前情境: {season} (關鍵字: {keywords})")
    print(f"⌛ 正在生成商品清單 ({MODEL_NAME})... 請稍候")
    
    prompt = f"""
    【角色設定】
    你是一位台灣頂尖的戶外用品電商總監，精通 SEO 關鍵字佈局與消費者心理學。你非常了解 Momo 購物網上最熱銷的露營商品趨勢。

    【任務目標】
    請根據目前的季節情境「{season}」(參考關鍵字：{keywords})，分析並篩選出 **5 大最具有商業潛力與搜尋熱度** 的露營商品類別。
    針對每個類別，列出 3 款使用者最可能搜尋、且具備高轉化率的具體商品（不要太冷門）。

    【輸出要求】
    1. **標題 (Title)**：必須具備「導購誘因」的類別名稱，包含 emoji，例如「🔥 冬季保暖神器」而非單純「保暖用品」。
    2. **關鍵字 (Keywords)**：請列出該類別對應的 5-8 個 SEO 高流量關鍵字。
    3. **Tags (Campground Tags)**：**非常重要**，請從以下清單中選擇最適合該商品類別的 1-2 個標籤，以便與營地進行媒合：
       [high_altitude, pet_friendly, glamping, general, cooking, sleep, play, forest, riverside]
       (例如：暖爐對應 high_altitude, 戲水玩具對應 play 或 riverside)
    3. **商品連結 (Link)**：請使用 Momo 購物網搜尋連結格式 `https://www.momoshop.com.tw/search/searchShop.jsp?keyword={{商品關鍵字}}&searchType=1`。
       *(重要：務必使用 Momo 官方搜尋連結格式)*
    4. **商品描述 (Desc)**：一句話賣點，直擊痛點 (15字以內)。
    5. **CTA**：簡短有力的行動呼籲 (例如：查優惠、看評價)。
    
    【JSON 結構】
    請直接回傳一個 JSON Array，不要 Markdown code block，格式如下：
    [
      {{
        "id": "category-unique-id",
        "tags": ["high_altitude", "sleep"], 
        "keywords": ["煤油暖爐", "電熱毯"],
        "title": "🔥 類別標題",
        "items": [
           {{ "name": "商品名稱", "price": "$2000起", "link": "...", "desc": "賣點描述", "cta": "查優惠" }}
        ]
      }}
    ]
    """
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        
        # 清洗 Markdown 標記
        raw_text = response.text.replace("```json", "").replace("```", "").strip()
        # 有時候 AI 會在開頭結尾多加文字，嘗試只擷取 [ ... ]
        if "[" in raw_text and "]" in raw_text:
            start = raw_text.find("[")
            end = raw_text.rfind("]") + 1
            raw_text = raw_text[start:end]
            
        product_data = json.loads(raw_text)
        
        # ----------------------------------------
        # 新增流程：自動查價
        # ----------------------------------------
        print("🕵️  開始進行即時查價 (Regex Only)...")
        for category in product_data:
            for item in category.get("items", []):
                link = item.get("link", "")
                if "momoshop.com.tw" in link:
                    real_price = fetch_momo_price_regex(link, item["name"])
                    if real_price:
                        print(f"   ✅ Updated: {item['name']} -> {real_price}")
                        item["price"] = real_price
                    else:
                        print(f"   ❌ Keep original: {item['name']}")
                    # 避免請求過於頻繁
                    time.sleep(1)
        
        # 加上一個固定的置頂廣告 (Klook / 通用)
        fixed_promo = [
            {
                "id": "booking-always",
                "tags": ["always_show"],
                "keywords": ["露營訂位", "營地推薦"],
                "title": "🏕️ 撿便宜營位",
                "items": [
                    { "name": "Klook 露營專區", "price": "95折起", "link": "https://www.klook.com/zh-TW/activity/list/?keywords=露營", "desc": "輸入代碼 CAMP2026 再折$100", "cta": "查詢空位" }
                ]
            }
        ]
        
        final_data = fixed_promo + product_data
        
        # 存檔
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
            
        print(f"💰 成功生成 {len(final_data)} 個熱銷類別並更新至 products.json")
        
    except Exception as e:
        print(f"❌ AI Analysis Failed: {e}")
        # 如果失敗，不要覆蓋舊檔案

def fetch_momo_price_regex(url, item_name):
    """
    Fetches the Momo search page and uses Regex to extract price accurately.
    No cost, fast, and reliable.
    """
    print(f"   🔍 Analysing price for: {item_name} ...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            print(f"      HTTP {resp.status_code} - skipping.")
            return None
        
        # 1. Expand search window for Regex
        full_search_window = resp.text[:100000] 
        
        # 2. Strategy A: Look for JSON data (Most reliable in Momo's current source)
        # Pattern: "price":"3,591" or escaped \"price\":\"3,591\"
        json_price_match = re.search(r'"price":"([0-9,]+)"', full_search_window)
        
        # If standard match fails, try escaped match (common in Momo)
        if not json_price_match:
            json_price_match = re.search(r'\\"price\\":\\"([0-9,]+)\\"', full_search_window)

        if json_price_match:
            price_val = json_price_match.group(1)
            # Filter out suspicious low numbers that might be ids (e.g. "1", "9")
            # Real prices usually are > 100 or contain commas
            if "," in price_val or (price_val.isdigit() and int(price_val) > 50):
                found_price = f"${price_val}"
                # print(f"      ⚡ Fast path (JSON Regex): found {found_price}")
                return found_price

        # 3. Strategy B: HTML structure (formatted price)
        # <b class="price">$9,999</b> or similar
        html_price_match = re.search(r'class="price"[^>]*>.*?\$([0-9,]+)', full_search_window)
        if html_price_match:
                found_price = f"${html_price_match.group(1)}"
                # print(f"      ⚡ Fast path (HTML Regex): found {found_price}")
                return found_price
    
    except Exception as e:
        print(f"   ⚠️ Price fetch failed: {e}")
        return None
    
    return None

if __name__ == "__main__":
    generate_trending_products()
