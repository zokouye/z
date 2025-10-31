from __future__ import annotations

from typing import Iterable

from .alerts import AlertChannel, dispatch_alerts
from .cli import run_collectors
from .collectors.base import PriceCollector
from .detection import DealCandidate, DealRule, detect_deals
from .logging_config import get_logger
from .monitoring import MonitorRegistry, monitor_prices
from .pipeline.unification import aggregate_by_item, unify_quotes
from .preferences import UserPreferences

logger = get_logger(__name__)


def build_messages(deals: Iterable[DealCandidate]) -> list[str]:
    messages = []
    for deal in deals:
        messages.append(
            f"{deal.market_hash_name}: {deal.target_price_usd:.2f} USD via {deal.best_source['source']} (margin {deal.margin_percent:.1f}% drop {deal.price_drop_percent:.1f}%)"
        )
    return messages


def run_once(
    collectors: list[PriceCollector],
    preferences: UserPreferences,
    monitor: MonitorRegistry,
    alert_channels: Iterable[AlertChannel],
) -> list[DealCandidate]:
    enabled_collectors = []
    for collector in collectors:
        preference = preferences.sources.get(collector.name)
        if preference is None or getattr(preference, "enabled", True):
            enabled_collectors.append(collector)
    quotes = run_collectors(enabled_collectors, preferences.desired_items)
    unified = unify_quotes(quotes)
    aggregated = aggregate_by_item(unified)
    monitor_prices(monitor, [entry["price_usd"] for entry in unified])
    rules = DealRule(
        min_margin_percent=preferences.min_margin_percent,
        max_price_usd=preferences.max_budget_usd,
        lookback_prices=[],
        price_drop_percent=5.0,
    )
    deals = detect_deals(aggregated, rules)
    if deals:
        messages = build_messages(deals)
        dispatch_alerts(alert_channels, messages)
    monitor.report()
    return deals
