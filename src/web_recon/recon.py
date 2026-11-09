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
import random


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

CURRENT_VERSION = "0.6.2"

current_date = datetime.today()
day = current_date.day
month = current_date.month
year = current_date.year

async def init_db(db_name):
    async with aiosqlite.connect(f"{db_name}.db") as conn:
        await conn.execute(f"CREATE TABLE IF NOT EXISTS [{db_name}] (date TEXT, url TEXT, status TEXT, whois_info TEXT, latency TEXT)")

async def insert_error(db_name, date, url, status, whois_raw, latency):
    async with aiosqlite.connect(f"{db_name}.db") as conn:
        await conn.execute(f"INSERT INTO [{db_name}] VALUES (?, ?, ?, ?, ?)", (date, url, status, whois_raw, latency))
        await conn.commit()

async def check_single_link_async(session, url, sem, delay, current_user_agent):

    error_msg = None
    latency = "No Response"
    status = None

    if url.startswith('http://') or url.startswith('https://'):
        try:
            async with sem:
                if delay > 0:
                    await asyncio.sleep(delay)

                start_time = time.perf_counter()

                local_headers = {'User-Agent': current_user_agent}

                async with session.get(url, timeout=30, headers=local_headers) as r:
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

async def process_single_async(url, database_name, loaded_agents):
    sem = asyncio.Semaphore(1)

    selected_agent = random.choice(loaded_agents)

    async with aiohttp.ClientSession() as session:
        result = await check_single_link_async(session, url, sem, 0, selected_agent)

        if result is not None:
            await insert_error(database_name, f"{day}.{month}.{year}", result["url"], result["status"], str(result["passport"]), result["latency"])
            console.print("[bold red]!Error saved to database. [/bold red]")

def check_for_updates():
    fallback_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) WebReconUpdater'}
    try:
        git_update = "https://github.com"
        vers = requests.get(git_update, timeout=2, headers=fallback_header)

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

async def process_file_async(file_path, database_name, concurrency_limit, delay_time, loaded_agents):
    sem = asyncio.Semaphore(concurrency_limit)

    with open(file_path, 'r', encoding='utf-8') as infile:
        urls_list = [line.strip() for line in infile if line.strip()]

        with Progress() as progress:
            task_id = progress.add_task("[cyan]Scanning targets...", total=len(urls_list))

            async with aiohttp.ClientSession() as session:
                futures = [
                    asyncio.create_task(
                        check_single_link_async(session, url, sem, delay_time, random.choice(loaded_agents))
                    )
                    for url in urls_list
                ]

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
            if isinstance(value, list):
                clean_value = ", ".join(str(item) for item in value)
            else:
                clean_value = value

            formatted_whois.append(f"{key.replace('_', '').capitalize()}: {clean_value}")

        final_whois = "\n\n".join(formatted_whois)
        return final_whois

    except:
        whois_info = "Could not find WHOIS data for this domain."
        return whois_info


def arguments():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) WebReconBot'}

    parser = argparse.ArgumentParser(description="Web-Recon OSINT & Scan Tool")

    parser.add_argument("-t", "--target", type=str, help="Target single URL (e.g. https://google.com)")
    parser.add_argument("-f", "--file", type=str, help="Path to .txt file with targets list")
    parser.add_argument("-o", "--output", type=str, help="Custom report database file name", default="RReport")
    parser.add_argument("-q", "--quiet", action="store_true", help="Activate headless mode (suppress TUI, banners, and progress bars)")
    parser.add_argument("-d", "--delay", type=float, help="Delay in seconds between checks (default: 0.5)", default=0.5)
    parser.add_argument("-c", "--concurrency", type=int, help="Max simultaneous requests (default: 50)", default=50)
    parser.add_argument("-A", "--UserAgents", type=str, help="User-Agent string")

    args = parser.parse_args()

    if not args.quiet:
        version = check_for_updates()
        console.clear()
        console.print(Panel(BANNER_ART.format(version_placeholder=version), title="Web-Recon", border_style="bright_blue"))

    f_db_name = args.output

    asyncio.run(init_db(f_db_name))

    loaded_agents = []

    if args.UserAgents:
        if os.path.exists(args.UserAgents):
            if not args.quiet:
                console.print(f"[bold green]► Loading custom User-Agents from file: {args.UserAgents}[/bold green]")

            with open(args.UserAgents, 'r', encoding='utf-8') as file:
                for line in file:
                    if line.strip():
                        loaded_agents.append(line.strip())
        else:
            console.print(f"[bold red]✖ Error: User-Agents file '{args.UserAgents}' does not exist.[/bold red]")
            sys.exit(1)

    else:
        if not args.quiet:
            console.print("[bold cyan]► Fetching fresh User-Agents from online database...[/bold cyan]")

        raw_site_url = "https://githubusercontent.com"

        try:
            r_response = requests.get(raw_site_url, timeout=4, headers=headers)
            if r_response.status_code == 200:
                for line in r_response.text.splitlines():
                    if line.strip().startswith("Mozilla/5.0"):
                        loaded_agents.append(line.strip())
        except:
            pass

        if not loaded_agents:
            if not args.quiet:
                console.print("[bold yellow]⚠️ Internet offline. Activating built-in hardcoded User-Agent fallback shield.[/bold yellow]")

            loaded_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
                "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
            ]

    if args.file:
        if os.path.exists(args.file):
            if not args.quiet:
                console.print(f"[bold green]► Detected a file! Launching async scanner for: {args.file}...[/bold green]")

            asyncio.run(process_file_async(args.file, f_db_name, args.concurrency, args.delay, loaded_agents))
        else:
            console.print(f"[bold red]✖ Error: file or path '{args.file}' does not exist.[/bold red]")

    elif args.target:
        if not args.quiet:
            with console.status(f"[bold green]Launching single target check for {args.target}...[/bold green]", spinner="line"):
                # И сюда передаем loaded_agents!
                asyncio.run(process_single_async(args.target, f_db_name, loaded_agents))
        else:
            asyncio.run(process_single_async(args.target, f_db_name, loaded_agents))

    else:
        console.print("[bold red]✖ Error: You must specify either a target URL (-t) or a file path (-f).[/bold red]")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    arguments()
