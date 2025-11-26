# Iran Proxy Finder

A fully dockerized utility that scrapes publicly available Iranian proxies, tests them against `https://ib.tejaratbank.ir/`, and stores the responsive proxies in `working_proxies.json`. A lightweight Flask web UI lets you start scans and follow logs in real time.

## Project Structure
```
.
├── docker-compose.yml
├── app/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── scraper.py
│   ├── tester.py
│   ├── run.py
│   └── working_proxies.json (generated after first run)
```

## Prerequisites
- Docker and Docker Compose (recommended), or
- Python 3.11+ with `pip` (for local runs)

## Quick Start (Docker)
1. Clone the repository:
   ```bash
   git clone <your-private-repo-url>
   cd iran_proxy_finder
   ```
2. Build and run (default web UI port is `5000`). If that port is busy, set `HOST_PORT` to any free port (for example `5001`):
   ```bash
   docker compose up --build
   # or
   HOST_PORT=5001 docker compose up --build
   ```
3. Open the web dashboard at `http://localhost:5000` (or your `HOST_PORT`).
   - Click **Start Scan** to fetch and validate proxies.
   - Watch progress in the live log panel.
   - Results are saved to `app/working_proxies.json` by default (see `OUTPUT_FILE`).

### Environment variables (Docker)
- `TARGET_URL` – request target used for validation. Default: `https://ib.tejaratbank.ir/`
- `VERIFY_IR` – set to `1` to enforce the proxy exit IP geolocates to Iran.
- `MAX_PROXIES` – cap how many proxies to test from the scrape.
- `OUTPUT_FILE` – override output path for results JSON (absolute or relative to `app/`).

Example:
```bash
HOST_PORT=5001 TARGET_URL=https://api.ipify.org?format=json MAX_PROXIES=200 docker compose up --build
```

## Local Run (without Docker)
1. Create a virtual environment and install deps:
   ```bash
   python3 -m venv .venv
   . .venv/bin/activate
   pip install -r app/requirements.txt
   ```
2. Run once in CLI mode:
   ```bash
   TARGET_URL=https://api.ipify.org?format=json MAX_PROXIES=100 python app/run.py --once
   ```
3. Or start the web UI (auto-runs a scan unless `--no-autostart`):
   ```bash
   python app/run.py --host 0.0.0.0 --port 5000
   ```

## Output
- Working proxies are saved to `app/working_proxies.json` (or `OUTPUT_FILE`) in the format:
  ```json
  [
    {"proxy": "IP:PORT", "latency": 1.234}
  ]
  ```
- Logs show success status and the connection scheme, e.g.:
  ```
  [OK] 91.107.190.207:8888 via http - 0.471s
  [FAIL] 31.25.92.114:8080
  ```
- Latest logs are visible in the web UI and printed to stdout.

## Web API
- `POST /start` – start a scan (no body)
- `GET /logs` – recent log lines
- `GET /status` – runner state (running, last started/finished)
- `GET /results` – JSON of working proxies

## Configuration & Extending
- Scrape sources are defined in `app/scraper.py` and include multiple providers and raw lists. Some sites may block automated requests.
- The tester in `app/tester.py` tries both `http` and `https` proxy schemes and considers `2xx–3xx` as success.
- Set `VERIFY_IR=1` to keep only proxies whose exit IP geolocates to Iran.
- Tweak timeouts and targets based on your use case.

## Notes
- Strict targets (e.g., banking sites) often block non-residential or non-IR exit IPs. Populate a proxy pool using general endpoints like `https://api.ipify.org?format=json` and then retest against the strict target.
- Public proxies are unstable and rotate often; repeat scans and higher `MAX_PROXIES` increase yield.
- Avoid committing secrets; this tool does not require any keys.
