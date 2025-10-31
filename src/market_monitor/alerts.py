from __future__ import annotations

import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from typing import Iterable, Protocol, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - imported for typing only
    import httpx

from .logging_config import get_logger

logger = get_logger(__name__)


class AlertChannel(Protocol):
    name: str

    def send(self, messages: Iterable[str]) -> None:
        ...


@dataclass
class EmailAlertChannel:
    name: str = "email"
    smtp_host: str = "localhost"
    smtp_port: int = 25
    sender: str = "alerts@example.com"
    recipients: tuple[str, ...] = ()

    def send(self, messages: Iterable[str]) -> None:
        if not self.recipients:
            logger.warning("Email channel disabled - no recipients configured")
            return
        body = "\n".join(messages)
        email = EmailMessage()
        email["Subject"] = "Market deals"
        email["From"] = self.sender
        email["To"] = ", ".join(self.recipients)
        email.set_content(body)
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as client:
            client.send_message(email)


@dataclass
class DiscordWebhookChannel:
    name: str = "discord"
    webhook_url: str = ""

    def send(self, messages: Iterable[str]) -> None:
        if not self.webhook_url:
            logger.warning("Discord channel disabled - missing webhook URL")
            return
        payload = {"content": "\n".join(messages)}
        response = _post_json(self.webhook_url, payload)
        response.raise_for_status()


@dataclass
class TelegramBotChannel:
    name: str = "telegram"
    bot_token: str = ""
    chat_id: str = ""

    def send(self, messages: Iterable[str]) -> None:
        if not (self.bot_token and self.chat_id):
            logger.warning("Telegram channel disabled - missing credentials")
            return
        payload = {"chat_id": self.chat_id, "text": "\n".join(messages)}
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        response = _post_json(url, payload)
        response.raise_for_status()


def dispatch_alerts(channels: Iterable[AlertChannel], messages: Iterable[str]) -> None:
    messages = list(messages)
    for channel in channels:
        try:
            channel.send(messages)
        except Exception as exc:  # pragma: no cover
            logger.exception("Failed to send alerts via %s: %s", channel.name, exc)


def _post_json(url: str, payload: dict[str, object]):
    try:
        import httpx
    except ModuleNotFoundError as exc:  # pragma: no cover - exercised in environments without httpx
        raise RuntimeError(
            "httpx is required for webhook-based alert channels. Install the 'httpx' extra to enable them."
        ) from exc

    return httpx.post(url, json=payload, timeout=10.0)
