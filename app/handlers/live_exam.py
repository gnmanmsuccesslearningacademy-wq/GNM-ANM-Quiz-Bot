from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

from app.database.models import get_scheduled_quizzes, get_questions_by_exam, get_random_question
from app.keyboards.main_menu import get_main_menu

router = Router()


class LiveExamStates(StatesGroup):
    choosing_exam = State()
    exam_active = State()
    exam_paused = State()
    exam_review = State()


@router.message(F.text == "📝 Live Quiz")
async def show_live_exams(message: Message, state: FSMContext):
    """Show available live exams"""
    
    quizzes = await get_scheduled_quizzes()
    
    if not quizzes:
        text = """❌ **NO LIVE EXAMS**

No scheduled exams at the moment.
Check back later!
"""
        await message.answer(text, reply_markup=get_main_menu())
        return
    
    text = """📝 **LIVE EXAMS**

Available exams:
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = []
    for exam_id, name, description, start_time, end_time, total_q, total_marks in quizzes:
        # Parse datetime - handle multiple formats
        try:
            start = datetime.fromisoformat(start_time)
        except ValueError:
            try:
                start = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
            except ValueError:
                continue  # Skip if format is invalid
        
        text += f"\n{name}\n"
        text += f"Questions: {total_q} | Marks: {total_marks}\n"
        text += f"Start: {start.strftime('%Y-%m-%d %H:%M')}\n\n"
        
        buttons.append([InlineKeyboardButton(
            text=f"📖 {name}",
            callback_data=f"exam_{exam_id}"
        )])
    
    buttons.append([InlineKeyboardButton(text="Back", callback_data="exam_back")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("exam_"))
async def join_live_exam(callback_query: CallbackQuery, state: FSMContext):
    """Join a live exam - with time validation"""
    
    exam_id = callback_query.data.split("_")[1]
    
    if exam_id == "back":
        await callback_query.message.delete()
        await callback_query.answer()
        return
    
    # Fetch exam details
    quizzes = await get_scheduled_quizzes()
    exam_data = None
    for quiz in quizzes:
        if str(quiz[0]) == exam_id:
            exam_data = quiz
            break
    
    if not exam_data:
        text = "❌ Exam not found!"
        await callback_query.message.edit_text(text)
        await callback_query.answer()
        return
    
    exam_id, exam_name, description, start_time, end_time, total_q, total_marks = exam_data
    
    # Parse times
    try:
        start_dt = datetime.fromisoformat(start_time)
    except ValueError:
        try:
            start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
        except ValueError:
            await callback_query.answer("❌ Invalid exam time format!", show_alert=True)
            return
    
    try:
        end_dt = datetime.fromisoformat(end_time)
    except ValueError:
        try:
            end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M")
        except ValueError:
            await callback_query.answer("❌ Invalid exam time format!", show_alert=True)
            return
    
    current_time = datetime.now()
    
    # ✅ TIME VALIDATION - Check if exam is available now
    if current_time < start_dt:
        # Exam hasn't started yet
        wait_time = (start_dt - current_time).total_seconds() / 60
        text = f"""⏰ **EXAM NOT STARTED YET**

Exam: {exam_name}
📍 Scheduled Start: {start_dt.strftime('%Y-%m-%d %H:%M')}

⏳ Exam will be available in {int(wait_time)} minutes

Please try again at the scheduled time!
"""
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        buttons = [[InlineKeyboardButton(text="Back", callback_data="exam_back")]]
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback_query.message.edit_text(text, reply_markup=kb)
        await callback_query.answer()
        return
    
    if current_time > end_dt:
        # Exam has ended
        text = f"""❌ **EXAM ENDED**

Exam: {exam_name}
📍 Scheduled End: {end_dt.strftime('%Y-%m-%d %H:%M')}

Sorry! The exam time has passed.
You cannot take this exam anymore.
"""
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        buttons = [[InlineKeyboardButton(text="Back", callback_data="exam_back")]]
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback_query.message.edit_text(text, reply_markup=kb)
        await callback_query.answer()
        return
    
    # ✅ Exam is active - allow student to join
    # Fetch questions for this exam
    questions = await get_questions_by_exam(exam_name, limit=total_q)
    
    if not questions:
        text = f"""❌ **NO QUESTIONS AVAILABLE**

