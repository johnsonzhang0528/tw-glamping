import json
import os
from pathlib import Path

# Configuration
INPUT_FILE = Path("src/data/campgrounds_enriched.json")
OUTPUT_DIR = Path("public/feeds")
OUTPUT_FILE = OUTPUT_DIR / "top_camps.json"
BASE_URL = "https://www.outdoorcampingworld.com"  # Updated to match the actual project domain

def calculate_score(item):
    score = 10  # Base score

    # Altitude Weight
    elevation = item.get("elevation", 0)
    # Ensure elevation is a number
    try:
        elevation = float(elevation)
    except (ValueError, TypeError):
        elevation = 0
        
    if elevation > 1000:
        score += 30
    elif elevation > 500:
        score += 10
    
    # Feature Weight
    features = item.get("features", {})
    if features.get("has_glamping"):
        score += 20
    if features.get("pet_friendly"):
        score += 5
    if features.get("high_altitude"): # Also checking the flag if present
         score += 5   
        
    # Content Completeness Weight
    description = item.get("description", "")
    if description and len(description) > 50:
        score += 5
    
    tags = item.get("tags", [])
    if len(tags) > 5:
        score += 5
        
    return score

def main():
    # Ensure input exists
    if not INPUT_FILE.exists():
        print(f"Error: Input file {INPUT_FILE} not found.")
        return

    # Read data
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    grouped_data = {}
    
    # Process each item
    for item in data:
        city = item.get("city", "其他")
        if not city:
            city = "其他"
            
        score = calculate_score(item)
        
        # Prepare output item
        desc = item.get("description", "")
        # Remove newlines and truncate to 60 chars
        clean_desc = desc.replace("\n", " ").strip()
        if len(clean_desc) > 60:
            clean_desc = clean_desc[:57] + "..."
            
        # Image handling
        image = item.get("image")
        if not image:
             image = "/images/camps/default.webp"

        output_item = {
            "name": item.get("name"),
            "desc": clean_desc,
            "link": f"{BASE_URL}/camp/{item.get('name')}",
            "image": image,
            "tags": item.get("tags", [])[:3],
            "score": score
        }
        
        if city not in grouped_data:
            grouped_data[city] = []
        
        grouped_data[city].append(output_item)

    # Sort and keep top 3 per city
    final_output = {}
    for city, items in grouped_data.items():
        # Sort by score descending
        sorted_items = sorted(items, key=lambda x: x["score"], reverse=True)
        final_output[city] = sorted_items[:3]

    # Ensure output directory exists
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Error creating output directory: {e}")
        return

    # Write output
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(final_output, f, ensure_ascii=False, indent=2)
        print(f"Successfully generated feed for {len(final_output)} cities.")
        print(f"Output saved to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error writing output file: {e}")

if __name__ == "__main__":
    main()
