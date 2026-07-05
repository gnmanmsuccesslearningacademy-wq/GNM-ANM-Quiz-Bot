from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID

router = Router()


# Note: /admin command is handled by admin_dashboard.py
# This file only contains the unified upload process