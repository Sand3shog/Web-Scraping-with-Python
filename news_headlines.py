# still learning this 
# cannot decompress the response

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

BASE_URL = "https://inshorts.com/en/read"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.5"
}

def scrape_inshorts_page():
    """
    Scrapes the initial Inshorts page for all visible news articles.
    """
    print(f"Fetching news from {BASE_URL}...")
    
    try:
        # The requests library will automatically decompress the response
        # when it sees the 'Content-Encoding' header from the server.
        response = requests.get(BASE_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
        
        # We now have the clean, decompressed HTML text
        html_content = response.text
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching the webpage: {e}")
        return

    soup = BeautifulSoup(html_content, "html.parser")
    
    # Using the class for the main card container we found in the readable HTML.
    # If this fails again, it means the class name has changed.
    news_cards = soup.find_all("div", class_="TfxplVx3RtbilOD2tqd6")
    
    if not news_cards:
        print(" Could not find any news cards. The website's main class name has likely changed.")
        # Save the (now readable) HTML for debugging, just in case.
        with open("readable_debug_output.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("   The HTML received by the script has been saved to 'readable_debug_output.html' for inspection.")
        return

    print(f"✅ Found {len(news_cards)} news articles. Parsing now...")
    
    all_headlines = []
    for card in news_cards:
        try:
            headline = card.find("span", itemprop="headline").text.strip()
            body = card.find("div", itemprop="articleBody").text.strip()
            author = card.find("span", class_="author").text.strip()
            date = card.find("span", class_="date").text.strip()
            source_url_tag = card.find("a", class_="afA2Wlcd6bZojCgstcCi")
            source_url = source_url_tag['href'] if source_url_tag else "N/A"
            
            all_headlines.append({
                "headline": headline,
                "summary": body,
                "author": author,
                "date": date,
                "source_url": source_url
            })
        except AttributeError:
            # This handles cases where a card might be structured differently (e.g., an ad)
            print("--> Skipping a card with unexpected structure.")
            continue

    if not all_headlines:
        print("No headlines were successfully parsed.")
        return

    df = pd.DataFrame(all_headlines)
    
    csv_path = os.path.join(OUTPUT_DIR, "news_headlines.csv")
    df.to_csv(csv_path, index=False)
    
    json_path = os.path.join(OUTPUT_DIR, "news_headlines.json")
    df.to_json(json_path, orient="records", indent=2)
    
    print(f"Success! Saved {len(df)} headlines to the '{OUTPUT_DIR}' directory.")


if __name__ == "__main__":
    scrape_inshorts_page()