# Price Data Sources

This document summarizes the publicly known pricing endpoints for the Counter-Strike skin marketplaces that the platform can ingest. The table can be extended with additional sources as needed.

| Marketplace | Base URL | API / Endpoint | Authentication | Rate Limits & Notes |
|-------------|----------|----------------|----------------|---------------------|
| Steam Community Market | `https://steamcommunity.com/market/` | Unofficial JSON: `priceoverview/?appid=730&market_hash_name=<ITEM>`<br>Listings: `listings/<APPID>/<MARKET_HASH_NAME>/render/?query=&start=0&count=100` | No official API key. Requires Steam session cookies for authenticated queries. | Aggressive request throttling; recommended to keep under ~1 request/s. Response caching strongly advised. Captcha and temporary bans possible. |
| Buff163 | `https://buff.163.com/` | REST JSON: `api/market/goods?game=csgo&page_num=<PAGE>&search=<ITEM>`<br>Details: `api/market/goods/sell_order?game=csgo&goods_id=<ID>` | Requires login cookies or web session token. | Buff163 blocks repeated unauthenticated requests. Respect `X-RateLimit-Remaining` headers and use rotating proxies for high volume. |
| Skinport | `https://skinport.com/` | Public API: `api/bots/prices?app_id=730&currency=<CURRENCY>`<br>Item detail: `api/items/<APPID>/<MARKET_HASH_NAME>` | No auth for price list; optional API key for extended detail. | Rate limited to roughly 60 requests/minute per IP. Supports `If-Modified-Since` for caching. |
| CSFloat | `https://csfloat.com/` | Public API: `api/v1/listings` with query params `limit`, `page`, `sort`. | API key optional for higher limits. | Free tier limited to ~120 requests/minute. Provides float values. |
| Bitskins | `https://bitskins.com/` | REST: `api/v1/get_price_data_for_items_on_sale/?app_id=730&api_key=<KEY>` | Requires API key and 2FA code per request. | Hard limit of 25 requests/minute. |
| DMarket | `https://api.dmarket.com/` | REST JSON: `/exchange/v1/market/items` with filters; `/marketplace-api/v1/user/items` for user inventory. | Requires API key with OAuth 2.0. | Public endpoints limited to 60 requests/minute. Include `Request-Id` header for tracing. |
| Waxpeer | `https://api.waxpeer.com/` | REST: `/v1/prices/` `?game=csgo` for aggregated prices; `/v1/items/list` for live listings. | Requires API key. | Tiered rate limits starting at 1 request/sec. |
| CS.Money | `https://cs.money/` | REST JSON: `/api/v1/sell-offers?limit=<N>&offset=<N>` for skins, `/api/v1/sell-orders/<ID>` for details. | Requires session token retrieved from web app. | Anti-bot protections; introduce human-like delays and browser headers. |
| ShadowPay | `https://api.shadowpay.com/` | REST: `/api/v1/prices/{appId}`; `/api/v2/user/offers`. | Requires API key with JWT Bearer token. | 180 requests/minute for price endpoint. |
| Swap.GG | `https://api.swap.gg/` | REST: `/market/sell/orders` with filters. | Requires API key. | 120 requests/minute; supports websockets for live updates. |
| Lootbear | `https://api.lootbear.com/` | REST: `/v1/marketplace/listings?app_id=730`. | Requires API key. | 60 requests/minute baseline. |

## Helpful Conventions

* Default application identifier for CS:GO / CS2 skins is `730`.
* Always URL-encode the `market_hash_name` parameter.
* Many sources require TLS fingerprinting close to mainstream browsers; rotating user-agent strings is recommended.
* When scraping HTML-only sources, respect robots.txt and terms of service.
* Cache successful responses to reduce load and stay within rate limits.
