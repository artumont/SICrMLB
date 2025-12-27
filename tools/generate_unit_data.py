import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import yaml
import concurrent.futures
import sys
import time

# --- Configuration ---
BASE_URL = "https://www.deckshop.pro"
LIST_URL = "https://www.deckshop.pro/card/list"
OUTPUT_FILE = "unit_data.yaml"
MAX_WORKERS = 6  # Reduced to prevent server blocking

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

# --- Setup Robust Session with Retries ---
session = requests.Session()
session.headers.update(HEADERS)

# Retry 3 times on bad status codes (500, 502, 503, 504) or connection errors
retry_strategy = Retry(
    total=5,
    backoff_factor=2,  # Wait 1s, 2s, 4s...
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)


def clean_text(text):
    translation = str.maketrans(" -", "__")
    if text:
        return " ".join(text.split()).lower().translate(translation)
    return None


def get_card_list():
    """Scrapes the main list page to get card URLs."""
    print(f"Fetching list from {LIST_URL}...")
    try:
        response = session.get(LIST_URL)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching list: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    by_type_container = soup.find(id="byType")
    cards_to_process = []

    if by_type_container:
        sections = by_type_container.find_all("section")
        for section in sections:
            category_header = section.find("h3")
            category_name = (
                clean_text(category_header.text) if category_header else "unknown"
            )

            links = section.find_all("a", href=True)
            for link in links:
                href = link["href"]
                if "/card/detail/" in href:
                    full_url = BASE_URL + href  # type: ignore
                    cards_to_process.append(
                        {"url": full_url, "category": category_name}
                    )

    unique_cards = {c["url"]: c for c in cards_to_process}.values()
    return list(unique_cards)


def parse_card_detail(card_info):
    """Worker function to scrape details."""
    url = card_info["url"]
    category = card_info["category"]

    try:
        response = session.get(url, timeout=15)  # Increased timeout
        if response.status_code != 200:
            print(f"\n[!] Failed {url} - Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"\n[!] Exception for {url}: {e}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    # 1. Name
    h1 = soup.find("h1")
    card_name = clean_text(h1.text) if h1 else "unknown"

    # 2. Image ID
    identifier = "unknown"
    # Try multiple selectors for safety
    main_img = soup.select_one("div.flex.items-center img.card")
    if not main_img:
        # Fallback: look for any image with class 'card' inside main container
        main_img = soup.select_one("main img.card")

    if main_img and main_img.get("src"):
        src = main_img["src"]
        filename = src.split("/")[-1]  # type: ignore
        identifier = clean_text(filename.split(".")[0])

    # 3. Arena
    arena = "unknown"
    arena_link = soup.find("a", href=lambda x: x and "by-arena" in x)  # type: ignore
    if arena_link:
        arena = int(clean_text(arena_link.text).split("_")[-1].removeprefix("a"))  # type: ignore

    # 4. Base Stats
    base_stats = {}
    tables = soup.find_all("table")
    summary_table = None

    # Find summary table (usually the one WITHOUT 'table-inverse')
    for t in tables:
        if "table-inverse" not in t.get("class", []):  # type: ignore
            summary_table = t
            break

    if summary_table:
        for row in summary_table.find_all("tr"):
            th = row.find("th")
            td = row.find("td")
            if th and td:
                key = clean_text(th.text)
                val = clean_text(td.text)
                try:
                    if "." in val:  # type: ignore
                        val = float(val)  # type: ignore
                    else:
                        clean_val = val.replace("x", "").replace(",", "").strip()  # type: ignore
                        val = int(clean_val)
                except ValueError:
                    pass
                base_stats[key] = val

    # 5. Meta Data
    flag_links = soup.select('a[href*="/card/flag/"]')
    roles = [clean_text(a.text) for a in flag_links]  # type: ignore

    prop_links = soup.select('a[href*="/card/property/"]')
    properties = [clean_text(a.text) for a in prop_links]  # type: ignore

    return {
        "key_name": identifier,
        "data": {
            "name": card_name,
            "type": category,
            "arena": arena,
            "level_multiplier": 1.1,
            "base_stats": base_stats,
            "meta_data": {"roles": roles, "properties": properties},
            "url": url,
        },
    }


if __name__ == "__main__":
    cards = get_card_list()
    total_cards = len(cards)
    print(f"Found {total_cards} unique cards. Starting processing...")

    all_units = {}
    completed = 0
    failures = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_card = {
            executor.submit(parse_card_detail, card): card for card in cards
        }

        for future in concurrent.futures.as_completed(future_to_card):
            try:
                result = future.result()
                completed += 1
                if result:
                    all_units[result["key_name"]] = result["data"]
                else:
                    failures += 1
            except Exception as e:
                failures += 1
                print(f"\n[!] Unexpected worker error: {e}")

            # Progress bar
            sys.stdout.write(
                f"\rProgress: {completed}/{total_cards} (Success: {completed-failures} | Fail: {failures})"
            )
            sys.stdout.flush()

    print("\nSaving to YAML...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        yaml.dump(all_units, file, sort_keys=False, allow_unicode=True)

    print(f"Done! Saved {len(all_units)} cards to {OUTPUT_FILE}")
