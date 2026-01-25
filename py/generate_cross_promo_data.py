import json
import os
from pathlib import Path
import random

# Configuration
INPUT_FILE = Path("src/data/campgrounds_smart_clean.json")
OUTPUT_DIR = Path("public/feeds")
OUTPUT_FILE = OUTPUT_DIR / "cross_promo_camps.json"
BASE_URL = "https://www.outdoorcampingworld.com"

def calculate_score(item):
    score = 10
    
    # Simple scoring logic
    elevation = item.get("elevation", 0)
    try:
        elevation = float(elevation)
    except:
        elevation = 0
        
    if elevation > 800: score += 20
    
    features = item.get("features", {})
    if features.get("has_glamping"): score += 15
    if features.get("pet_friendly"): score += 5
    
    if len(item.get("description", "")) > 50: score += 10
    
    return score

def main():
    if not INPUT_FILE.exists():
        print(f"Error: {INPUT_FILE} not found.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Loaded {len(data)} camps.")

    processed = []
    for item in data:
        score = calculate_score(item)
        if score < 30: continue # Filter low quality

        # Construct Image URL (Placeholder logic or first image if available)
        # Assuming no image array in basic data, using generic or specific
        image_url = f"{BASE_URL}/images/placeholders/camp_{random.randint(1,5)}.webp" 
        # In a real scenario, we would check item.get('images')
        
        camp_slug = item.get("name") # Ideally sanitized
        
        processed.append({
            "id": f"cw-{abs(hash(item['name']))}",
            "title": item["name"],
            "description": item.get("description", "")[:80] + "...", # Truncate
            "image": image_url,
            "url": f"{BASE_URL}/camp/{camp_slug}/",
            "tags": item.get("tags", [])[:3],
            "score": score
        })

    # Sort by score desc
    processed.sort(key=lambda x: x["score"], reverse=True)
    
    # Take top 12
    top_picks = processed[:12]

    # Clean Output for Cross-Promo
    output_data = {
        "source": "Outdoor Camping World",
        "generated_at": str(os.times().elapsed),
        "items": top_picks
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"Success: Exported {len(top_picks)} promo items to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
