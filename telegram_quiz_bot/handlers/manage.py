import os
import tempfile
from datetime import datetime

import pytz
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from config import TIMEZONE
from database import QuizDB
from parser import parse_quiz_text, read_text_from_file
from quiz_runtime import POLL_OPEN_PERIOD_MAX, POLL_OPEN_PERIOD_MIN
from scheduler import remove_quiz_jobs, schedule_quiz_jobs

db = QuizDB()
TZ = pytz.timezone(TIMEZONE)

MENU, EDIT_VALUE, EDIT_FILE = range(3)

FIELD_PROMPTS = {
    "name": "Send the new quiz title:",
    "marks": "Send the new marks for each correct answer (e.g. 1 or 2 or 0.5):",
    "negative": "Send the new negative marking value (0 for none, e.g. 0.25):",
    "start_time": "Send the new start time as YYYY-MM-DD HH:MM:",
    "qtime": (
        f"Send the new number of seconds each question should stay open for "
        f"({POLL_OPEN_PERIOD_MIN}-{POLL_OPEN_PERIOD_MAX}):"
    ),
    "reminder": "Send the new reminder time in minutes before start (0 for none):",
}


def _quiz_list_keyboard(quizzes):
    buttons = [
        [InlineKeyboardButton(f"{q['name']} ({q['start_time'][:16]})", callback_data=f"manage:{q['id']}")]
        for q in quizzes
    ]
    buttons.append([InlineKeyboardButton("Close", callback_data="mgmt_close")])
    return InlineKeyboardMarkup(buttons)


def _quiz_detail_keyboard(quiz_id):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✏️ Title", callback_data=f"editfield:{quiz_id}:name"),
                InlineKeyboardButton("✏️ Marks", callback_data=f"editfield:{quiz_id}:marks"),
            ],
            [InlineKeyboardButton("✏️ Negative marking", callback_data=f"editfield:{quiz_id}:negative")],
            [
                InlineKeyboardButton("✏️ Start time", callback_data=f"editfield:{quiz_id}:start_time"),
                InlineKeyboardButton("✏️ Time/question", callback_data=f"editfield:{quiz_id}:qtime"),
            ],
            [InlineKeyboardButton("✏️ Reminder", callback_data=f"editfield:{quiz_id}:reminder")],
            [InlineKeyboardButton("📄 Replace questions", callback_data=f"editquestions:{quiz_id}")],
            [InlineKeyboardButton("🚫 Cancel quiz", callback_data=f"cancelquiz:{quiz_id}")],
            [InlineKeyboardButton("⬅️ Back", callback_data="mgmt_back")],
        ]
    )


async def myquizzes_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        await update.message.reply_text("Please DM me and send /myquizzes there.")
        return ConversationHandler.END

    quizzes = db.list_manageable_quizzes(update.effective_user.id)
    if not quizzes:
        await update.message.reply_text(
            "You have no upcoming (not-yet-started) quizzes to manage."
        )
        return ConversationHandler.END

    await update.message.reply_text("Your upcoming quizzes:", reply_markup=_quiz_list_keyboard(quizzes))
    return MENU


async def _show_detail(query, quiz_id):
    quiz = db.get_quiz(quiz_id)
    if not quiz or quiz["status"] != "scheduled":
        await query.edit_message_text(
            "That quiz is no longer editable (it may have started, ended, or been cancelled)."
        )
        return ConversationHandler.END

    q_count = len(db.get_questions(quiz_id))
    text = (
        f"📋 {quiz['name']}\n"
        f"Questions: {q_count}\n"
        f"Start: {quiz['start_time'][:16]}\n"
        f"⏱ {quiz['question_time_sec']}s per question | Reminder: {quiz['reminder_min']} min before\n"
        f"Marks: +{quiz['marks_per_question']:g} correct / -{quiz['negative_marks']:g} wrong\n\n"
        "What would you like to do?"
    )
    await query.edit_message_text(text, reply_markup=_quiz_detail_keyboard(quiz_id))
    return MENU


async def menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    if data == "mgmt_close":
        await query.edit_message_text("Closed.")
        return ConversationHandler.END

    if data == "mgmt_back":
        quizzes = db.list_manageable_quizzes(update.effective_user.id)
        if not quizzes:
            await query.edit_message_text("You have no upcoming quizzes to manage.")
            return ConversationHandler.END
        await query.edit_message_text("Your upcoming quizzes:", reply_markup=_quiz_list_keyboard(quizzes))
        return MENU

    if data.startswith("manage:"):
        return await _show_detail(query, data.split(":", 1)[1])

    if data.startswith("cancelquiz:"):
        quiz_id = data.split(":", 1)[1]
        quiz = db.get_quiz(quiz_id)
        if not quiz or quiz["status"] != "scheduled":
            await query.edit_message_text("This quiz can no longer be cancelled (it may have already started).")
            return ConversationHandler.END

        remove_quiz_jobs(context.application, quiz_id)
        try:
            await context.bot.send_message(
                quiz["chat_id"], f"🚫 Quiz '{quiz['name']}' has been cancelled by the admin."
            )
        except Exception:
            pass
        db.delete_quiz_data(quiz_id)
        await query.edit_message_text(f"Quiz '{quiz['name']}' cancelled and removed.")
        return ConversationHandler.END

    if data.startswith("editfield:"):
        _, quiz_id, field = data.split(":", 2)
        context.user_data["edit"] = {"quiz_id": quiz_id, "field": field}
        await query.edit_message_text(FIELD_PROMPTS[field])
        return EDIT_VALUE

    if data.startswith("editquestions:"):
        quiz_id = data.split(":", 1)[1]
        context.user_data["edit"] = {"quiz_id": quiz_id}
        await query.edit_message_text(
            "Upload the new question file (.txt or .docx) — this fully replaces the current questions."
        )
        return EDIT_FILE

    return MENU


