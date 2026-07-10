import logging

import pytz
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    ChatMemberHandler,
    CommandHandler,
    PollAnswerHandler,
)

from config import BOT_TOKEN, TIMEZONE
from database import QuizDB
from handlers.admin import get_conversation_handler
from handlers.manage import get_manage_conversation_handler
from quiz_runtime import handle_poll_answer, handle_ready_click, resume_running_quiz
from scheduler import schedule_quiz_jobs, arm_end_safety_job

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

db = QuizDB()
TZ = pytz.timezone(TIMEZONE)


async def start_cmd(update, context):
    await update.message.reply_text(
        "👋 Hi! I'm a Quiz Bot.\n\n"
        "Add me to a group and make me an admin (I need permission to post messages).\n\n"
        "To keep questions private until the quiz starts, DM me here and send /createquiz — "
        "I'll ask which group to post to, and everything else stays private.\n\n"
        "Commands:\n"
        "/createquiz — create & schedule a quiz\n"
        "/myquizzes — cancel or edit a quiz you haven't started yet\n"
        "/cancel — cancel whatever step you're currently on"
    )


async def track_chats(update, context):
    """Keeps the `groups` table in sync so the private /createquiz picker
    knows which groups the bot currently belongs to."""
    result = update.my_chat_member
    chat = result.chat
    if chat.type not in ("group", "supergroup"):
        return

    new_status = result.new_chat_member.status
    if new_status in ("member", "administrator", "creator"):
        db.upsert_group(chat.id, chat.title)
    elif new_status in ("left", "kicked"):
        db.remove_group(chat.id)


async def _on_startup(application):
    """Re-arm scheduled/ready/running quizzes after a restart so nothing is lost."""
    from quiz_runtime import deliver_quiz_questions

    for quiz in db.get_scheduled_quizzes():
        status = quiz["status"]

        if status == "scheduled":
            schedule_quiz_jobs(application, quiz["id"])

        elif status == "ready_gate":
            # We don't know exactly how many were "ready" pre-restart, but to
            # avoid quizzes getting stuck forever, just deliver question 1 now.
            arm_end_safety_job(application, quiz["id"])
            await deliver_quiz_questions(application, quiz["id"])

        elif status == "running":
            # Questions are posted one at a time by their own timer jobs,
            # which don't survive a restart — pick up right where we left
            # off instead of trying to reconstruct exact remaining time.
            arm_end_safety_job(application, quiz["id"])
            await resume_running_quiz(application, quiz["id"])

    logger.info("Resumed pending quizzes after startup.")


def main():
    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN is not set. Please add it to your .env file.")

    application = Application.builder().token(BOT_TOKEN).post_init(_on_startup).build()

    application.add_handler(CommandHandler("start", start_cmd))
    application.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(get_conversation_handler())
    application.add_handler(get_manage_conversation_handler())
    application.add_handler(CallbackQueryHandler(handle_ready_click, pattern="^ready:"))
    application.add_handler(PollAnswerHandler(handle_poll_answer))

    logger.info("Bot started. Polling for updates...")
    application.run_polling(
        allowed_updates=["message", "callback_query", "my_chat_member", "poll_answer"]
    )


if __name__ == "__main__":
    main()