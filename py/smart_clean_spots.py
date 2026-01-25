import json
import os
from pathlib import Path
import re

# Config
INPUT_FILE = Path("src/data/campgrounds_enriched.json")
OUTPUT_FILE = Path("src/data/campgrounds_smart_clean.json")

def normalize_text(text):
    if not text: return ""
    # Remove special chars, spaces
    return re.sub(r'[ \(\)（）\-\_]', '', text).lower()

def auto_tag(item):
    desc = (item.get("description") or "") + (item.get("name") or "")
    tags = set(item.get("tags", []))
    
    keywords = {
        "高海拔": ["高海拔", "雲海", "避暑"],
        "親子": ["親子", "沙坑", "溜滑梯", "兒童"],
        "寵物": ["寵物", "毛小孩", "狗狗"],
        "溫泉": ["溫泉", "湯屋"],
        "森林系": ["森林", "樹林", "杉木"],
        "豪華露營": ["豪華", "懶人", "Glamping", "免搭帳"],
        "海景": ["海景", "海邊", "沙灘"]
    }
    
    for tag_name, syns in keywords.items():
        for syn in syns:
            if syn in desc:
                tags.add(tag_name)
                break
                
    item["tags"] = list(tags)
    return item

def main():
    if not INPUT_FILE.exists():
        print("No input file found.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Original Count: {len(data)}")

    # 1. Deduplication
    unique_map = {}
    duplicates = 0
    
    for item in data:
        # Key: Use standardized phone + first 3 chars of name as a simplified key
        # Or simplified name. Phone is often good identifier for businesses.
        phone = normalize_text(item.get("phone", ""))
        name_key = normalize_text(item.get("name", ""))[:4] # First 4 chars
        
        # Strategy: Prefer Phone, fallback to Name/Address
        key = phone if len(phone) > 6 else (name_key + normalize_text(item.get("city", "")))
        
        if key in unique_map:
            duplicates += 1
            # Merge logic: Keep the one with longer description
            existing = unique_map[key]
            if len(item.get("description", "")) > len(existing.get("description", "")):
                unique_map[key] = item
        else:
            unique_map[key] = item

    cleaned_data = list(unique_map.values())
    print(f"Removed {duplicates} duplicates.")

    # 2. AI Tagging (Keyword based)
    final_data = []
    for item in cleaned_data:
        final_data.append(auto_tag(item))

    # Output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)

    print(f"Smart cleaning complete. Output: {len(final_data)} items to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
