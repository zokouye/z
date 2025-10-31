# Market Monitor

A modular toolkit for aggregating Counter-Strike skin prices across popular marketplaces, unifying the data, and detecting profitable deals based on user-defined preferences.

## Features

1. **Multi-source collectors** – Modular HTTP collectors with retry/backoff logic for Steam Market, Buff163, and Skinport.
2. **Normalization pipeline** – Standardizes item names, converts currencies to USD, and aggregates quotes.
3. **Deal detection** – Margin and price-drop rules identify attractive offers.
4. **User preferences** – JSON-backed profile with CLI overrides and per-source weighting.
5. **Alerts & scheduling** – Email, Discord, Telegram outputs and a lightweight scheduler for recurring refreshes.
6. **Observability** – Centralized logging and a monitoring registry for price metrics.
7. **Documentation & tests** – Source catalogue plus unit tests covering the critical pieces.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # installs the test tooling

# Optional: enable HTTP collectors and webhook alerts
pip install httpx
```

## Usage

1. Create or edit `preferences.json` to define target items, budget, and alert credentials.
2. Run the CLI, supplying desired items if they are not already in the preferences file:

```bash
python -m market_monitor.cli "AK-47 | Redline (Field-Tested)"
```

3. Integrate in a service loop by combining the scheduler and service helper:

```python
from market_monitor.collectors.buff163 import Buff163Collector
from market_monitor.collectors.skinport import SkinportCollector
from market_monitor.collectors.steam import SteamMarketCollector
from market_monitor.monitoring import MonitorRegistry
from market_monitor.preferences import UserPreferences
from market_monitor.scheduler import JobScheduler
from market_monitor.service import run_once

collectors = [SteamMarketCollector(), Buff163Collector(), SkinportCollector()]
preferences = UserPreferences.load(Path("preferences.json"))
monitor = MonitorRegistry()

scheduler = JobScheduler()
scheduler.add_job(300, lambda: run_once(collectors, preferences, monitor, []))
scheduler.start()
```

## Tests

```bash
pytest
```

## Additional Documentation

* [Price sources and API coverage](docs/price_sources.md)
