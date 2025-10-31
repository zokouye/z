from pathlib import Path

from market_monitor.preferences import SourcePreference, UserPreferences


def test_preferences_serialization(tmp_path: Path):
    prefs = UserPreferences(
        desired_items=["AK-47"],
        min_margin_percent=15.0,
        max_budget_usd=250.0,
        sources={"skinport": SourcePreference(enabled=True, weight=1.2)},
        alert_channels={"discord": {"webhook_url": "https://example.com"}},
    )
    path = tmp_path / "prefs.json"
    prefs.save(path)
    loaded = UserPreferences.load(path)
    assert loaded.desired_items == ["AK-47"]
    assert loaded.sources["skinport"].weight == 1.2
    assert loaded.alert_channels["discord"]["webhook_url"] == "https://example.com"
