from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List


@dataclass
class SourcePreference:
    enabled: bool = True
    weight: float = 1.0


@dataclass
class UserPreferences:
    desired_items: List[str] = field(default_factory=list)
    min_margin_percent: float = 10.0
    max_budget_usd: float = 500.0
    sources: Dict[str, SourcePreference] = field(default_factory=dict)
    alert_channels: Dict[str, Dict[str, str]] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, payload: str) -> "UserPreferences":
        raw = json.loads(payload)
        raw["sources"] = {k: SourcePreference(**v) for k, v in raw.get("sources", {}).items()}
        return cls(**raw)

    def save(self, path: Path) -> None:
        path.write_text(self.to_json(), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "UserPreferences":
        if not path.exists():
            return cls()
        return cls.from_json(path.read_text(encoding="utf-8"))
