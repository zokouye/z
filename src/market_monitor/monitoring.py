from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from typing import Dict, Iterable

from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class MetricSnapshot:
    name: str
    values: list[float] = field(default_factory=list)

    def add(self, value: float) -> None:
        self.values.append(value)

    def summary(self) -> Dict[str, float]:
        if not self.values:
            return {"count": 0, "avg": 0.0, "min": 0.0, "max": 0.0}
        return {
            "count": len(self.values),
            "avg": statistics.mean(self.values),
            "min": min(self.values),
            "max": max(self.values),
        }


class MonitorRegistry:
    def __init__(self) -> None:
        self._metrics: Dict[str, MetricSnapshot] = {}

    def observe(self, name: str, value: float) -> None:
        metric = self._metrics.setdefault(name, MetricSnapshot(name))
        metric.add(value)

    def report(self) -> Dict[str, Dict[str, float]]:
        report: Dict[str, Dict[str, float]] = {}
        for name, metric in self._metrics.items():
            report[name] = metric.summary()
        logger.info("Metrics report: %s", report)
        return report


def monitor_prices(monitor: MonitorRegistry, prices: Iterable[float]) -> None:
    for value in prices:
        monitor.observe("price_usd", value)
