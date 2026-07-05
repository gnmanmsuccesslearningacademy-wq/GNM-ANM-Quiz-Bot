import os

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID
from app.states.upload_state import UploadQuestions
from app.services.importer import import_file

router = Router()


# ==============================
# Shared Upload Function
# ==============================

async def start_upload_process(message: Message, state: FSMContext):
    """Shared function to start upload process"""
    
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Access Denied!")
        return

    await state.clear()

    await state.set_state(UploadQuestions.waiting_for_exam)

    await message.answer(
        "📝 Exam Name লিখুন।\n\n"
        "উদাহরণ:\n"
        "GNM ANM 2027"
    )


# ==============================
# /upload Command
# ==============================

@router.message(Command("upload"))
async def upload_command(message: Message, state: FSMContext):
    """Handle /upload command"""
    
    await start_upload_process(message, state)


# ==============================
# Upload Button Handler
# ==============================

@router.message(F.text == "Upload Questions")
async def upload_questions_button(message: Message, state: FSMContext):
    """Handle Upload Questions button - calls same upload process"""
    
    await start_upload_process(message, state)


# ==============================
# Exam
# ==============================

@router.message(UploadQuestions.waiting_for_exam)
async def get_exam(message: Message, state: FSMContext):

    await state.update_data(exam=message.text)

    await state.set_state(UploadQuestions.waiting_for_subject)

    await message.answer("📚 Subject লিখুন।")


# ==============================
# Subject
# ==============================

@router.message(UploadQuestions.waiting_for_subject)
async def get_subject(message: Message, state: FSMContext):

    await state.update_data(subject=message.text)

    await state.set_state(UploadQuestions.waiting_for_chapter)

    await message.answer("📖 Chapter লিখুন।")


# ==============================
# Chapter
# ==============================

@router.message(UploadQuestions.waiting_for_chapter)
async def get_chapter(message: Message, state: FSMContext):

    await state.update_data(chapter=message.text)

    await state.set_state(UploadQuestions.waiting_for_marks)

    await message.answer("🎯 Marks লিখুন। (যেমন: 1)")


# ==============================
# Marks
# ==============================

@router.message(UploadQuestions.waiting_for_marks)
async def get_marks(message: Message, state: FSMContext):

    try:
        marks = float(message.text)
    except:
        await message.answer("❌ শুধু Number লিখুন।")
        return

    await state.update_data(marks=marks)

    await state.set_state(UploadQuestions.waiting_for_negative)

    await message.answer("➖ Negative Marks লিখুন। (যেমন: 0 অথবা 0.25)")


# ==============================
# Negative Marks
# ==============================

@router.message(UploadQuestions.waiting_for_negative)
async def get_negative(message: Message, state: FSMContext):

    try:
        negative = float(message.text)
    except:
        await message.answer("❌ শুধু Number লিখুন।")
        return

    await state.update_data(negative=negative)

    await state.set_state(UploadQuestions.waiting_for_file)

    await message.answer(
        "📤 এখন Question File পাঠান।\n\n"
        "Supported Format:\n"
        "✅ .xlsx\n"
        "✅ .docx\n"
        "✅ .txt"
    )


# ==============================
# Receive File
# ==============================

@router.message(
    UploadQuestions.waiting_for_file,
    F.document
)
async def receive_file(message: Message, state: FSMContext):

    document = message.document

    file_name = document.file_name.lower()

    if not (
        file_name.endswith(".xlsx")
        or file_name.endswith(".docx")
        or file_name.endswith(".txt")
    ):
        await message.answer(
            "❌ শুধুমাত্র .xlsx / .docx / .txt File Support করে।"
        )
        return

    os.makedirs("downloads", exist_ok=True)

    file_path = f"downloads/{document.file_name}"

    await message.bot.download(
        document,
        destination=file_path
    )

    data = await state.get_data()

    try:

        count = await import_file(

            file_path=file_path,

            exam=data["exam"],

            subject=data["subject"],

            chapter=data["chapter"],

            marks=data["marks"],

            negative=data["negative"]

        )

        await message.answer(
            f"""
✅ Import Successful

📘 Exam : {data['exam']}
📚 Subject : {data['subject']}
📖 Chapter : {data['chapter']}

📝 Questions Imported : {count}
            """
        )

    except Exception as e:

        await message.answer(
            f"❌ Import Failed\n\n{e}"
        )

    await state.clear()


# ==============================
# Non-document Handler (reminder)
# ==============================

@router.message(UploadQuestions.waiting_for_file)
async def non_document_file_reminder(message: Message):
    """Remind user to send a document when they send text in file waiting state"""
    
    await message.answer(
        "📤 শুধুমাত্র Question File পাঠান।\n\n"
        "Supported Format:\n"
        "✅ .xlsx\n"
        "✅ .docx\n"
        "✅ .txt"
    )


# ==============================
# Cancel Upload - Any state
# ==============================

@router.message(F.text == "/cancel")
@router.message(F.text.lower() == "cancel")
async def cancel_upload(message: Message, state: FSMContext):
    """Cancel upload process from any state"""
    
    current_state = await state.get_state()
    
    if current_state and current_state.startswith("UploadQuestions"):
        await state.clear()
        await message.answer(
            "❌ Upload cancelled!\n\n"
            "Type /upload to start again."
        )
    else:
        await message.answer("ℹ️ No active upload process.")