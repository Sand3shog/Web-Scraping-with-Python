import os
import time
import pandas as pd
from bs4 import BeautifulSoup

# --- Selenium Imports ---
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# --- Global Constants ---
OUTPUT_DIR = "data"
DOMAIN_URL = "https://ekantipur.com"
BASE_URL = f"{DOMAIN_URL}/entertainment"


def get_main_page_html_with_selenium() -> str | None:
    """
    Uses Selenium to open the main entertainment page, wait for JavaScript
    to load the articles, and then returns the fully rendered HTML.
    """
    print("Setting up Selenium WebDriver...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")

    service = Service()
    driver = None

    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print(f"Fetching dynamically loaded content from {BASE_URL}...")
        driver.get(BASE_URL)

        print("Waiting for articles to load via JavaScript...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".teaser.offset"))
        )
        print("✅ Articles have loaded.")
        
        # for rendering
        time.sleep(2)

        return driver.page_source

    except Exception as e:
        print(f"❌ An error occurred with Selenium: {e}")
        return None
    finally:
        if driver:
            driver.quit()


def main():
    """
    Main function to run the simplified scraper.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    html_content = get_main_page_html_with_selenium()

    if not html_content:
        print("Failed to retrieve page content. Exiting.")
        return

    soup = BeautifulSoup(html_content, "html.parser")
    article_cards = soup.find_all("div", class_="teaser offset")
    
    if not article_cards:
        print("Could not find any article cards with class 'teaser offset'. The website layout may have changed again.")
        return
    
    print(f"✅ Found {len(article_cards)} articles. Extracting details...")

    # Extraction
    all_articles_data = []
    for card in article_cards:
        # Safely find the headline, description, and author
        headline_tag = card.find("h2")
        headline = headline_tag.text.strip() if headline_tag else "No headline"

        description_tag = card.find("p")
        description = description_tag.text.strip() if description_tag else "No description"
        author_tag = card.find("div", class_="author")
        author = author_tag.text.strip() if author_tag else "No author"

        all_articles_data.append({
            "headline": headline,
            "description": description,
            "author": author
        })

    if not all_articles_data:
        print("No articles were successfully parsed.")
        return

    # Save the new, simpler data to CSV and JSON files
    df = pd.DataFrame(all_articles_data)
    
    csv_path = os.path.join(OUTPUT_DIR, "ekantipur_articles.csv")
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    json_path = os.path.join(OUTPUT_DIR, "ekantipur_articles.json")
    df.to_json(json_path, orient="records", indent=2, force_ascii=False)
    
    print(f"\nSuccess! Saved {len(df)} articles to the '{OUTPUT_DIR}' directory.")


if __name__ == "__main__":
    main()