Exam: {exam_name}
This exam has no questions yet.
The admin needs to upload questions first.
"""
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        buttons = [[InlineKeyboardButton(text="Back", callback_data="exam_back")]]
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback_query.message.edit_text(text, reply_markup=kb)
        await callback_query.answer()
        return
    
    # Calculate exam duration in seconds
    exam_duration_seconds = int((end_dt - start_dt).total_seconds())
    
    # Store exam info in state with time tracking
    await state.update_data(
        exam_id=exam_id,
        exam_name=exam_name,
        questions=questions,
        current_question_index=0,
        questions_answered=0,
        score=0,
        user_answers={},
        user_start_time=datetime.now().isoformat(),  # When student started
        quiz_start_time=start_time,  # Scheduled start time
        quiz_end_time=end_time,  # Scheduled end time
        exam_duration_seconds=exam_duration_seconds  # Total duration in seconds
    )
    
    # Display first question
    await show_question(callback_query, state)


async def auto_submit_exam(callback_query: CallbackQuery, state: FSMContext):
    """Auto-submit exam when time is up"""
    
    data = await state.get_data()
    score = data.get('score', 0)
    answered = data.get('questions_answered', 0)
    total = len(data.get('questions', []))
    
    text = f"""⏰ **TIME'S UP! EXAM SUBMITTED**

Time has expired. Your exam has been automatically submitted.

📊 Final Score: {score}
✅ Questions Answered: {answered}/{total}

Thank you for taking the exam!
"""
    
    await state.clear()
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = [[InlineKeyboardButton(text="Back to Menu", callback_data="exam_back")]]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=kb)
    await callback_query.answer("⏰ Exam time expired!")


async def show_question(callback_query: CallbackQuery, state: FSMContext):
    """Display current question"""
    
    data = await state.get_data()
    questions = data.get('questions', [])
    current_idx = data.get('current_question_index', 0)
    
    if current_idx >= len(questions):
        # Exam finished
        text = f"""✅ **EXAM COMPLETED**

Score: {data.get('score', 0)}
Questions Answered: {data.get('questions_answered', 0)}
"""
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        buttons = [[InlineKeyboardButton(text="Back to Menu", callback_data="exam_back")]]
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback_query.message.edit_text(text, reply_markup=kb)
        await callback_query.answer("✅ Exam submitted!")
        return
    
    question_data = questions[current_idx]
    question_id = question_data[0]
    question_text = question_data[4]
    option_a = question_data[5]
    option_b = question_data[6]
    option_c = question_data[7]
    option_d = question_data[8]
    marks = question_data[12]
    
    # Calculate time remaining
    quiz_end_time = data.get('quiz_end_time')
    time_remaining_text = ""
    
    if quiz_end_time:
        try:
            end_dt = datetime.fromisoformat(quiz_end_time)
        except ValueError:
            try:
                end_dt = datetime.strptime(quiz_end_time, "%Y-%m-%d %H:%M")
            except ValueError:
                end_dt = None
        
        if end_dt:
            current_time = datetime.now()
            if current_time < end_dt:
                remaining_seconds = int((end_dt - current_time).total_seconds())
                minutes = remaining_seconds // 60
                seconds = remaining_seconds % 60
                time_remaining_text = f"\n⏱️ Time Remaining: {minutes}m {seconds}s"
            else:
                # Time is up - auto submit
                await auto_submit_exam(callback_query, state)
                return
    
    text = f"""🎯 **LIVE EXAM**

📊 Progress: {current_idx + 1}/{len(questions)}
Score: {data.get('score', 0)}{time_remaining_text}

━━━━━━━━━━━━━━━━━

📝 **Question {current_idx + 1}**

{question_text}

