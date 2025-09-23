from bs4 import BeautifulSoup
import requests
import json
import os

def scrape_stronghold_data(url):
    """
    Scrape a Splatoon Stronghold guide and return a JSON-like dictionary
    with all content combined into a single text block.
    """
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    text_fragments = []

    h1_tag = soup.find("h1")
    page_title = ' '.join(h1_tag.stripped_strings) if h1_tag else "No title found"

    content_div = soup.find("article") or soup.find("div", class_="post-content")

    if content_div:
        for elem in content_div.find_all(["h2", "h3", "p"]):
            text = " ".join(elem.stripped_strings)
            if not text:
                continue

            if elem.name == "h2":
                text_fragments.append(f"## {text}")
            elif elem.name == "h3":
                text_fragments.append(f"### {text}")
            else:
                text_fragments.append(text)

    full_content = "\n\n".join(text_fragments)

    page_data = {
        "url": url,
        "title": page_title,
        "content": full_content
    }

    return page_data

def save_json(data, folder="data", category_name="misc"):
    """Save scraped page to JSON, skipping if already exists"""

    category = category_name
    folder_path = os.path.join(folder, category)
    os.makedirs(folder_path, exist_ok=True)
    filename = os.path.join(folder_path, f"{data['title'].replace('/', '_')}.json")

    if os.path.exists(filename):
        print(f"Skipping {data["title"]} (already exists)")
        return
     
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {data["title"]}")

links = ["competitive-splatoon-guidebook-part-1-competitive", "competitive-splatoon-guidebook-part-2-tournaments",
         "competitive-splatoon-guidebook-part-3-contributing", "analyzing-a-weapons-viability",
         "researching-competitive-japanese-content", "playing-smarter-a-guide-to-improving-tactical-thinking-part-1-introduction-and-overview",
         "more-than-just-scrims-four-ways-to-practice-in-splatoon", "series-weapon-power-breakdown",
         "how-long-and-short-range-players-can-harmonize-in-game", "how-to-create-a-competitive-splatoon-team-from-the-ground-up",
         "splatoon-3-more-ways-to-compete"]

base_url = "https://www.splatoonstronghold.com/guides/"
for ext in links:
    url = base_url + ext
    data = scrape_stronghold_data(url)
    save_json(data, category_name="Stronghold")