async def edit_value_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    edit = context.user_data.get("edit")
    if not edit:
        return ConversationHandler.END

    quiz_id, field = edit["quiz_id"], edit["field"]
    text = update.message.text.strip()

    quiz = db.get_quiz(quiz_id)
    if not quiz or quiz["status"] != "scheduled":
        await update.message.reply_text("That quiz is no longer editable.")
        context.user_data.pop("edit", None)
        return ConversationHandler.END

    reschedule = False
    try:
        if field == "name":
            db.update_quiz_field(quiz_id, name=text)
        elif field == "marks":
            value = float(text)
            if value <= 0:
                raise ValueError
            db.update_quiz_field(quiz_id, marks_per_question=value)
        elif field == "negative":
            value = float(text)
            if value < 0:
                raise ValueError
            db.update_quiz_field(quiz_id, negative_marks=value)
        elif field == "start_time":
            naive = datetime.strptime(text, "%Y-%m-%d %H:%M")
            dt = TZ.localize(naive)
            if dt <= datetime.now(TZ):
                await update.message.reply_text("Start time must be in the future. Try again:")
                return EDIT_VALUE
            db.update_quiz_field(quiz_id, start_time=dt.isoformat())
            reschedule = True
        elif field == "qtime":
            value = int(text)
            if not (POLL_OPEN_PERIOD_MIN <= value <= POLL_OPEN_PERIOD_MAX):
                raise ValueError
            db.update_quiz_field(quiz_id, question_time_sec=value)
            # duration_min is only an internal safety-net figure now (see
            # scheduler.arm_end_safety_job) — keep it roughly in sync with
            # however long the quiz will actually take at the new pace.
            num_questions = len(db.get_questions(quiz_id))
            estimated_seconds = num_questions * (value + 5)
            db.update_quiz_field(quiz_id, duration_min=max(1, -(-estimated_seconds // 60)))
            reschedule = True
        elif field == "reminder":
            value = int(text)
            if value < 0:
                raise ValueError
            db.update_quiz_field(quiz_id, reminder_min=value)
            reschedule = True
    except ValueError:
        await update.message.reply_text("That doesn't look valid. Please try again:")
        return EDIT_VALUE

    if reschedule:
        remove_quiz_jobs(context.application, quiz_id)
        schedule_quiz_jobs(context.application, quiz_id)

    await update.message.reply_text("✅ Updated. Send /myquizzes to review your quizzes again.")
    context.user_data.pop("edit", None)
    return ConversationHandler.END


async def edit_file_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    edit = context.user_data.get("edit")
    if not edit:
        return ConversationHandler.END
    quiz_id = edit["quiz_id"]

    doc = update.message.document
    if not doc or not (doc.file_name.lower().endswith(".txt") or doc.file_name.lower().endswith(".docx")):
        await update.message.reply_text("Please upload a .txt or .docx file.")
        return EDIT_FILE

    tg_file = await doc.get_file()
    tmp_dir = tempfile.mkdtemp()
    local_path = os.path.join(tmp_dir, doc.file_name)
    await tg_file.download_to_drive(local_path)

    text = read_text_from_file(local_path)
    questions, errors = parse_quiz_text(text)
    if not questions:
        msg = "❌ No valid questions could be parsed."
        if errors:
            msg += "\n\n" + "\n".join(errors[:10])
        await update.message.reply_text(msg)
        return EDIT_FILE

    db.replace_questions(quiz_id, questions)
    warn = f"\n⚠️ {len(errors)} question(s) skipped due to formatting issues." if errors else ""
    await update.message.reply_text(
        f"✅ Replaced with {len(questions)} question(s).{warn}\n\nSend /myquizzes to review your quizzes again."
    )
    context.user_data.pop("edit", None)
    return ConversationHandler.END


async def cancel_manage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("edit", None)
    await update.message.reply_text("Closed.")
    return ConversationHandler.END


def get_manage_conversation_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("myquizzes", myquizzes_start)],
        states={
            MENU: [CallbackQueryHandler(menu_router)],
            EDIT_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_value_received)],
            EDIT_FILE: [MessageHandler(filters.Document.ALL, edit_file_received)],
        },
        fallbacks=[CommandHandler("cancel", cancel_manage)],
    )