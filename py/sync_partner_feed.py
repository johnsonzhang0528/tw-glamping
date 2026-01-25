import json
import os
import requests
import time
from pathlib import Path

# Configuration
PARTNER_URL = "https://www.outdoorfun.com.tw/feeds/top_spots.json"
OUTPUT_FILE = Path("src/data/partner_ads.json")

def main():
    print("🔄 開始同步衝浪站 (Partner) 資料...")
    print(f"   來源: {PARTNER_URL}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
        'Referer': 'https://www.google.com/'
    }

    try:
        response = requests.get(PARTNER_URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Transform Logic to match our Ad Schema if necessary, 
        # or just save raw and let Component handle it.
        # Saving raw is more flexible.
        
        # Ensure directory exists
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"✅ 同步成功！已取得 {len(data)} 筆衝浪推薦資料。")
        print(f"   存檔位置: {OUTPUT_FILE}")
        
    except Exception as e:
        print(f"❌ 同步失敗: {str(e)}")
        # If valid previous file exists, don't delete it, just warn.

if __name__ == "__main__":
    main()
