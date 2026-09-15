# Raspberry Pi 3B+ (ARMv7) — CloudMiu 2.0 via Docker Hub

**Do not run two polling containers with the same `BOT_TOKEN`.** That is the `TelegramConflictError` you already saw.

Keep the old container **stopped** (not deleted) until 2.0 looks healthy.

| Piece | Value |
|-------|--------|
| Hub image | `eastwesser/home_arm_miumiu2:latest` |
| Platform | `linux/arm/v7` (Pi 3B+ / `armv7l`) |
| Old container | `cloudmiu` |
| New container | `cloudmiu2` |
| `.env` on Pi | `/home/pi/Desktop/home_miumiu/.env` |
| Network | `--network host` (uses host WireGuard) |

Flash / `tar` = backup of configs only. **Not** how you update the bot.

---

## 1. Windows — one-time: Docker Desktop + buildx

1. Docker Desktop running, **WSL2 backend** on.
2. Settings → Docker Engine: leave defaults. QEMU for ARM is bundled.
3. Log in to Hub:

```powershell
docker login
# username: eastwesser
```

4. Builder (once):

```powershell
docker buildx create --name miumiuarm --use --bootstrap
docker buildx ls
```

You want a line with `linux/arm/v7`.

---

## 2. Windows — build ARM image and push

From the unzipped `CloudMiuyaka` folder (the one with `Dockerfile`):

```powershell
cd C:\Users\altte\OneDrive\Desktop\CloudMiuyaka_2.0\CloudMiuyaka

.\make.bat arm-push
```

Same thing by hand:

```powershell
docker buildx build --platform linux/arm/v7 -t eastwesser/home_arm_miumiu2:latest --push .
```

`--push` uploads to Hub. Local `docker images` may **not** show the ARM image; that is normal.

Build takes a long time (aiohttp/psutil compile under QEMU). Let it finish.

Optional extra tag (rollback):

```powershell
docker buildx build --platform linux/arm/v7 -t eastwesser/home_arm_miumiu2:v2 --push .
```

Hub check: https://hub.docker.com/r/eastwesser/home_arm_miumiu2/tags

`.env` is **not** in the image (`.dockerignore`). Pi still mounts the host file.

---

## 3. Raspberry Pi — stop old, pull, start new

SSH to the Pi. **Do not** `docker rm cloudmiu` until you are sure.

```bash
# 0. Confirm arch
uname -m
# expect: armv7l

# 1. Pull 2.0
docker pull eastwesser/home_arm_miumiu2:latest

# 2. Stop the OLD bot only (keeps the container for rollback)
docker stop cloudmiu

# 3. Start 2.0 (host net = WireGuard on the Pi)
docker run -d \
  --name cloudmiu2 \
  --restart unless-stopped \
  --network host \
  -v /home/pi/Desktop/home_miumiu/.env:/app/.env:ro \
  eastwesser/home_arm_miumiu2:latest

# 4. Logs — want POLLING, no Unauthorized, no Conflict
docker logs --tail 40 -f cloudmiu2
```

If `.env` for 2.0 lives elsewhere, change the `-v` path. Same token as the old bot is fine **only because `cloudmiu` is stopped**.

---

## 4. VPN check (host WireGuard)

`--network host` → bot uses the Pi’s default route (WG if that is default).

On the Pi:

```bash
# WG up?
sudo wg show
# or: ip link | grep -E 'wg|amnezia'

# From INSIDE the new container (host net = same stack)
docker exec cloudmiu2 python -c "import socket; print(socket.gethostname())"
docker exec cloudmiu2 sh -c 'python - <<"PY"
import urllib.request
print(urllib.request.urlopen("https://api.telegram.org", timeout=15).status)
PY'
```

`200` (or Telegram HTML) = outbound HTTPS works. Then in Telegram tap Help / Memes.

If Telegram is blocked without VPN, confirm `wg show` has a handshake **before** blaming the image.

---

## 5. Rollback (old image still there)

```bash
docker stop cloudmiu2
docker start cloudmiu
docker logs --tail 30 -f cloudmiu
```

When 2.0 is trusted:

```bash
docker rm cloudmiu2   # only if you want to recreate it
# optional later: docker rm cloudmiu
```

---

## 6. If ARM build fails on Windows

- Enable virtualization / WSL2.
- `docker buildx inspect --bootstrap` and confirm `linux/arm/v7`.
- Do **not** `docker build` without `--platform` — that produces **amd64**, which will not run on Pi 3B+.
- `exec format error` on the Pi = wrong architecture image.

---

## 7. Two versions at once

**No**, not with the same token. Stop one, start the other.
