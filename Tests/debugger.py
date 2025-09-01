import requests

URL = "http://quotes.toscrape.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Referer": "https://www.google.com/"
}

print(f"Running diagnostic script to fetch HTML from {URL}...")

try:
    response = requests.get(URL, headers=HEADERS)
    response.raise_for_status()

    
    with open("debug_output.html", "w", encoding="utf-8") as f:
        f.write(response.text)
        
    print("SUCCESS!")
    print("The raw HTML that your script sees has been saved to the file 'debug_output.html'.")
    print("\nPlease proceed to Step 2.")

except requests.exceptions.RequestException as e:
    print(f" FAILED to fetch the webpage.")
    print(f"   Error: {e}")