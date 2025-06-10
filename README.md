# MiuMiu

MiuMiu, your friendly Telegram bot, has undergone exciting updates, bringing a plethora of new features to enhance your
chatting experience. Powered by asyncio and aiogram, constantly running in Docker, MiuMiu is now smarter and more 
versatile than ever before! 😎

## Features

**Weather Updates**: Receive real-time weather forecasts with detailed information on timing and atmospheric pressure, 
courtesy of OpenWeatherAPI. You can get weather updates for any city on the planet.

**Magnetic Storm Alerts**: Stay informed about magnetic storms using data from NASA tokens.

**Conversation with YandexGPT**: Engage in conversations with YandexGPT for interesting interactions.

**Currency Conversion**: Convert currency at the current exchange rate. The following currency pairs are supported:

1. **USD to EUR**: Convert from US Dollar (USD) to Euro (EUR)
2. **EUR to USD**: Convert from Euro (EUR) to US Dollar (USD)
3. **USD to GBP**: Convert from US Dollar (USD) to British Pound (GBP)
4. **USD to RUB**: Convert from US Dollar (USD) to Russian Ruble (RUB)
5. **EUR to RUB**: Convert from Euro (EUR) to Russian Ruble (RUB)
6. **HUF to RUB**: Convert from Hungarian Forint (HUF) to Russian Ruble (RUB)
7. **RSD to RUB**: Convert from Serbian Dinar (RSD) to Russian Ruble (RUB)
8. **AMD to RUB**: Convert from Armenian Dram (AMD) to Russian Ruble (RUB)
9. **CNY to RUB**: Convert from Chinese Yuan (CNY) to Russian Ruble (RUB)
10. **JPY to RUB**: Convert from Japanese Yen (JPY) to Russian Ruble (RUB)

**Art with Kandinsky**: Convert text into images with Kandinsky. You may draw any picture you like, 
except violent or restricted ones.

**Video to MP3 converter**: You can send your up to 30 seconds video to get the audiofile from it.

**Calculator and Metric Conversion**: Perform calculations and convert between metric types 
(e.g., Fahrenheit to Celsius).

**Games**: Play games such as "Rock, Paper, Scissors", memory games as "Five Cats", BlockMe!, Blackjack, and dice games, 
along with various emoji-based games.

## Installation

To install the necessary dependencies, here are the required libraries:

```plaintext
aiofiles==23.2.1
aiogram==3.5.0
aiohttp==3.9.5
aiosignal==1.3.1
annotated-types==0.6.0
anyio==4.3.0
async-timeout==4.0.3
attrs==23.2.0
certifi==2024.2.2
charset-normalizer==3.3.2
colorama==0.4.6
decorator==4.4.2
exceptiongroup==1.2.1
frozenlist==1.4.1
h11==0.14.0
httpcore==1.0.5
httpx==0.27.0
idna==3.7
imageio==2.34.1
imageio-ffmpeg==0.4.9
magic-filter==1.0.12
moviepy==1.0.3
multidict==6.0.5
numpy==1.26.4
proglog==0.1.10
pydantic==2.7.1
pydantic-settings==2.2.1
pydantic_core==2.18.2
python-dotenv==1.0.1
pytz==2024.1
requests==2.31.0
sniffio==1.3.1
tqdm==4.66.2
typing_extensions==4.11.0
urllib3==2.2.1
yarl==1.9.4
```
## .env Sample
For tokens and other data use .env:

```commandline
BOT_TOKEN=your_telegram_bot_token
WEATHER_API_TOKEN=your_weather_api_token
NASA_API_TOKEN=your_nasa_api_token
OPEN_EXCHANGE_TOKEN=your_open_exchange_token
YANDEX_ID_ADMIN=your_yandex_admin_id
YANDEX_API_KEY=your_yandex_api_token
FUSION_BRAIN_TOKEN=your_fusion_brain_token
FB_KEY=your_fusion_brain_key
```


Feel free to interact with MiuMiu and explore its current functionalities.
Stay tuned for updates and new features as we continue to enhance its capabilities! 🚀

## 📦 Команды для управления

### Построить:
```bash
docker compose build
```

### Запустить:
```bash
docker compose up -d
```

Логи:
```bash
docker compose logs -f fastapi
docker compose logs -f webhook-bot
```

Остановить:
```bash
docker compose down
```
