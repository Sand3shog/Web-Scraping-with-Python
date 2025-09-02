import os
import sys
import json
import base64
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials

URL = "http://quotes.toscrape.com"
script_dir = Path(__file__).parent if "__file__" in globals() else Path.cwd()  
OUTPUT_DIR = (script_dir.parent / "data").resolve()    #data directory outside app folder so
OUTPUT_DIR.mkdir(parents=True, exist_ok=True) 
CSV_PATH = OUTPUT_DIR / "quotes.csv"

REQUEST_TIMEOUT = 10
USER_AGENT = "quotes-scraper/1.0"

def get_gspread_client_from_env():
    path_env = os.environ.get("GOOGLE_CREDS_JSON_PATH") or os.environ.get("GOOGLE_CREDS_JSON")
    if path_env:
        if not Path(path_env).exists():
            raise FileNotFoundError(f"Credentials file not found: {path_env}")
        return gspread.service_account(filename=path_env)

    content = os.environ.get("GOOGLE_CREDS_JSON_CONTENT")
    if content:
        creds_dict = json.loads(content)
        try:
            return gspread.service_account_from_dict(creds_dict)
        except AttributeError:
            scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            return gspread.authorize(creds)

    b64 = os.environ.get("GOOGLE_CREDS_JSON_B64")
    if b64:
        decoded = base64.b64decode(b64)
        creds_dict = json.loads(decoded)
        try:
            return gspread.service_account_from_dict(creds_dict)
        except AttributeError:
            scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            return gspread.authorize(creds)

    raise ValueError("No Google credentials found in environment (set GOOGLE_CREDS_JSON_PATH / _CONTENT / _B64)")

def fetch_page(url: str) -> str:
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.text

def parse_quotes_from_html(html: str):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    quote_containers = soup.find_all("div", class_="quote")
    results = []
    for q in quote_containers:
        text_tag = q.find("span", class_="text")
        author_tag = q.find("small", class_="author")
        tags_container = q.find("div", class_="tags")
        text = text_tag.text.strip() if text_tag else ""
        author = author_tag.text.strip() if author_tag else ""
        tags_list = [t.text.strip() for t in tags_container.find_all("a", class_="tag")] if tags_container else []
        results.append({"quote": text, "author": author, "tags": ", ".join(tags_list)})
    return results

def upload_df_to_sheet(df: pd.DataFrame):
    spreadsheet_id = os.environ.get("SPREADSHEET_ID")
    if not spreadsheet_id:
        raise ValueError("Set SPREADSHEET_ID environment variable")
    worksheet_name = os.environ.get("WORKSHEET_NAME", "quotes")
    gc = get_gspread_client_from_env()
    sh = gc.open_by_key(spreadsheet_id)
    try:
        ws = sh.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=worksheet_name, rows=str(max(100, len(df) + 10)), cols=str(len(df.columns) + 5))
    ws.clear()
    set_with_dataframe(ws, df, include_index=False, include_column_header=True)
    print(f"Uploaded {len(df)} rows to spreadsheet '{sh.title}' worksheet '{ws.title}'")

def main():
    print(f"Fetching quotes from {URL}...")
    try:
        html = fetch_page(URL)
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        sys.exit(1)

    quotes = parse_quotes_from_html(html)
    if not quotes:
        print("No quotes found.")
        sys.exit(1)

    df = pd.DataFrame(quotes)
    df.to_csv(CSV_PATH, index=False)
    print(f"✨ Saved {len(df)} quotes to '{CSV_PATH}'")
    print("\n--- First 5 Scraped Quotes ---")
    print(df.head())

    try:
        upload_df_to_sheet(df)
    except Exception as e:
        print(f"❌ Failed to upload to Google Sheets: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
