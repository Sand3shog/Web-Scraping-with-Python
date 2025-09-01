import requests

URL = "https://inshorts.com/en/read"  # keep the url of the site to test network connection

print("--- Starting Network Connection Test ---")
print(f"Attempting to connect to: {URL}")

try:

    response = requests.get(URL)

    print("Connection Successful!")
        
    # A status code of 200 means "OK".
    print(f"   - Server responded with status code: {response.status_code}")
    print(f"   - Received {len(response.text)} characters of HTML.")

    if response.status_code == 200 and len(response.text) > 0:
        print("\nDiagnosis: Your connection is working! The main scraper should work.")
    else:
        print("\nDiagnosis: Connected, but got an empty or error response from the server.")

except requests.exceptions.Timeout:
    print("\n❌ Connection Timed Out.")
    print("   This means the website is likely blocked by your network or ISP, or the connection is too slow.")

except requests.exceptions.RequestException as e:
    print("\n❌ A critical connection error occurred.")
    print(f"   Error details: {e}")
    print("   This often points to a firewall, DNS, or ISP blocking issue.")

print("\n--- Test Complete ---")