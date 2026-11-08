---

##  Project Roadmap & Future Milestones

This development timeline charts the active engineering milestones projected for the upcoming major and minor architecture updates of `Web-Recon`.

###  Phase 1: Core Automation & Architecture Hardening (v0.6.0 - Current Release)
* [x] **Asynchronous Refactoring:** Full transition from rigid OS threads to a non-blocking `asyncio` event-driven lifecycle.
* [x] **CLI Standardization:** Implementation of programmatic argument parsing (`argparse`) and complete deprecation of blocking interactive input fields.
* [x] **Throttling & Guard Rails:** Added hardware concurrency limitations via `asyncio.Semaphore` and configurable sub-second stealth delays to avoid accidental DoS vectors.
* [x] **CI/CD Integration:** Deployment of an automated structural testing pipeline using `pytest` running inside GitHub Actions.
* [x] **Packaging Transition:** Complete migration to the modernized `src-layout` directory mapping and automated backend builds setup via `pyproject.toml`.

###  Phase 2: Data Sanitization & Network Stealth (v0.6.1 - Up Next)
* [ ] **WHOIS Output Cleansing:** Implement runtime `isinstance` checks to filter and strip programmatic array string structures (`['...']`) out of multiline WHOIS string persists, enforcing human-readable schema outputs.
* [ ] **Smarter Timeout Bounds:** Introduce specialized connection drop interceptors to handle air-gapped host exploration without loop degradation.
* [ ] **Network Evasion Mechanics:** Integrate dynamic User-Agent rotation layers to mimic varied browser traversal behavior and evade adaptive WAF barriers.

###  Phase 3: Defensive Auditing Extensions (v0.7.0)
* [ ] **Asynchronous Directory Discovery:** Deploy a high-velocity concurrent folder brute-forcing core utilizing a customizable, layered flat-file dictionary ingestion.
* [ ] **Targeted Configuration Exposure Checks:** Implement optimized request pipelines targeting isolated hidden configurations (e.g., exposed runtime environments like `/.env`, decoupled repository indices like `/.git/config`, and isolated configuration payloads).
* [ ] **Relational Database Sharding:** Introduce customizable table partitioning configurations based on explicit scan-job domains to isolate massive network discovery batches.
