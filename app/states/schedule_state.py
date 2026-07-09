from aiogram.fsm.state import StatesGroup, State


class QuizScheduleStates(StatesGroup):
    
    waiting_for_name = State()
    waiting_for_exam = State()
    waiting_for_date = State()
    waiting_for_time = State()
    waiting_for_reminder = State()
    waiting_for_duration = State()
    waiting_for_questions = State()
