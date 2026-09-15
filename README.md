# MiuMiu 2.0 (CloudMiuyaka)

Friendly Telegram bot on **aiogram 3** + asyncio. Runs in Docker or on a Raspberry Pi.

## Features

**Core pillars:** Alice chat (YandexGPT) · Drawer · Calculator/Converter · Games

**Also:** weather, magnetic storms, currency, memes, stickers.

See `confluence/FEATURES.md` for backends and why **not Apify**.

## Layout

```
main.py                 # entry
config.py               # pydantic settings from .env
app/runner.py           # polling | webhook lifecycle
services/leonardo.py    # async Leonardo client
routers/…/drawer.py     # drawer FSM handlers
routers/…/photobot.py   # memes / stickers / presentation
```

## Bot update mode

Telegram Bot API does **not** offer a client WebSocket for updates.

| `BOT_MODE` | When to use |
|------------|-------------|
| `polling` (default) | Local / Pi without public HTTPS |
| `webhook` | Public HTTPS reverse-proxy → `WEBHOOK_PORT` |

Webhook example:

```env
BOT_MODE=webhook
WEBHOOK_HOST=https://bot.yourdomain.com
WEBHOOK_PATH=/telegram/webhook
WEBHOOK_SECRET=long-random-string
WEBHOOK_PORT=8080
```

Point nginx/caddy at `http://127.0.0.1:8080/telegram/webhook`.

## Drawer backends

| `DRAWER_BACKEND` | Meaning |
|------------------|---------|
| **`pollinations`** (default) | **Free** Pollinations.AI — no key/card |
| `fusionbrain` | Kandinsky (RU keys) |
| `mock` | Offline placeholder |
| `craiyon` | Only if you host a compatible API |
| `leonardo` | Paid/credit |
| `auto` | Pollinations → FusionBrain → … → mock |

See `confluence/FREE_IMAGE_APIS.md`.

## Tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

Covers Leonardo client (mocked HTTP), drawer handlers, config/keyboards, polling vs webhook selection.

## Docker (Windows / Pi)

Need Docker Desktop (Windows) and a filled `.env`.

**PowerShell** (note the `.\` — required):

```powershell
cd path\to\CloudMiuyaka
.\make.bat up
.\make.bat logs
.\make.bat down
```

**CMD**:

```bat
cd path\to\CloudMiuyaka
make.bat up
make.bat logs
```

With GNU make (Git Bash / WSL / Chocolatey):

```bash
make up
make logs
make down
```

Polling needs no published ports. For webhook later: set `BOT_MODE=webhook` and uncomment `ports` in `docker-compose.yml`.

## Raspberry Pi 3B+ (ARM, Docker Hub)

Do **not** `docker build` on Windows without `--platform linux/arm/v7` — that image will not run on the Pi.

Full steps (buildx push + Pi stop/start, VPN, rollback): **`PI_DEPLOY.md`**.

```powershell
docker login
.\make.bat arm-push
```

On the Pi: `docker stop cloudmiu` then run `cloudmiu2` from `eastwesser/home_arm_miumiu2:latest` with `--network host` and the host `.env`. Never poll the same token twice.

## Local run (Windows, no Docker)

Use **Python 3.10–3.12** already installed (`python --version`). Prefer one folder only (don’t mix an old Desktop `\cloudmiuyaka` venv with a new unzip).

```powershell
cd path\to\CloudMiuyaka
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
# Edit .env → BOT_TOKEN from @BotFather (fresh token if Unauthorized)
python main.py
```

If Activate.ps1 is blocked: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### Telegram Unauthorized

Bot code is fine if you see `Starting bot in POLLING mode` then `Unauthorized`.
That means Telegram rejected `BOT_TOKEN` in **this** folder’s `.env`:

1. @BotFather → `/mybots` → bot → API Token → copy
2. Put in `.env`: `BOT_TOKEN=123456:AA…` (no spaces/quotes)
3. Save as UTF-8, run `python main.py` again

In Telegram: Help → **Drawer** → prompt / Memes / Alice / Games.


## .env sample

```env
BOT_TOKEN=
WEATHER_API_TOKEN=
NASA_API_TOKEN=
OPEN_EXCHANGE_TOKEN=
YANDEX_ID_ADMIN=
YANDEX_API_KEY=
LEONARDO_API_KEY=
LEONARDO_MODEL=phoenix-v1.0
LEONARDO_MODE=FAST
BOT_MODE=polling
WEBHOOK_HOST=
WEBHOOK_PATH=/telegram/webhook
WEBHOOK_SECRET=
WEBHOOK_PORT=8080
```

`FUSION_BRAIN_*` — used when `DRAWER_BACKEND=fusionbrain` or `auto`.

## Run

```bash
pip install -r requirements.txt
python main.py
# or
docker build -t miumiu . && docker run --env-file .env -p 8080:8080 miumiu
```

23.04.2026 — homecoming day (beget cloud → Raspberry Pi 3)
