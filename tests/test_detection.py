from market_monitor.detection import DealRule, detect_deals


def test_detect_deals_filters_by_margin_and_drop():
    aggregated = {
        "ak-47": {
            "normalized_name": "ak-47",
            "market_hash_name": "AK-47",
            "avg_price_usd": 120.0,
            "sources": [
                {"source": "skinport", "price_usd": 90.0},
                {"source": "steam", "price_usd": 130.0},
            ],
        }
    }
    rules = DealRule(min_margin_percent=20.0, max_price_usd=100.0, lookback_prices=[130.0, 125.0], price_drop_percent=5.0)
    deals = detect_deals(aggregated, rules)
    assert deals
    deal = deals[0]
    assert deal.best_source["source"] == "skinport"
    assert deal.margin_percent >= 20.0
