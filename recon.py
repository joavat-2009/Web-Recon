import asyncio
from rich.console import Console
from rich.progress import Progress
from rich.panel import Panel
from datetime import datetime
from urllib.parse import urlparse
from whois import whois
import requests
import time
import os.path
import aiosqlite
import aiohttp
import logging
import argparse
import sys


# region ASCII & INFO BANNER
BANNER_ART = r"""
    __    __  __       [bold bright_blue]Web-Recon Utility[/bold bright_blue]                             │ [bold cyan]Author:[/bold cyan] joavat-2009 (Joseph Avatiants)
   / /_  / /_/ /_____  --------------------------------------------- │ [bold cyan]Status:[/bold cyan] {version_placeholder}
  / __ \/ __/ __/ __ \ A high-performance multithreaded OSINT tool   │ 
 / / / / /_/ /_/ /_/ / designed for infrastructure security auditing │ [bold space]      [/bold space]
/_/ /_/\__/\__/ .___/  network latency performance tracking,         │ 
             /_/       and deep unstructured WHOIS data gathering.   │ 
"""
# endregion

console = Console()

logging.getLogger("whois.whois").setLevel(logging.CRITICAL)


CURRENT_VERSION = "0.5.0"

current_date = datetime.today()

day = current_date.day
month = current_date.month
year = current_date.year

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

async def init_db(db_name):
    async with aiosqlite.connect(f"{db_name}.db") as conn:
        await conn.execute(f"CREATE TABLE IF NOT EXISTS [{db_name}] (date TEXT, url TEXT, status TEXT, whois_info TEXT, latency TEXT)")

async def insert_error(db_name, date, url, status, whois_raw, latency):
    async with aiosqlite.connect(f"{db_name}.db") as conn:
        await conn.execute(f"INSERT INTO [{db_name}] VALUES (?, ?, ?, ?, ?)", (date, url, status, whois_raw, latency))
        await conn.commit()

async def check_single_link_async(session, url, sem, delay):

    error_msg = None
    latency = "No Response"
    status = None

    if url.startswith('http://') or url.startswith('https://'):
        try:
            async with sem:
                if delay > 0:
                    await asyncio.sleep(delay)

                start_time = time.perf_counter()
                async with session.get(url, timeout=30, headers=headers) as r:
                    end_time = time.perf_counter()
                    latency = (end_time - start_time) * 1000

                    if r.status == 200:
                        status = "Working"
                    else:
                        error_msg = f"Error code {r.status}: {r.reason}"

        except:
            error_msg = "Connection error. Site is completely down or domain is invalid."

    else:
        console.print("[bold red]! Your link should starting with http:// or https:// [/bold red]")

    if error_msg is not None:
        whois_data = await asyncio.to_thread(check_your_domain_info, url)
        return {"url": url, "status": error_msg, "passport": whois_data, "latency": latency}

    elif status == "Working":
        return {"url": url, "status": status, "passport": "Not checked for working sites", "latency": latency}
    else:
        return None

async def process_single_async(url, database_name):
    sem = asyncio.Semaphore(1)
    async with aiohttp.ClientSession() as session:
        result = await check_single_link_async(session, url, sem, 0)

        if result is not None:
            await insert_error(database_name, f"{day}.{month}.{year}", result["url"], result["status"], str(result["passport"]), result["latency"])
            console.print("[bold red]!Error saved to database. [/bold red]")

def check_for_updates():
    try:
        git_update = "https://api.github.com/repos/joavat-2009/Web-Recon/releases/latest"
        vers = requests.get(git_update, timeout=2, headers=headers)

        if vers.status_code == 200:
            vers = vers.json()
            latest_tag = vers["tag_name"]
            latest_version = latest_tag.replace('v', '')
            if latest_version != CURRENT_VERSION:
                latest_version = f"v{CURRENT_VERSION} [bold red](New version available! v{latest_version})[/bold red])"
                return latest_version
            else:
                return f"v{CURRENT_VERSION}"

        return f"v{CURRENT_VERSION}"

    except:
        return f"v{CURRENT_VERSION}"

async def process_file_async(file_path, database_name, concurrency_limit, delay_time): # <- Принимаем delay_time
    sem = asyncio.Semaphore(concurrency_limit)

    with open(file_path, 'r', encoding='utf-8') as infile:
        urls_list = [line.strip() for line in infile if line.strip()]

        with Progress() as progress:
            task_id = progress.add_task("[cyan]Scanning targets...", total=len(urls_list))

            async with aiohttp.ClientSession() as session:
                futures = [asyncio.create_task(check_single_link_async(session, url, sem, delay_time)) for url in urls_list]

                for future in asyncio.as_completed(futures):
                    result = await future

                    if result is not None:
                        await insert_error(database_name, f"{day}.{month}.{year}", result["url"], result["status"], str(result["passport"]), result["latency"])

                    progress.update(task_id, advance=1)


def check_your_domain_info(url):
    try:
        if url.startswith('http://') or url.startswith('https://'):
            parsed_url = urlparse(url)
            clean_domain = parsed_url.netloc
        else:
            clean_domain = url

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

        formatted_whois = []
        for key, value in whois_info.items():
            formatted_whois.append(f"{key.replace('_', '').capitalize()}: {value}")

        final_whois = "\n\n".join(formatted_whois)
        return final_whois

    except:
        whois_info = "Could not find WHOIS data for this domain."
        return whois_info


def arguments():
    parser = argparse.ArgumentParser(description="Web-Recon OSINT & Scan Tool")

    parser.add_argument("-t", "--target", type=str, help="Target single URL (e.g. https://google.com)")
    parser.add_argument("-f", "--file", type=str, help="Path to .txt file with targets list")
    parser.add_argument("-o", "--output", type=str, help="Custom report database file name", default="RReport")
    parser.add_argument("-q", "--quiet", action="store_true", help="Activate headless mode (suppress TUI, banners, and progress bars)")
    parser.add_argument("-d", "--delay", type=float, help="Delay in seconds between checks (default: 0.5)", default=0.5)
    parser.add_argument("-c", "--concurrency", type=int, help="Max simultaneous requests (default: 50)", default=50)

    args = parser.parse_args()

    if not args.quiet:
        version = check_for_updates()
        console.clear()
        console.print(Panel(BANNER_ART.format(version_placeholder=version), title="Web-Recon", border_style="bright_blue"))

    f_db_name = args.output

    asyncio.run(init_db(f_db_name))

    if args.file:
        if os.path.exists(args.file):
            if not args.quiet:
                console.print(
                    f"[bold green]► Detected a file! Launching async scanner for: {args.file}...[/bold green]")

            asyncio.run(process_file_async(args.file, f_db_name, args.concurrency, args.delay))

        else:
            console.print(
                f"[bold red]✖ Error: file or path '{args.file}' does not exist. Please check the path.[/bold red]")

    elif args.target:
        if not args.quiet:
            with console.status(f"[bold green]Launching single target async check for {args.target}...[/bold green]",
                                spinner="line"):
                asyncio.run(process_single_async(args.target, f_db_name))
        else:
            asyncio.run(process_single_async(args.target, f_db_name))

    else:
        console.print("[bold red]✖ Error: You must specify either a target URL (-t) or a file path (-f).[/bold red]")
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    arguments()




