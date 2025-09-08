import os
import json

data_folder = "data"
# Category list for now
category_list = ["Abilities", "Blasters", "Boss_Salmonids", "Brands", "Brellas", "Brushes",
"Chargers", "Dualies", "Modes", "Rollers", "Sloshers", "Shooters", "Splatanas", "Splatlings", "Splatoon_stages",
"Splatoon_2_stages", "Splatoon_3_stages", "Stringers", "Splatoon_sub_weapons", "Splatoon_2_sub_weapons",
"Splatoon_3_sub_weapons", "Splatoon_special_weapons", "Splatoon_2_special_weapons", "Splatoon_3_special_weapons",
"Weapon_strategy"]

def cleanup(folder, category):
    """
    Removes duplicates that may occur when scraping Inkpedia bullet lists
    """
    folder_path = folder + '/' + category
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # remove duplicates while preserving order
            prev_amount = len(data["paragraphs"])
            seen = set()
            unique_paragraphs = []
            for paragraph in data.get("paragraphs", []):
                if paragraph not in seen:
                    unique_paragraphs.append(paragraph)
                    seen.add(paragraph)

            data["paragraphs"] = unique_paragraphs

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"Processed {filename}, removed {prev_amount - len(unique_paragraphs)} duplicates")

for category in category_list:
    cleanup(data_folder, category)