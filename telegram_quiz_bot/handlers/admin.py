import os
import tempfile
import uuid
from datetime import datetime, timedelta

import pytz
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import TelegramError
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from config import EXTRA_ADMIN_IDS, TIMEZONE
from database import QuizDB
from parser import parse_quiz_text, read_text_from_file
from quiz_runtime import POLL_OPEN_PERIOD_MAX, POLL_OPEN_PERIOD_MIN

db = QuizDB()
TZ = pytz.timezone(TIMEZONE)

(
    SELECT_GROUP,
    WAITING_FILE,
    WAITING_NAME,
    WAITING_START,
    WAITING_QTIME,
    WAITING_REMINDER,
    WAITING_MARKS,
    WAITING_NEGATIVE,
    CONFIRM,
) = range(9)

FILE_INSTRUCTIONS = (
    "Upload the question file (.txt or .docx). Each question looks like this:\n\n"
    "Question: SI unit of electric current is\n"
    "(a) Volt\n(b) Ohm\n(c) Ampere\n(d) Watt\n"
    "Answer: c\n\n"
    "Notes:\n"
    "• You can use 2, 4, 5, or any number of options — not limited to a–d.\n"
    "• For a question with more than one correct answer, list them "
    "comma-separated, e.g. Answer: c,a\n"
    "• I number the questions myself — no need to number them in the file.\n\n"
    "Send /cancel anytime to abort."
)


async def _is_admin_of(context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int) -> bool:
    if user_id in EXTRA_ADMIN_IDS:
        return True
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
    except TelegramError:
        return False
    return member.status in ("administrator", "creator")


