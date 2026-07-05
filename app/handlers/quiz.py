from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from app.database.models import (
    get_question_by_id,
    get_quiz_session,
    get_random_question,
    next_question,
    start_quiz_session,
    update_score,
)

from app.keyboards.quiz_keyboard import quiz_keyboard

router = Router()


# ==========================
# Common Quiz Function
# ==========================

async def send_quiz(message: Message, start_new: bool = True):

    user_id = message.from_user.id

    if start_new:
        await start_quiz_session(user_id)

    session = await get_quiz_session(user_id)

    if session is None:
        await message.answer("❌ Quiz session could not be started.")
        return

    if session[3] > session[4]:
        await message.answer(
            f"🏁 Quiz Completed!\n\n✅ Your Score: {session[2]}/{session[4]}"
        )
        return

    question = await get_random_question()

    if question is None:
        await message.answer("❌ Database-এ কোনো Question নেই।")
        return

    text = f"""
🎯 Quiz Started

📌 Question {session[3]}/{session[4]}
📚 Subject : {question[2]}
📖 Chapter : {question[3]}

❓ {question[4]}

🅰️ {question[5]}
🅱️ {question[6]}
🇨 {question[7]}
🇩 {question[8]}
"""

    await message.answer(
        text,
        reply_markup=quiz_keyboard(question[0])
    )


# ==========================
# /quiz Command
# ==========================

@router.message(Command("quiz"))
async def quiz_command(message: Message):

    await send_quiz(message)


# ==========================
# Quiz Answer Handler
# ==========================

@router.callback_query(F.data.startswith("answer:"))
async def quiz_answer(callback: CallbackQuery):

    await callback.answer()

    user_id = callback.from_user.id
    data = callback.data.split(":")

    if len(data) < 3:
        await callback.message.answer("❌ Invalid answer selection.")
        return

    selected_option = data[1]
    question_id = int(data[2])

    question = await get_question_by_id(question_id)

    if question is None:
        await callback.message.answer("❌ Question not found.")
        return

    correct_answer = question[9]
    explanation = question[10]

    if selected_option == correct_answer:
        await update_score(user_id)
        feedback = "✅ Correct Answer!"
    else:
        feedback = f"❌ Wrong Answer!\n✅ Correct Answer: {correct_answer}"

    if explanation:
        feedback += f"\n\n💡 Explanation:\n{explanation}"
    else:
        feedback += "\n\n💡 No explanation added for this question."

    await callback.message.answer(feedback)

    await next_question(user_id)

    session = await get_quiz_session(user_id)

    if session is None:
        return

    if session[3] > session[4]:
        await callback.message.answer(
            f"🏁 Quiz Completed!\n\n✅ Your Score: {session[2]}/{session[4]}"
        )
        return

    await send_quiz(callback.message, start_new=False)