from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from app.database.models import (
    add_user,
    get_quiz_schedule_by_id,
    get_questions_by_exam,
    save_quiz_result,
    save_quiz_history,
    get_user_quiz_result,
    update_user_stats,
    get_quiz_leaderboard,
    update_quiz_status
)

from app.database.models import add_quiz_session
from app.keyboards.contact import get_contact_keyboard
from app.keyboards.main_menu import get_main_menu
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from datetime import datetime, timedelta

router = Router()


class SimpleQuizStates(StatesGroup):
    quiz_active = State()


@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    """Handle /start command with optional quiz parameter"""
    
    await add_user(
        message.from_user.id,
        message.from_user.full_name,
        message.from_user.username,
    )
    
    # Check if this is a quiz start
    args = message.text.split()
    
    if len(args) > 1 and args[1].startswith("quiz_"):
        # Quiz deep link
        quiz_id_str = args[1].replace("quiz_", "")
        
        try:
            quiz_id = int(quiz_id_str)
        except ValueError:
            await message.answer("❌ Invalid quiz ID!", reply_markup=get_main_menu())
            return
        
        # Fetch quiz details
        quiz = await get_quiz_schedule_by_id(quiz_id)
        
        if not quiz:
            await message.answer("❌ Quiz not found!", reply_markup=get_main_menu())
            return
        
        quiz_id, quiz_name, exam, date, time_str, duration, reminder_minutes, question_limit, status, group_message_id = quiz
        
        # Check quiz window
        schedule_datetime = datetime.strptime(f"{date} {time_str}", "%Y-%m-%d %H:%M")
        end_datetime = schedule_datetime + timedelta(minutes=duration)
        now = datetime.now()
        
        if now < schedule_datetime:
            await message.answer(
                f"⏳ Quiz has not started yet. Start time: {schedule_datetime.strftime('%Y-%m-%d %H:%M')}",
                reply_markup=get_main_menu()
            )
            return
            return
        
        if now >= end_datetime:
            await message.answer(
                "❌ This quiz has already finished.",
                reply_markup=get_main_menu()
            )
            return
        
        if status == 'pending' and schedule_datetime <= now < end_datetime:
            await update_quiz_status(quiz_id, 'active')
        
        # Check if user already submitted
        existing_result = await get_user_quiz_result(quiz_id, message.from_user.id)
        if existing_result:
            correct, wrong, score, submitted_at = existing_result
            await message.answer(
                f"✅ আপনি ইতিমধ্যেই এই Quiz সম্পন্ন করেছেন।\n\nCorrect: {correct}\nWrong: {wrong}\nScore: {score}\nSubmitted: {submitted_at}",
                reply_markup=get_main_menu()
            )
            return
        
        # Fetch questions for this quiz
        questions = await get_questions_by_exam(exam, limit=question_limit)

        if not questions and quiz_name and quiz_name != exam:
            questions = await get_questions_by_exam(quiz_name, limit=question_limit)

        if not questions:
            await message.answer(
                f"❌ No questions available for this quiz!\nScheduled exam key: {exam}\nQuiz name: {quiz_name}\nPlease check the scheduled exam name or reschedule with a valid exam name.",
                reply_markup=get_main_menu()
            )
            return
        
        # Store quiz info in state
        # Create DB quiz session for tracking
        session_id = await add_quiz_session(
            message.from_user.id,
            quiz_id,
            total_question=question_limit,
            exam=exam,
            quiz_type='scheduled'
        )

        await state.update_data(
            quiz_id=quiz_id,
            quiz_name=quiz_name,
            exam=exam,
            questions=questions,
            current_question_index=0,
            correct=0,
            wrong=0,
            user_answers={},
            start_time=schedule_datetime.isoformat(),
            end_time=end_datetime.isoformat(),
            session_id=session_id
        )
        
        await state.set_state(SimpleQuizStates.quiz_active)
        
        # Show first question
        await show_question(message, state)
        return
    
    # Regular start message
    name = message.from_user.full_name or message.from_user.first_name or "Student"

    text = f"""🎉 Welcome {name}

📚 GNM / ANM Success Learning Academy
"""

    if message.chat.type == "private":
        text += "\n📱 প্রথমে আপনার মোবাইল নম্বর Verify করুন।\n\nনিচের \"📱 Share Contact\" বাটনে চাপুন।"
        await message.answer(text, reply_markup=get_contact_keyboard())
    else:
        text += "\n\nএই bot-এর সাথে private chat-এ কথা বলুন: @GNM_ANM_SLA_Quiz_Bot"
        await message.answer(text)


