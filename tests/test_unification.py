from market_monitor.collectors.base import PriceQuote
from market_monitor.pipeline.unification import aggregate_by_item, normalize_name, unify_quotes


def test_normalize_name_removes_symbols():
    assert normalize_name("StatTrak™ AK-47 | Redline (Field-Tested)") == "stattrak ak-47 | redline (field-tested)"


def test_unify_quotes_converts_currency():
    quotes = [
        PriceQuote(source="skinport", market_hash_name="AK-47", price=100.0, currency="USD"),
        PriceQuote(source="buff163", market_hash_name="AK-47", price=500.0, currency="CNY"),
    ]
    unified = unify_quotes(quotes)
    assert unified[0]["price_usd"] == 100.0
    assert unified[1]["price_usd"] == 70.0


def test_aggregate_by_item_stats():
    quotes = [
        {"normalized_name": "ak-47", "market_hash_name": "AK-47", "price_usd": 100.0, "source": "skinport", "currency": "USD", "price": 100.0, "metadata": {}},
        {"normalized_name": "ak-47", "market_hash_name": "AK-47", "price_usd": 120.0, "source": "steam", "currency": "USD", "price": 120.0, "metadata": {}},
    ]
    aggregated = aggregate_by_item(quotes)
    assert aggregated["ak-47"]["min_price_usd"] == 100.0
    assert aggregated["ak-47"]["max_price_usd"] == 120.0
    assert aggregated["ak-47"]["avg_price_usd"] == 110.0
