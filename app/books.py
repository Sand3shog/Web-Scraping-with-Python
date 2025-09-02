import requests
from bs4 import BeautifulSoup
import pandas as pd
import os 

OUTPUT_DIR = "Data"

os.makedirs(OUTPUT_DIR, exist_ok=True)

base_url = "http://books.toscrape.com"
books = []

print("Starting scraper...")

for page in range(1, 6):  # scrape first 5 pages
    url = f"{base_url}/catalogue/page-{page}.html"
    print(f"Scraping page: {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    for item in soup.find_all("article", class_="product_pod"):
        title = item.h3.a["title"]
        price = item.find("p", class_="price_color").get_text()
        availability = item.find("p", class_="instock availability").get_text(strip=True)
        rating = item.p["class"][1]  
        books.append({
            "Title": title,
            "Price": price,
            "Availability": availability,
            "Rating": rating
        })

df = pd.DataFrame(books)

#Using os.path.join to create the correct file path for CSV
csv_path = os.path.join(OUTPUT_DIR, "books.csv")
df.to_csv(csv_path, index=False)

#Using os.path.join to create the correct file path for JSON
json_path = os.path.join(OUTPUT_DIR, "books.json")
df.to_json(json_path, orient="records", indent=4)

print(f"\nScraping completed. Data saved to '{OUTPUT_DIR}' directory.")