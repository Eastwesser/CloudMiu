# CloudMiuyaka TODO

## Done (ship-ready code)

- [x] Pluggable drawer: pollinations / fusionbrain / leonardo / craiyon-host / mock / auto
- [x] Free Pollinations drawer (+ optional `POLLINATIONS_TOKEN`)
- [x] Offline mock + fallback
- [x] Alice button → YandexGPT chat (menu kept; async httpx)
- [x] Polling vs webhook runner
- [x] Unit tests for drawer/config/runner
- [x] Wire reply buttons to the same handlers as slash commands
- [x] docker-compose + Makefile / make.bat (Windows)
- [x] Domain fixes: stickers, weather, calculator FSM, converter FSM, games UX
- [x] Memes 1–224 (jpg/png/mp4) + per-user no-dupe deck + reset

## Do on Windows (you — not blocking the zip)

- [ ] `make.bat up` then `make.bat logs` (Docker Desktop running)
- [ ] Smoke: Memes · Alice · Drawer · Calculator · one Game
- [ ] Confirm `POLLINATIONS_TOKEN` is real (not a placeholder)
- [ ] If Drawer blocked (TSPU): `DRAWER_BACKEND=fusionbrain` → `make.bat restart`

## Nice later (optional, not required to ship)

- [ ] Webhook mode + public HTTPS (when you have a site)
- [ ] YandexART drawer (same Yandex Cloud bill as Alice)
- [ ] Persist meme “seen” set across restarts (now in-memory)
- [ ] Trim dead commented video→mp3 stubs

## Drop / ignore

- [ ] Restore adtime.pro / official Craiyon API
- [ ] Leonardo until foreign payment works
- [ ] Apify