async def createquiz_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == "private":
        all_groups = db.list_groups()
        eligible = [g for g in all_groups if await _is_admin_of(context, g["chat_id"], user.id)]

        if not eligible:
            await update.message.reply_text(
                "I couldn't find any group where you're an admin and I'm already a member.\n\n"
                "1) Add me to your group\n"
                "2) Make me a group admin\n"
                "3) Make sure YOU are also a group admin\n"
                "4) Come back here and send /createquiz again"
            )
            return ConversationHandler.END

        context.user_data["new_quiz"] = {}
        buttons = [
            [InlineKeyboardButton(g["title"] or str(g["chat_id"]), callback_data=f"select_group:{g['chat_id']}")]
            for g in eligible
        ]
        await update.message.reply_text(
            "Which group is this quiz for?\n(Everything from here on stays private — "
            "students won't see the file or setup.)",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        return SELECT_GROUP

    if chat.type in ("group", "supergroup"):
        if not await _is_admin_of(context, chat.id, user.id):
            await update.message.reply_text("Only group admins can create a quiz.")
            return ConversationHandler.END

        db.upsert_group(chat.id, chat.title)  # backfill for the private picker later

        context.user_data["new_quiz"] = {"chat_id": chat.id, "chat_title": chat.title}
        await update.message.reply_text(
            "⚠️ Heads up: setting up the quiz here means everyone in this group can see the "
            "question file and answers as you upload them.\n\n"
            "For a private setup instead, message me directly (DM) and send /createquiz there.\n\n"
            "Continuing here for now.\n\nStep 1/7: " + FILE_INSTRUCTIONS
        )
        return WAITING_FILE

    return ConversationHandler.END


async def select_group_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = int(query.data.split(":", 1)[1])
    user_id = update.effective_user.id

    if not await _is_admin_of(context, chat_id, user_id):
        await query.edit_message_text("You're no longer an admin of that group.")
        return ConversationHandler.END

    group = next((g for g in db.list_groups() if g["chat_id"] == chat_id), None)
    title = group["title"] if group else str(chat_id)

    context.user_data["new_quiz"] = {"chat_id": chat_id, "chat_title": title}

    await query.edit_message_text(f"Target group: {title}\n\nStep 1/7: " + FILE_INSTRUCTIONS)
    return WAITING_FILE


async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc:
        await update.message.reply_text("Please upload a .txt or .docx file.")
        return WAITING_FILE

    fname = doc.file_name.lower()
    if not (fname.endswith(".txt") or fname.endswith(".docx")):
        await update.message.reply_text("Unsupported file type. Please upload a .txt or .docx file.")
        return WAITING_FILE

    tg_file = await doc.get_file()
    tmp_dir = tempfile.mkdtemp()
    local_path = os.path.join(tmp_dir, doc.file_name)
    await tg_file.download_to_drive(local_path)

    text = read_text_from_file(local_path)
    questions, errors = parse_quiz_text(text)

    if not questions:
        msg = "❌ No valid questions could be parsed from that file."
        if errors:
            msg += "\n\nIssues found:\n" + "\n".join(errors[:10])
        msg += "\n\nPlease fix the formatting and upload again."
        await update.message.reply_text(msg)
        return WAITING_FILE

    context.user_data["new_quiz"]["questions"] = questions

    multi_count = sum(1 for q in questions if len(q["correct_indices"]) > 1)
    warn = ""
    if errors:
        warn = f"\n\n⚠️ {len(errors)} question(s) skipped due to formatting issues:\n" + "\n".join(errors[:10])

    await update.message.reply_text(
        f"✅ Parsed {len(questions)} question(s) successfully"
        f"{f' ({multi_count} with multiple correct answers)' if multi_count else ''}.{warn}\n\n"
        "Step 2/7: What should the quiz be called?"
    )
    return WAITING_NAME


async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    if not name:
        await update.message.reply_text("Please send a valid quiz name.")
        return WAITING_NAME

    context.user_data["new_quiz"]["name"] = name
    await update.message.reply_text(
        "Step 3/7: When should the quiz start?\n"
        f"Send it as: YYYY-MM-DD HH:MM (24hr, timezone {TIMEZONE})\n"
        "Or send 'now' to start in ~30 seconds."
    )
    return WAITING_START


async def receive_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    now = datetime.now(TZ)

    if text.lower() == "now":
        start_dt = now + timedelta(seconds=30)
    else:
        try:
            naive = datetime.strptime(text, "%Y-%m-%d %H:%M")
            start_dt = TZ.localize(naive)
        except ValueError:
            await update.message.reply_text(
                "Invalid format. Please send as YYYY-MM-DD HH:MM (e.g. 2026-07-15 18:30) or 'now'."
            )
            return WAITING_START

        if start_dt <= now:
            await update.message.reply_text("Start time must be in the future. Please try again.")
            return WAITING_START

    context.user_data["new_quiz"]["start_time"] = start_dt
    await update.message.reply_text(
        f"Step 4/7: How many seconds should each question stay open for?\n"
        f"Send a number between {POLL_OPEN_PERIOD_MIN} and {POLL_OPEN_PERIOD_MAX} (e.g. 30 or 45). "
        f"This applies to every question in this quiz."
    )
    return WAITING_QTIME


async def receive_qtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text.isdigit() or not (POLL_OPEN_PERIOD_MIN <= int(text) <= POLL_OPEN_PERIOD_MAX):
        await update.message.reply_text(
            f"Please send a whole number of seconds between {POLL_OPEN_PERIOD_MIN} and "
            f"{POLL_OPEN_PERIOD_MAX} — that's Telegram's own limit for how long a poll can stay open."
        )
        return WAITING_QTIME

    q_time = int(text)
    nq = context.user_data["new_quiz"]
    nq["question_time_sec"] = q_time

    # duration_min is only ever used internally now, as a safety-net cutoff
    # in case delivery gets stuck (see scheduler.arm_end_safety_job) — the
    # admin no longer sets it directly. Estimate it from how long the quiz
    # will actually take to run through all its questions.
    num_questions = len(nq["questions"])
    estimated_seconds = num_questions * (q_time + 5)
    nq["duration_min"] = max(1, -(-estimated_seconds // 60))  # ceil division

    await update.message.reply_text(
        "Step 5/7: How many minutes before start should the reminder be sent?\n"
        "Send 0 for no reminder."
    )
    return WAITING_REMINDER


async def receive_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("Please send a valid non-negative number of minutes.")
        return WAITING_REMINDER

    reminder_min = int(text)
    nq = context.user_data["new_quiz"]
    start_dt = nq["start_time"]
    now = datetime.now(TZ)
    reminder_dt = start_dt - timedelta(minutes=reminder_min)

    if reminder_min > 0 and reminder_dt <= now:
        await update.message.reply_text(
            "That reminder time would fall in the past given the start time. "
            "Please send a smaller number, or 0 for no reminder."
        )
        return WAITING_REMINDER

    nq["reminder_min"] = reminder_min
    await update.message.reply_text("Step 6/7: How many marks for each correct answer? (e.g. 1 or 2 or 0.5)")
    return WAITING_MARKS


async def receive_marks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    try:
        marks = float(text)
        if marks <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Please send a valid positive number, e.g. 1 or 2 or 0.5")
        return WAITING_MARKS

    context.user_data["new_quiz"]["marks_per_question"] = marks
    await update.message.reply_text(
        "Step 7/7: Negative marking per wrong answer? Send 0 for none, or e.g. 0.25"
    )
    return WAITING_NEGATIVE


async def receive_negative(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    try:
        negative = float(text)
        if negative < 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Please send a valid number that's 0 or higher, e.g. 0 or 0.25")
        return WAITING_NEGATIVE

    nq = context.user_data["new_quiz"]
    nq["negative_marks"] = negative

    start_dt = nq["start_time"]
    multi_count = sum(1 for q in nq["questions"] if len(q["correct_indices"]) > 1)

    summary = (
        "📋 Quiz Summary\n"
        f"Name: {nq['name']}\n"
        f"Group: {nq['chat_title']}\n"
        f"Questions: {len(nq['questions'])}"
        f"{f' ({multi_count} with multiple correct answers)' if multi_count else ''}\n"
        f"Start: {start_dt.strftime('%Y-%m-%d %H:%M')} ({TIMEZONE})\n"
        f"⏱ {nq['question_time_sec']}s per question (~{nq['duration_min']} min total, estimated)\n"
        f"Reminder: {nq['reminder_min']} min before start\n"
        f"Marks: +{nq['marks_per_question']:g} correct / -{negative:g} wrong\n\n"
        "Confirm creation?"
    )
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Confirm", callback_data="quiz_confirm"),
                InlineKeyboardButton("❌ Cancel", callback_data="quiz_cancel"),
            ]
        ]
    )
    await update.message.reply_text(summary, reply_markup=keyboard)
    return CONFIRM


async def confirm_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "quiz_cancel":
        context.user_data.pop("new_quiz", None)
        await query.edit_message_text("Quiz creation cancelled.")
        return ConversationHandler.END

    nq = context.user_data.pop("new_quiz")
    quiz_id = uuid.uuid4().hex[:10]

    db.create_quiz(
        quiz_id=quiz_id,
        chat_id=nq["chat_id"],
        name=nq["name"],
        start_time=nq["start_time"].isoformat(),
        duration_min=nq["duration_min"],
        reminder_min=nq["reminder_min"],
        marks_per_question=nq["marks_per_question"],
        negative_marks=nq["negative_marks"],
        created_by=update.effective_user.id,
        question_time_sec=nq["question_time_sec"],
    )
    for i, q in enumerate(nq["questions"], start=1):
        db.add_question(quiz_id, i, q["question"], q["options"], q["correct_indices"])

    from scheduler import schedule_quiz_jobs
    schedule_quiz_jobs(context.application, quiz_id)

    await query.edit_message_text(
        f"🎉 Quiz '{nq['name']}' scheduled successfully for {nq['chat_title']}! (ID: {quiz_id})\n"
        f"It will start at {nq['start_time'].strftime('%Y-%m-%d %H:%M')} ({TIMEZONE}).\n\n"
        f"Manage or cancel it anytime with /myquizzes."
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("new_quiz", None)
    await update.message.reply_text("Quiz creation cancelled.")
    return ConversationHandler.END


def get_conversation_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("createquiz", createquiz_start)],
        states={
            SELECT_GROUP: [CallbackQueryHandler(select_group_callback, pattern="^select_group:")],
            WAITING_FILE: [MessageHandler(filters.Document.ALL, receive_file)],
            WAITING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)],
            WAITING_START: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_start)],
            WAITING_QTIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_qtime)],
            WAITING_REMINDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_reminder)],
            WAITING_MARKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_marks)],
            WAITING_NEGATIVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_negative)],
            CONFIRM: [CallbackQueryHandler(confirm_button, pattern="^quiz_(confirm|cancel)$")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )