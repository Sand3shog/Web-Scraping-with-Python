import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

URL = "http://quotes.toscrape.com"  # url
OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"Fetching quotes from {URL}...")

try:
    response = requests.get(URL)
    response.raise_for_status()  # Check for any request errors

    soup = BeautifulSoup(response.text, "html.parser")

    # Finding all the containers for each quote.
    quote_containers = soup.find_all("div", class_="quote")

    if not quote_containers:
        print("Could not find any quote containers.")
    else:
        print(f"Found {len(quote_containers)} quotes on the page. Parsing...")
        
        scraped_quotes = []
        # Loop through each container to find the data inside.
        for quote in quote_containers:

            # The text is in a <span> with class "text"
            text = quote.find("span", class_="text").text

            # The author is in a <small> with class "author"
            author = quote.find("small", class_="author").text

            # Tags are inside a <div> with class "tags"
            # find all the <a> tags inside it to get each tag.
            tags_container = quote.find("div", class_="tags")
            tags = [tag.text for tag in tags_container.find_all("a", class_="tag")]
            # Join the list of tags into a single string
            tags_str = ", ".join(tags)

            scraped_quotes.append({
                "quote": text,
                "author": author,
                "tags": tags_str
            })
        df = pd.DataFrame(scraped_quotes)
        
        # Save to CSV
        csv_path = os.path.join(OUTPUT_DIR, "quotes.csv")
        df.to_csv(csv_path, index=False)
        print(f"\n✨ Success! Saved {len(df)} quotes to '{csv_path}'.")

        # Print the first 5 quotes
        print("\n--- First 5 Scraped Quotes ---")
        print(df.head())


except requests.exceptions.RequestException as e:
    print(f"❌ An error occurred: {e}")