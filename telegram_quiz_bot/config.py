import os
from dotenv import load_dotenv

load_dotenv()

# Get this from @BotFather on Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Optional: comma separated Telegram user IDs that are always treated as
# quiz admins (in addition to actual group admins), e.g. "111111,222222"
EXTRA_ADMIN_IDS = set(
    int(x) for x in os.getenv("EXTRA_ADMIN_IDS", "").split(",") if x.strip().isdigit()
)

DB_PATH = os.getenv("DB_PATH", "quizbot.db")

# Timezone used for parsing/displaying quiz start times (IANA tz name)
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")

# How long (seconds) each question stays open before the bot reveals the
# answer and moves on to the next one. This is what actually paces question
# delivery now — "duration_min" on a quiz is only used as a rough safety-net
# cutoff, not the real clock.
QUESTION_TIME_SECONDS = int(os.getenv("QUESTION_TIME_SECONDS", "20"))