# Web Recon & Domain Intelligence Tool (v0.1)

![Python](https://shields.io) ![Linux](https://shields.io) ![License](https://shields.io) ![Output](https://shields.io) [![GPLv3](https://img.shields.io/badge/GPLv3-FFFFFF)](#)


A lightweight, fault-tolerant Python script designed for fast website connectivity checks and automated domain security intelligence gathering.


## Features
- **Smart Link Validation**: Checks HTTP status codes using professional User-Agent headers to prevent fake 403 Forbidden blocks.
- **Robust Error Handling**: Safely catches connection timeouts, dead domains, input typos, and missing pages without breaking execution.
- **Domain Intelligence (OSINT)**: Automatically extracts registrar details, creation/expiration dates, name servers, and EPP status codes via WHOIS.
- **Structured JSON Reports**: Saves data about caught errors and WHOIS intelligence into cleanly formatted `report.json` logs.

## Tech Stack & Requirements
The script uses pure Python 3 modules along with the standard web automation toolkit:
- **`requests`** — for making reliable network connections.
- **`python-whois`** — for fetching official domain registry records.
- **`urllib.parse`** — for extracting clean domain names from raw URLs.
- **`json`** — for generating report outputs.

## Installation
To run this tool locally on your machine, clone this repository and install the dependencies:

```bash
# Clone the repository
git https://joavat-2009/Web-Recon.git
cd Web-Recon

# Install required external libraries
pip install requests python-whois
```

## How to Use
Simply execute the Python script in your terminal:
```bash
python recon.py
```
1. Paste the target URL (e.g., `https://google.com`).
2. If the link is working correctly, the script proceeds as normal.
3. If an error is detected, it generates a comprehensive `report.json` with the exact HTTP status and WHOIS passport data in your directory.

## Author

- Joseph Avatyants

- GitHub: joavat-2009

- Email: joavat2009@gmail.com
