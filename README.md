# Web Recon & Domain Intelligence Tool

[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff&style=for-the-badge)](#) [![SQLite](https://img.shields.io/badge/SQLite-%2307405e.svg?logo=sqlite&logoColor=white&style=for-the-badge)][![Linux](https://img.shields.io/badge/Linux-FCC624?logo=linux&logoColor=black&style=for-the-badge)](#)(#)[![GPLv3](https://img.shields.io/badge/GPLv3-FFFFFF?style=for-the-badge)](#)


A lightweight, fault-tolerant Python script designed for fast website connectivity checks, multi-threaded mass scanning, and automated domain security intelligence gathering.

##  Features
- **Smart Link Validation**: Checks HTTP status codes using professional User-Agent headers to prevent fake 403 Forbidden blocks.
- **High-Speed Multi-Threading**: Features an automated concurrent scanner using `ThreadPoolExecutor` to process entire `.txt` lists of targets simultaneously.
- **Robust Error Handling**: Safely catches connection timeouts, dead domains, input typos, and missing pages without breaking execution.
- **Domain Intelligence (OSINT)**: Automatically extracts registrar details, creation/expiration dates, name servers, and EPP status codes via WHOIS.
- **Persistent SQLite Storage**: Automatically initializes and logs all scan results and network errors into a local structured database (`reconReport.db`).

##  Tech Stack & Requirements
The script uses pure Python 3 modules along with the standard web automation toolkit:
- **`requests`** — for making reliable network connections.
- **`python-whois`** — for fetching official domain registry records.
- **`sqlite3`** — for local relational data logging and history retention.
- **`concurrent.futures`** — for orchestrating asynchronous thread pools.
- **`urllib.parse`** — for extracting clean domain names from raw URLs.

##  Installation
To run this tool locally on your machine, clone this repository and install the dependencies:

```bash
# Clone the repository
git clone https://github.com
cd Web-Recon

# Install required external libraries
pip install requests python-whois
```

##  How to Use
Simply execute the Python script in your terminal:
```bash
python recon.py
```
### Modes of Operation:
1. **Single URL Mode**: Paste a regular link (e.g., `https://google.com`). The script evaluates connectivity, performs a WHOIS lookup, and saves the error to the database.
2. **Mass Scan Mode**: Input a path to a text file containing multiple targets (e.g., `targets.txt`). The script auto-branches into high-speed parallel scanning and logs logs sequentially into the SQLite backend.

##  Changelog

### [v0.2.1]
- Implemented multi-threaded scanning architecture.
- Added automated file stream parsing for `.txt` target lists.
- Added **SQLite3 database** integration (`reconReport.db`).
- Implemented structured tables initialization upon startup.
- Fixed race conditions and file write blocks during multi-threaded DB commits.

### [v0.1.0]
- Initial release. Basic HTTP validation and local JSON reporting.

##  Author
- **Joseph Avatyants**
- GitHub: [@joavat-2009](https://github.com)
- Email: joavat2009@gmail.com
