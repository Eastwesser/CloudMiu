# MiuMiu 3.0 — roadmap

## Context (2.0, done)

| Piece | Value |
|-------|--------|
| Image | `eastwesser/home_arm_miumiu2:latest` |
| Container | `cloudmiu2` (`--network host`, WireGuard, `.env` from host) |
| Host | Raspberry Pi 3B+ (`armv7l`) |
| Boot | `wg-quick@wg0` + Docker `--restart unless-stopped` |

2.0 pillars that already work: Alice (YandexGPT) · Drawer · calc/converter · games · memes/stickers.

**Constraint for 3.0:** better text + images, **no** heavy local ML on the Pi (no torch/numpy stacks). Keep ARM image slim; quality lives in **remote APIs + better prompts**.

---

## Goal

Raise answer and drawing quality without raising Pi CPU/RAM load or breaking the Hub → Pi deploy loop.

Tag target: `eastwesser/home_arm_miumiu3:latest` · container `cloudmiu3` · keep `cloudmiu2` stopped for rollback.

---

## Priority order (do this order)

### P0 — Prompt & LLM quality (biggest win / cheapest)

Today Alice is a thin Yandex call. Make it intentional.

- [ ] System prompt file: `prompts/alice_system.txt` (character, language, refuse rules)
- [ ] Optional task prompts: `prompts/rewrite.txt`, `prompts/summary.txt`, `prompts/creative.txt`
- [ ] Few-shot (2–3 examples) in the system or first messages
- [ ] `.env` knobs (already partly hardcoded):

```env
YANDEX_TEMPERATURE=0.4
YANDEX_MAX_TOKENS=2000
YANDEX_SYSTEM_PROMPT_FILE=prompts/alice_system.txt
```

- [ ] Optional: short **per-user chat history** (last N turns) — needs tiny storage (P2 SQLite) or in-memory with TTL

**Keep YandexGPT as default** (RU keys, already wired). Do not force OpenAI/`gpt-4o-mini` unless you want a second paid path.

### P1 — Drawer quality (still API-only)

Do **not** run SD locally on Pi 3B+.

- [ ] Stronger **prompt rewrite** before draw (short Russian/English enhancer via Alice or a fixed template)
- [ ] **Negative prompt** support where the backend allows (FusionBrain / future Flux)
- [ ] Style presets as reply/inline buttons: anime · photo · sketch · sticker
- [ ] Size from `.env`: `DRAWER_WIDTH` / `DRAWER_HEIGHT` (or backend equivalents)
- [ ] Prefer quality backends when reachable: `fusionbrain` (RU) → optional Flux/Replicate later → Pollinations → mock
- [ ] Cache by prompt hash (file or SQLite) so repeats are free

### P2 — Light persistence (SQLite only)

One file volume on the Pi: `/home/pi/Desktop/home_miumiu/data` → `/app/data`.

- [ ] SQLite tables: `user_settings`, `chat_turns` (capped), `image_cache`
- [ ] `/clear` clears that user’s history
- [ ] No Postgres/Redis on the Pi for 3.0

### P3 — UX polish

- [ ] Inline: «Перегенерировать» · «Другой стиль» (Drawer)
- [ ] `/style` · `/clear` · keep existing Back / Main menu
- [ ] Always show «Рисую…» / «Думаю…» before slow API calls (partially done)

### P4 — Ops (nice, not blocking quality)

- [ ] Log to file: `LOG_FILE=/app/logs/bot.log` (+ rotate via host or docker log opts)
- [ ] Retry + backoff on Telegram / Yandex / drawer HTTP errors
- [ ] Optional admin alert if `vcgencmd measure_temp` > 80°C (host cron → bot, or sidecar — keep out of hot path)
- [ ] Rate limit per `user_id` (in-memory or SQLite)

---

## Architecture for 3.0 (evolve 2.0, don’t rewrite)

Keep Clean-ish layers you already have. Prefer **extract services**, not a greenfield tree.

```
config.py                 # + LLM/drawer prompt paths
prompts/                  # text files only
services/
  llm/                    # Yandex client + system prompt load
  drawer/                 # already exists — enhance
  storage/                # sqlite (P2)
routers/…                 # keep 4 domains; Alice/Drawer call services
app/runner.py             # unchanged polling/webhook
```

Avoid dragging everything into `handlers/text.py` / `image.py` unless you are ready for a big rename PR. Incremental > rewrite on Pi.

---

## `.env` additions (draft)

```env
# Alice / Yandex
YANDEX_TEMPERATURE=0.4
YANDEX_MAX_TOKENS=2000
YANDEX_SYSTEM_PROMPT_FILE=prompts/alice_system.txt
ALICE_HISTORY_TURNS=6

# Drawer
DRAWER_BACKEND=fusionbrain
DRAWER_FALLBACK_MOCK=true
DRAWER_STYLE=anime
DRAWER_NEGATIVE_PROMPT=blurry, low quality, text, watermark
DRAWER_CACHE=true

# Ops
LOG_LEVEL=INFO
LOG_FILE=/app/logs/bot.log
DATA_DIR=/app/data
```

---

## ARM / deploy notes (unchanged discipline)

- Build only: `docker buildx build --platform linux/arm/v7 -t eastwesser/home_arm_miumiu3:latest --push .`
- No torch / local SD / heavy CV libs
- Volume for data: `-v /home/pi/Desktop/home_miumiu/data:/app/data`
- One polling container per `BOT_TOKEN`
- Rollback: `docker stop cloudmiu3 && docker start cloudmiu2`

```bash
docker pull eastwesser/home_arm_miumiu3:latest
docker stop cloudmiu2
docker run -d --name cloudmiu3 --restart unless-stopped \
  --network host \
  -v /home/pi/Desktop/home_miumiu/.env:/app/.env:ro \
  -v /home/pi/Desktop/home_miumiu/data:/app/data \
  -v /home/pi/Desktop/home_miumiu/logs:/app/logs \
  eastwesser/home_arm_miumiu3:latest
```

---

## Suggested first slice (start coding here)

1. `prompts/alice_system.txt` + load in Alice handler  
2. Env for temperature / max_tokens  
3. Drawer: style presets + negative prompt + “enhancing…” caption  
4. Ship as `miumiu3` only after Windows smoke + ARM push  

Later: SQLite history + image cache + regen buttons.

---

## Parked for 4.0+

Voice (Whisper/TTS) · admin web · channel autopost · plugin commands · calendar/reminders.

---

## Decision log

| Topic | Decision |
|-------|----------|
| Pi scheduling | Host WG + Docker restart; no second scheduler needed |
| Local image models on Pi | **No** for 3.0 |
| Default LLM | Stay on **YandexGPT** |
| Default draw | Prefer **FusionBrain** when keys work; Pollinations as free fallback |
| Storage | **SQLite** only if we need history/cache |
| Rewrite vs evolve | **Evolve** `services/` + `prompts/` |
