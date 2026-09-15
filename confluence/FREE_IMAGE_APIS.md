# Free / cheap image APIs for MiuMiu drawer

## Winner for us: **Pollinations.AI**

| | |
|--|--|
| Cost | **Free**, no card |
| Key | **Not required** (optional free signup → higher rate / less watermark) |
| Call | `GET https://image.pollinations.ai/prompt/{prompt}` |
| Limits | ~1 req / 15s anonymous; better after free register at auth.pollinations.ai |
| MiuMiu | `DRAWER_BACKEND=pollinations` (default now) |

Docs: https://github.com/pollinations/pollinations/blob/master/APIDOCS.md

## Other options (short)

| Service | Free API? | Card? | Notes for RF / TSPU |
|---------|-----------|-------|---------------------|
| **Pollinations** | Yes | No | Best fit; may be blocked by TSPU sometimes → mock fallback |
| **FusionBrain / Kandinsky** | Limited / often paid for API | Mir/Sber OK | Already in bot; use if Pollinations blocked |
| **AI Horde** | Yes (kudos / slow queue) | No | Crowdsourced; flaky quality/wait |
| **Cloudflare Workers AI** | 10k Neurons/day | Usually no for free tier | Needs CF account; image models available |
| **Hugging Face Inference** | Tiny free credit | No | Limits tight for image gen |
| **Craiyon.com** | Web only | — | **No public API** |
| **Leonardo / OpenAI** | Trial then $ | Foreign card | Skip for now |
| **YandexART** | Billed YC | Yandex bill | Possible later (you already have Yandex for Alice) |

## Recommended `.env`

```env
DRAWER_BACKEND=pollinations
# or: auto  (= Pollinations → FusionBrain → … → mock)
DRAWER_FALLBACK_MOCK=true
POLLINATIONS_MODEL=flux
# optional free token from https://auth.pollinations.ai
POLLINATIONS_TOKEN=
```
