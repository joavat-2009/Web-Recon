import requests
import sys
from datetime import datetime
from whois import whois
from urllib.parse import urlparse
import json

current_date = datetime.today()

day = current_date.day
month = current_date.month
year = current_date.year

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}


link = input("Please, paste link of your site here: ")

def check_your_domain_info(link):
    try:
        if link[:7] == 'http://' or link[:8] == 'https://':
            parsed_url = urlparse(link)
            clean_domain = parsed_url.netloc
        else:
            clean_domain = link

        info = whois(clean_domain)
        whois_info = {
            "domain": info.domain_name,
            "registrar": info.registrar,
            "creation_date": str(info.creation_date),
            "expiration_date": str(info.expiration_date),
            "last_update": str(info.updated_date),
            "servers_names": info.name_servers,
            "status": info.status
        }
        return whois_info

    except:
        whois_info = "Could not find WHOIS data for this domain."
        return whois_info



error_msg = None

if link[:4] == 'http' or link[:5] == 'https':
    try:
        r = requests.get(link, stream=True, timeout=30, headers=headers)

        if r.status_code == 200:
            print("Link is working! Processing...")

        elif r.status_code == 400:
            error_msg = f"Error code {r.status_code}. Bad request!"

        elif r.status_code == 401:
            error_msg = f"Error code {r.status_code}. Unauthorized!"

        elif r.status_code == 403:
            error_msg = f"Error code {r.status_code}. Forbidden!"

        elif r.status_code == 404:
            error_msg = f"Error code {r.status_code}. Not found!"

        elif r.status_code == 405:
            error_msg = f"Error code {r.status_code}. Method not allowed!"

        elif r.status_code == 408:
            error_msg = f"Error code {r.status_code}. Request timed out!"

        elif r.status_code == 429:
            error_msg = f"Error code {r.status_code}. Too many requests!"

        elif r.status_code == 500:
            error_msg = f"Error code {r.status_code}. Internal server error!"

        elif r.status_code == 502:
            error_msg = f"Error code {r.status_code}. Bad gateway!"

        elif r.status_code == 503:
            error_msg = f"Error code {r.status_code}. Service unavailable!"

        elif r.status_code == 504:
            error_msg = f"Error code {r.status_code}. Gateway timeout!"

        else:
            print("Invalid link or site is down, error code. Errors saved in report.")
            error_msg = f"Unknown error code: {r.status_code}"
    except:
        error_msg = "Connection error. Site is completely down or domain is invalid."

else:
    print("Your link should starting with http:// or https://")

if error_msg is not None:
    domain_data = check_your_domain_info(link)
    final_report = {
        "date": f"{day}.{month}.{year}",
        "url": link,
        "status": error_msg,
        "whois_details": domain_data
    }
    with open("report.json", "w", encoding="utf-8") as file:
        json.dump(final_report, file, indent=4, ensure_ascii=False)

    print("Error caught! Details saved to 'report.json'.")
    sys.exit()



