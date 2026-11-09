# Web Recon & Domain Intelligence Tool

<p align="left">
  <img src="assets/logo.png" width="250" alt="Web-Recon Logo">
</p>

[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff&style=for-the-badge)](#) [![SQLite](https://img.shields.io/badge/SQLite-%2307405e.svg?logo=sqlite&logoColor=white&style=for-the-badge)](#) [![Linux](https://img.shields.io/badge/Linux-FCC624?logo=linux&logoColor=black&style=for-the-badge)](#) [![GPLv3](https://img.shields.io/badge/GPLv3-FFFFFF?style=for-the-badge)](#)

**Web-Recon** is a high-performance, production-grade asynchronous CLI/TUI utility engineered for passive reconnaissance (OSINT), mass network perimeter auditing, and deep infrastructure health tracking.

Unlike traditional, rigid brute-forcers or simple domain checkers, `Web-Recon` bridges the gap between reactive asynchronous scanning speeds and multi-dimensional OSINT data enrichment. Upon detecting any network anomaly (such as connection drops, DNS failures, timeouts, or non-200 HTTP response codes), the utility instantly spawns non-blocking background workers. These workers retrieve full WHOIS registration profiles, including registrar metadata, creation/expiration timelines, and active name servers, immediately packaging structured outputs into an atomic SQLite relational database.

---

## Core Architectural Features

* **Reactive Async Core (`asyncio` + `aiohttp`):** Orchestrates massive non-blocking request bursts through a single persistent `ClientSession` pipeline, bypassing heavy OS-level thread overhead. It leverages native response reason parsing to capture precise server-side execution context without bloated conditional statements.
* **Asynchronous Storage Sink (`aiosqlite`):** Delivers concurrent data persistence and dynamic runtime database schema mapping without causing Event Loop degradation or freezing the terminal layout. Table names are dynamically isolated inside strict `[]` SQL brackets to ensure complete structural query validation.
* **Thread-Isolated WHOIS Engine (`asyncio.to_thread`):** Smoothly offloads blocking synchronous network operations (Port 43 socket connections) onto native background thread scopes. This guarantees that sluggish or air-gapped domain lookups never block the main loop or interrupt the fluid TUI frame rendering.
* **Advanced Concurrency Control (Rate Limiting):** Implements fine-grained hardware task capping via an `asyncio.Semaphore` flag (`-c`) combined with configurable "Stealth Delays" (`-d`). This allows operators to audit infrastructure meticulously without generating accidental Denial-of-Service (DoS) footprints or triggering Web Application Firewall (WAF) blocks.
* **Headless Automation Mode (`--quiet`):** Provides a comprehensive automated scripting flag (`-q`) that completely suppresses all ANSI screen clear operations, ASCII artwork, split-panels, and progressive layout monitors. This enables seamless, silent integration inside headless bash pipelines and automated cron jobs.
* **Rigid CLI Parameter Binding (`argparse`):** Restructures runtime setup using standardized option parsing. It enforces configuration integrity by binding target URL inputs and list files inside a mutually exclusive parameter group.

---

## CLI Flags & Usage Manual

### Options Matrix

| Flag | Long Option | Data Type | Default | Description |
| :--- | :--- | :---: | :---: | :--- |
| `-t` | `--target` | `string` | *None* | Target a single URL for immediate individual audit. |
| `-f` | `--file` | `string` | *None* | Path to a `.txt` target list for bulk asynchronous exploration. |
| `-o` | `--output` | `string` | `RReport` | Custom SQLite database and synchronized table filename. |
| `-c` | `--concurrency`| `integer` | `50` | Maximum number of simultaneous network requests. |
| `-d` | `--delay` | `float` | `0.5` | Stealth delay time in seconds between parallel checks. |
| `-q` | `--quiet` | `flag` | `False` | Triggers Headless Silent Mode (kills all UI and drawings). |

### Practical Execution Examples

```bash
# Display the built-in technical manual and options layout
python recon.py --help

# Run a standard mass async perimeter scan with the interactive TUI dashboard active
python recon.py -f ./sites/targets.txt -o CorporateAudit

# Stealth Mode: Cap concurrency to 2 tasks and inject a strict 1.5s delay to evade WAF blocks
python recon.py -f ./sites/targets.txt -o StealthReport -c 2 -d 1.5

# Audit a single isolated target infrastructure
python recon.py -t https://linode.com -o OnDemandCheck

# Headless execution mode for background bash scripting pipelines
python recon.py -f ./sites/targets.txt -o AutomatedLog --quiet
```

---

## Security & SAST Audit Results

The application's source code has been audited via the **Bandit SAST Scanner** (Static Application Security Testing) against strict production security metrics.

* **Scan Result:** `No issues identified`
* **Metrics:** 0 Low, 0 Medium, 0 High severity flaws discovered.
* **Compliance:** Zero hardcoded credential leaks, zero unhandled execution paths, and zero unsanitized `eval()` shell operations.

---

## Release Notes (v0.6.0-RC)

This release elevates the repository to the formal standards required by the upstream **Kali Linux Packages** submission workflow. 
1. **Removed Manual I/O Blockers:** Deprecated all blocking, runtime keyboard-prompt hooks (`console.input()`), migrating lifecycle orchestration completely to programmatic arguments.
2. **Defensive Tabular Escaping:** Patched runtime schema compilation queries inside `init_db` and `insert_error` with `[]` encapsulation, preventing database execution crashes on user outputs containing hyphens or spaces.
3. **Muted Subsystem Logging:** Intercepted third-party stream telemetry from the underlying socket layer, forcing verbose connection errors on dead domains to drop silently in the background while keeping the main progress tracking UI pristine.


##  Author
- **Joseph Avatyants**
- GitHub: [@joavat-2009](https://github.com)
- Email: joavat2009@gmail.com
