import os

# Valid Telegram token *shape* (not a real secret) so aiogram validators don't explode on import.
os.environ.setdefault("BOT_TOKEN", "123456789:AAFakeTokenForUnitTestsOnly_xxxxxxxxxxxx")
os.environ.setdefault("BOT_MODE", "polling")
os.environ.setdefault("LEONARDO_API_KEY", "")

import config  # noqa: E402

config.clear_settings_cache()
config.settings = config.get_settings()
