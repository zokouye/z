from market_monitor.collectors.base import PriceQuote
from market_monitor.monitoring import MonitorRegistry
from market_monitor.collectors.base import PriceQuote
from market_monitor.monitoring import MonitorRegistry
from market_monitor.preferences import UserPreferences
from market_monitor.service import run_once


class DummyCollector:
    name = "dummy"

    def fetch(self, items):
        return [PriceQuote(source=self.name, market_hash_name=item, price=100.0, currency="USD") for item in items]


class DummyChannel:
    def __init__(self):
        self.sent = []
        self.name = "dummy_channel"

    def send(self, messages):
        self.sent.extend(messages)


def test_run_once_dispatches_alert_when_deal(monkeypatch):
    collector = DummyCollector()
    preferences = UserPreferences(desired_items=["AK-47"], min_margin_percent=0.0, max_budget_usd=200.0)
    monitor = MonitorRegistry()

    from market_monitor import service as service_module

    def fake_detect(aggregated, rules):
        return [
            service_module.DealCandidate(
                normalized_name="ak-47",
                market_hash_name="AK-47",
                target_price_usd=90.0,
                best_source={"source": "dummy", "price_usd": 90.0},
                margin_percent=10.0,
                price_drop_percent=5.0,
            )
        ]

    monkeypatch.setattr(service_module, "detect_deals", fake_detect)

    channel = DummyChannel()
    deals = run_once([collector], preferences, monitor, [channel])
    assert deals
    assert channel.sent
