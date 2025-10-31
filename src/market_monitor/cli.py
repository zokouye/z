from __future__ import annotations

import argparse
from pathlib import Path

from .detection import DealRule, detect_deals
from .logging_config import get_logger
from .pipeline.unification import aggregate_by_item, unify_quotes
from .preferences import UserPreferences
from .collectors.base import PriceCollector, PriceQuote

logger = get_logger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Market monitor CLI")
    parser.add_argument("items", nargs="*", help="Market hash names to monitor")
    parser.add_argument("--preferences", type=Path, default=Path("preferences.json"))
    parser.add_argument("--min-margin", type=float, help="Override minimum margin percent")
    parser.add_argument("--max-price", type=float, help="Maximum acceptable price in USD")
    return parser


def run_collectors(collectors: list[PriceCollector], items: list[str]) -> list[PriceQuote]:
    quotes: list[PriceQuote] = []
    for collector in collectors:
        logger.info("Collecting from %s", collector.name)
        try:
            quotes.extend(collector.fetch(items))
        except Exception as exc:  # pragma: no cover
            logger.exception("Collector %s failed: %s", collector.name, exc)
    return quotes


def run_cli(collectors: list[PriceCollector]) -> None:
    parser = build_parser()
    args = parser.parse_args()
    preferences = UserPreferences.load(args.preferences)
    if args.items:
        preferences.desired_items = args.items
    if args.min_margin is not None:
        preferences.min_margin_percent = args.min_margin
    if args.max_price is not None:
        preferences.max_budget_usd = args.max_price

    enabled_collectors = []
    for collector in collectors:
        preference = preferences.sources.get(collector.name)
        if preference is None or getattr(preference, "enabled", True):
            enabled_collectors.append(collector)
    quotes = run_collectors(enabled_collectors, preferences.desired_items)
    unified = unify_quotes(quotes)
    aggregated = aggregate_by_item(unified)

    rule = DealRule(
        min_margin_percent=preferences.min_margin_percent,
        max_price_usd=preferences.max_budget_usd,
        lookback_prices=[],
        price_drop_percent=5.0,
    )
    deals = detect_deals(aggregated, rule)

    if not deals:
        logger.info("No deals found.")
        return

    for deal in deals:
        logger.info(
            "%s: buy at %.2f USD via %s (margin %.2f%% drop %.2f%%)",
            deal.market_hash_name,
            deal.target_price_usd,
            deal.best_source["source"],
            deal.margin_percent,
            deal.price_drop_percent,
        )
