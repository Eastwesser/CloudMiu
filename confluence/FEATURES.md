# MiuMiu 2.0 — product pillars

## Must work

| Pillar | UI | Backend | Status |
|--------|-----|---------|--------|
| Chat (Alice) | **Alice** / legacy YandexGPT → `/ask_miumiu_gpt` | YandexGPT Lite (`YANDEX_*`) | already in `business.py` |
| Draw | **Drawer** → `/start_drawer` | `DRAWER_BACKEND` pluggable | mock / fusionbrain / leonardo / auto |
| Calculate | **Calculator** / **Converter** | local mathix | already |
| Play | **Games** | RPS, Blackjack, BlockMe, emoji… | already |

Also: weather, currency, memes, stickers (nice-to-have).

## Drawer: what to use (RU / no foreign card)

| Option | Verdict for you |
|--------|-----------------|
| **Craiyon.com website** | Free UI login ≠ API. **No public API key** today (Enterprise/contact only; “coming soon” on pricing FAQ). |
| **Craiyon-compatible host** | Our `craiyon` drawer talks to a server with AdTime-like `/login` + `/generate`. Only works if *you* host/restore that service. |
| **mock** | Always works offline (TSPU). Placeholder art. |
| **FusionBrain / Kandinsky** | Best real draw from RF right now. |
| **Leonardo** | Quality later; foreign payment. |
| **Apify** | **Skip**. |
| **GigaChat image API** | Possible later (Sber ecosystem); separate product from FusionBrain keys. |
| **YandexART** | If you already have Yandex Cloud — optional future drawer class. |
| **Local SD on PC** | Free/offline if you have GPU; heavy for Pi 3. |
| **Pollinations / HF Spaces** | Often free but flaky + often blocked/geo-limited. |

**Recommendation now:** `DRAWER_BACKEND=fusionbrain` (or `auto` without Craiyon host) + `DRAWER_FALLBACK_MOCK=true`.  
Craiyon.com free account does **not** give an API key — forget waiting for one in the account UI.

## Apify in one line

Apify = run scrapers/actors in the cloud. It does **not** replace Kandinsky/Leonardo; image “actors” wrap other paid APIs. Not a fix for MiuMiu drawer.
