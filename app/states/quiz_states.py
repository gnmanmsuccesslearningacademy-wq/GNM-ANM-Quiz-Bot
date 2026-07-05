from aiogram.fsm.state import State, StatesGroup


class QuizStates(StatesGroup):
    """States for quiz flow"""
    choosing_quiz_type = State()
    choosing_subject = State()
    choosing_chapter = State()
    choosing_difficulty = State()
    quiz_active = State()
    quiz_review = State()


class AdminStates(StatesGroup):
    """States for admin operations"""
    uploading_questions = State()
    sending_broadcast = State()
    managing_users = State()
    publishing_notice = State()


class UserStates(StatesGroup):
    """States for user operations"""
    editing_profile = State()
    viewing_stats = State()