async def show_question(message: Message, state: FSMContext):
    """Display current question"""
    
    data = await state.get_data()
    questions = data.get('questions', [])
    current_idx = data.get('current_question_index', 0)
    end_time_str = data.get('end_time')
    
    if end_time_str:
        end_time = datetime.fromisoformat(end_time_str)
        if datetime.now() >= end_time:
            await message.answer("⏱️ Quiz time is over. Submitting your answers...")
            await show_results(message, state)
            return
    
    if current_idx >= len(questions):
        # Quiz finished
        await show_results(message, state)
        return
    
    question_data = questions[current_idx]
    question_id = question_data[0]
    question_text = question_data[4]
    option_a = question_data[5]
    option_b = question_data[6]
    option_c = question_data[7]
    option_d = question_data[8]
    marks = question_data[12]
    
    text = f"""🎯 **QUIZ**

📊 Progress: {current_idx + 1}/{len(questions)}
✅ Correct: {data.get('correct', 0)}
❌ Wrong: {data.get('wrong', 0)}

━━━━━━━━━━━━━━━━━

📝 **Question {current_idx + 1}**

{question_text}

A) {option_a}
B) {option_b}
C) {option_c}
D) {option_d}
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = [
        [InlineKeyboardButton(text="A", callback_data=f"sq_ans_A_{question_id}"),
         InlineKeyboardButton(text="B", callback_data=f"sq_ans_B_{question_id}")],
        [InlineKeyboardButton(text="C", callback_data=f"sq_ans_C_{question_id}"),
         InlineKeyboardButton(text="D", callback_data=f"sq_ans_D_{question_id}")],
    ]
    
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("sq_ans_"))
async def answer_question(callback_query: CallbackQuery, state: FSMContext):
    """Handle answer selection"""
    
    parts = callback_query.data.split("_")
    user_answer = parts[2]
    question_id = int(parts[3])
    
    data = await state.get_data()
    questions = data.get('questions', [])
    current_idx = data.get('current_question_index', 0)
    end_time_str = data.get('end_time')

    if end_time_str and datetime.now() >= datetime.fromisoformat(end_time_str):
        await callback_query.answer("⏱️ Time is over. Submitting result.", show_alert=False)
        await show_results(callback_query.message, state)
        return
    
    if current_idx < len(questions):
        question_data = questions[current_idx]
        correct_answer = question_data[9]
        marks = question_data[12]
        
        # Check if correct
        is_correct = (user_answer == correct_answer)
        
        # Update state
        new_correct = data.get('correct', 0) + (1 if is_correct else 0)
        new_wrong = data.get('wrong', 0) + (0 if is_correct else 1)
        
        user_answers = data.get('user_answers', {})
        user_answers[question_id] = user_answer
        
        await state.update_data(
            user_answers=user_answers,
            current_question_index=current_idx + 1,
            correct=new_correct,
            wrong=new_wrong
        )
        
        # Show feedback
        feedback = "✅ Correct!" if is_correct else "❌ Wrong!"
        await callback_query.answer(feedback, show_alert=False)
    
    # Move to next question
    await show_question(callback_query.message, state)


async def show_results(message: Message, state: FSMContext):
    """Show quiz results and save to database"""
    
    data = await state.get_data()
    quiz_id = data.get('quiz_id')
    user_id = message.from_user.id
    correct = data.get('correct', 0)
    wrong = data.get('wrong', 0)
    
    # Calculate score
    questions = data.get('questions', [])
    positive_score = 0.0
    negative_score = 0.0
    for question in questions:
        q_id = question[0]
        marks = float(question[12] or 0)
        negative = float(question[13] or 0)
        
        if q_id in data.get('user_answers', {}):
            correct_answer = question[9]
            user_answer = data['user_answers'][q_id]
            
            if user_answer == correct_answer:
                positive_score += marks
            else:
                negative_score += negative

    final_score = round(positive_score + negative_score, 2)
    accuracy = round((positive_score / max(1, len(questions))) * 100, 2)

    # Save result to database
    await save_quiz_result(quiz_id, user_id, correct, wrong, final_score)
    await save_quiz_history(user_id, quiz_id, final_score, positive_score, accuracy)
    await update_user_stats(user_id, correct, wrong, final_score)

    text = f"""🎉 **QUIZ COMPLETED**

✅ Correct: {correct}
❌ Wrong: {wrong}
📊 Score: {positive_score:.2f}
➖ Negative: {negative_score:.2f}
🟰 Final: {final_score:.2f}

Your result is saved. Group leaderboard will update after quiz ends.
"""
    
    await state.clear()
    await message.answer(text, reply_markup=get_main_menu())