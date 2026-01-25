import json
import os
import requests
from datetime import datetime
from pathlib import Path

# Configuration
PARTNER_FEEDS = {
    "icamping": "src/data/icamping_raw.json", # Internal Source (Reference)
    # Add new partners here, e.g.:
    # "klook": "https://papi.klook.com/v2/products?query=camping",
    # "kkday": "..."
}

OUTPUT_FILE = Path("src/data/campgrounds_synced_raw.json")

def normalize_partner_data(source_name, raw_data):
    """
    Convert partner specific format to our unified Camp schema
    """
    normalized = []
    
    if source_name == "icamping":
        # Usually this is our base, so we might just pass through or skip
        # Logic is already in scrape_icamping.py, so maybe this script is for *merging* external feeds
        pass
        
    # Example placeholder for Klook
    # if source_name == "klook":
    #     for item in raw_data['products']:
    #         normalized.append({
    #             "source": "klook",
    #             "external_id": item['id'],
    #             "name": item['title'],
    #             "url": item['deep_link'],
    #             ...
    #         })
            
    return normalized

def main():
    print("🔄 Starting Multi-source Partner Sync...")
    
    all_camps = []
    
    # 1. Load Local Base (iCamping)
    if os.path.exists(PARTNER_FEEDS["icamping"]):
        with open(PARTNER_FEEDS["icamping"], "r", encoding="utf-8") as f:
            base_data = json.load(f)
            # Ensure it's list
            if isinstance(base_data, dict) and 'items' in base_data:
                base_data = base_data['items']
            print(f"✅ Loaded Base Data (iCamping): {len(base_data)} items")
            all_camps.extend(base_data)
            
    # 2. Sync External Partners (Placeholder)
    # for name, url in PARTNER_FEEDS.items():
    #     if name == "icamping": continue
    #     try:
    #         resp = requests.get(url)
    #         data = resp.json()
    #         norm = normalize_partner_data(name, data)
    #         print(f"✅ Synced {name}: {len(norm)} items")
    #         all_camps.extend(norm)
    #     except Exception as e:
    #         print(f"❌ Failed to sync {name}: {e}")

    # 3. Conflict Resolution & Merging
    # (Simple logic: If same name/phone, merge or prefer internal?)
    # For now, we just pass through.
    
    print(f"💾 Saving unified feed... Total: {len(all_camps)}")
    # In a real scenario, we would save to a new raw file that update_pipeline.py reads
    # For now, this is a template script.
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
         json.dump(all_camps, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
