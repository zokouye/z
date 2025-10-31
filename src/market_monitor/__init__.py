"""Market monitor toolkit."""

from .alerts import DiscordWebhookChannel, EmailAlertChannel, TelegramBotChannel, dispatch_alerts
from .detection import DealCandidate, DealRule, detect_deals
from .monitoring import MonitorRegistry
from .preferences import SourcePreference, UserPreferences
from .scheduler import JobScheduler

__all__ = [
    "DiscordWebhookChannel",
    "EmailAlertChannel",
    "TelegramBotChannel",
    "dispatch_alerts",
    "DealCandidate",
    "DealRule",
    "detect_deals",
    "MonitorRegistry",
    "SourcePreference",
    "UserPreferences",
    "JobScheduler",
]