A) {option_a}
B) {option_b}
C) {option_c}
D) {option_d}
"""
    
    await state.set_state(LiveExamStates.exam_active)
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = [
        [InlineKeyboardButton(text="A", callback_data=f"ans_A_{question_id}"),
         InlineKeyboardButton(text="B", callback_data=f"ans_B_{question_id}")],
        [InlineKeyboardButton(text="C", callback_data=f"ans_C_{question_id}"),
         InlineKeyboardButton(text="D", callback_data=f"ans_D_{question_id}")],
        [InlineKeyboardButton(text="⏩ Skip", callback_data="next_question"),
         InlineKeyboardButton(text="⏸️ Pause", callback_data="exam_pause")],
        [InlineKeyboardButton(text="🚪 Exit Exam", callback_data="exam_exit")]
    ]
    
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=kb)
    if current_idx == 0:
        await callback_query.answer("🚀 Exam started! Answer questions carefully.")
    else:
        await callback_query.answer()


@router.callback_query(F.data.startswith("ans_"))
async def answer_question(callback_query: CallbackQuery, state: FSMContext):
    """Handle answer selection - with time validation"""
    
    data = await state.get_data()
    
    # Check if time is up
    quiz_end_time = data.get('quiz_end_time')
    if quiz_end_time:
        try:
            end_dt = datetime.fromisoformat(quiz_end_time)
        except ValueError:
            try:
                end_dt = datetime.strptime(quiz_end_time, "%Y-%m-%d %H:%M")
            except ValueError:
                end_dt = None
        
        if end_dt:
            current_time = datetime.now()
            if current_time >= end_dt:
                # Time is up - auto submit
                await auto_submit_exam(callback_query, state)
                return
    
    parts = callback_query.data.split("_")
    user_answer = parts[1]
    question_id = int(parts[2])
    
    questions = data.get('questions', [])
    current_idx = data.get('current_question_index', 0)
    
    if current_idx < len(questions):
        question_data = questions[current_idx]
        correct_answer = question_data[9]
        marks = question_data[12]
        
        # Check if correct
        is_correct = (user_answer == correct_answer)
        score = marks if is_correct else 0
        
        # Store answer
        user_answers = data.get('user_answers', {})
        user_answers[question_id] = user_answer
        
        # Update state
        await state.update_data(
            user_answers=user_answers,
            current_question_index=current_idx + 1,
            questions_answered=data.get('questions_answered', 0) + 1,
            score=data.get('score', 0) + score
        )
        
        # Show feedback
        feedback = "✅ Correct!" if is_correct else "❌ Wrong!"
        await callback_query.answer(feedback, show_alert=False)
    
    # Move to next question
    data = await state.get_data()
    if data.get('current_question_index', 0) >= len(questions):
        await show_question(callback_query, state)
    else:
        await show_question(callback_query, state)


@router.callback_query(F.data == "next_question")
async def skip_question(callback_query: CallbackQuery, state: FSMContext):
    """Skip to next question - with time validation"""
    
    data = await state.get_data()
    
    # Check if time is up
    quiz_end_time = data.get('quiz_end_time')
    if quiz_end_time:
        try:
            end_dt = datetime.fromisoformat(quiz_end_time)
        except ValueError:
            try:
                end_dt = datetime.strptime(quiz_end_time, "%Y-%m-%d %H:%M")
            except ValueError:
                end_dt = None
        
        if end_dt:
            current_time = datetime.now()
            if current_time >= end_dt:
                # Time is up - auto submit
                await auto_submit_exam(callback_query, state)
                return
    
    await state.update_data(
        current_question_index=data.get('current_question_index', 0) + 1
    )
    
    await show_question(callback_query, state)


@router.callback_query(F.data == "exam_exit")
async def exit_exam(callback_query: CallbackQuery, state: FSMContext):
    """Exit and submit exam"""
    
    data = await state.get_data()
    score = data.get('score', 0)
    answered = data.get('questions_answered', 0)
    total = len(data.get('questions', []))
    
    text = f"""📋 **EXAM SUBMITTED**

Final Score: {score}
Questions Answered: {answered}/{total}

Thank you for taking the exam!
"""
    
    await state.clear()
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = [[InlineKeyboardButton(text="Back to Menu", callback_data="exam_back")]]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=kb)
    await callback_query.answer("✅ Exam submitted successfully!")


@router.callback_query(F.data == "exam_pause")
async def pause_exam(callback_query: CallbackQuery, state: FSMContext):
    """Pause the exam"""
    
    data = await state.get_data()
    current_idx = data.get('current_question_index', 0)
    total = len(data.get('questions', []))
    score = data.get('score', 0)
    answered = data.get('questions_answered', 0)
    
    await state.set_state(LiveExamStates.exam_paused)
    
    text = f"""⏸️ **EXAM PAUSED**

Current Status:
📊 Progress: {current_idx}/{total}
✅ Answered: {answered}
📈 Score: {score}

Your exam is paused. You can resume from where you left off.
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = [
        [InlineKeyboardButton(text="▶️ Resume Exam", callback_data="exam_resume")],
        [InlineKeyboardButton(text="🚪 Exit Exam", callback_data="exam_exit")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=kb)
    await callback_query.answer("⏸️ Exam paused successfully!")


@router.callback_query(F.data == "exam_resume")
async def resume_exam(callback_query: CallbackQuery, state: FSMContext):
    """Resume the paused exam"""
    
    await state.set_state(LiveExamStates.exam_active)
    await show_question(callback_query, state)
    await callback_query.answer("▶️ Exam resumed!")




@router.callback_query(F.data == "exam_back")
async def go_back_menu(callback_query: CallbackQuery, state: FSMContext):
    """Go back to main menu"""
    await callback_query.message.delete()
    await callback_query.answer()
    await state.clear()
    """View live exam leaderboard"""
    
    text = """🏆 **EXAM LEADERBOARD**

1. 🥇 John - 50/50 (100%)
2. 🥈 YOU - 45/50 (90%)
3. 🥉 Sarah - 42/50 (84%)
4. Mike - 40/50 (80%)
5. Lisa - 38/50 (76%)

...
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = [[InlineKeyboardButton(text="Back", callback_data="exam_home")]]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=kb)
    await callback_query.answer()


@router.callback_query(F.data == "exam_home")
async def exam_home(callback_query: CallbackQuery, state: FSMContext):
    """Go back to home"""
    
    await state.clear()
    await callback_query.message.delete()
    await callback_query.answer()


import asyncio
