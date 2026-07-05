from aiogram.fsm.state import StatesGroup, State


class UploadQuestions(StatesGroup):

    waiting_for_exam = State()
    waiting_for_subject = State()
    waiting_for_chapter = State()
    waiting_for_marks = State()
    waiting_for_negative = State()
    waiting_for_file = State()