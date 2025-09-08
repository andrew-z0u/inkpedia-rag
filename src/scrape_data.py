from bs4 import BeautifulSoup
import requests
import json
import os

DATA_DIR = "data"
# Simple list, may add more later
category_list = ["Abilities", "Blasters", "Boss_Salmonids", "Brands", "Brellas", "Brushes",
"Chargers", "Dualies", "Modes", "Rollers", "Sloshers", "Shooters", "Splatanas", "Splatlings", "Splatoon_stages",
"Splatoon_2_stages", "Splatoon_3_stages", "Stringers", "Splatoon_sub_weapons", "Splatoon_2_sub_weapons",
"Splatoon_3_sub_weapons", "Splatoon_special_weapons", "Splatoon_2_special_weapons", "Splatoon_3_special_weapons",
"Weapon_strategy"]

def scrape_page(url):
    """
    Scrape a webpage and return a JSON-like dictionary
    with all paragraphs in reading order, ignoring headers and other elements.
    """
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    page_data = {
        "url": url,
        "title": "",
        "paragraphs": []
    }

    # Page title
    h1_tag = soup.find("h1", id="firstHeading")
    page_data["title"] = h1_tag.get_text().strip() if h1_tag else "No title found"

    # Only look at content contained in mw-parser-outpue
    content_div = soup.find("div", class_="mw-parser-output")
    if not content_div:
         return page_data
    
    # Walk through the direct children in order to maintain reading order
    for element in content_div.children:
        if not hasattr(element, "name"):
            continue
         
         # Paragraphs
        if element.name == "p":
            if (element.find_parent(class_=["gallerybox", "gallerytext", "thumb", "infobox",
                                      "infobox", "navbox", "catlinks"])
                or element.find_parent("table")):
                    continue
            text = element.get_text().strip()
            if text:
                page_data["paragraphs"].append(text)

    # Bullet lists
        elif element.name == "ul":
            if (element.find_parent(class_=["gallerybox", "gallerytext", "thumb", "infobox", "navbox", "catlinks"])
                or element.find_parent("table")):
                    continue
            items = []
            for li in element.find_all("li", recursive=False):
                text = li.get_text().strip()
                if text:
                    items.append(f"- {text}")
                if items:
                    page_data["paragraphs"].extend(items)

    return page_data


    # # Extract all paragraphs in reading order
    # for p_tag in soup.find_all("p"):
    #     if (p_tag.find_parent(class_=["gallerybox", "gallerytext", "thumb", "infobox",
    #                                   "infobox", "navbox", "catlinks"])
    #         or p_tag.find_parent("table")):
    #             continue
    #     text = p_tag.get_text().strip()
    #     if text:
    #         page_data["paragraphs"].append(text)

    # # Extract bullet 

    # return page_data
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


def categories_to_json(category_url, base_url, category_name):
    """
    Given a category page URL, scrape all linked pages in that category
    and save them as JSON files.
    """
    response = requests.get(category_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Find links in categories
    content_div = soup.find("div", id="mw-pages")
    if not content_div:
        print("No pages found in this category.")
        return

    links = content_div.find_all("a")
    for link in links:
        href = link.get("href")
        if href and href.startswith("/wiki/") and not href.startswith("/wiki/Category:"):
            page_url = base_url + href
            try:
                page_data = scrape_page(page_url)
                save_json(page_data, category_name=category_name)
            except Exception as e:
                print(f"Error scraping {page_url}: {e}")

for category in category_list:
    url = "https://splatoonwiki.org/wiki/Category:" + category
    categories_to_json(category_url=url, base_url="https://splatoonwiki.org", category_name=category)
