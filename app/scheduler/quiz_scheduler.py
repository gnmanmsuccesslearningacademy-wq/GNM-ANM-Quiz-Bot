import asyncio
from datetime import datetime, timedelta
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import GROUP_ID
from app.database.models import get_all_quiz_schedules, update_quiz_status, delete_quiz_schedule, get_quiz_leaderboard


async def check_and_announce_quizzes(bot: Bot):
    """Check for scheduled quizzes and announce them in the group"""
    
    while True:
        try:
            quizzes = await get_all_quiz_schedules()
            current_time = datetime.now()
            
            for quiz in quizzes:
                quiz_id, quiz_name, exam, date, time_str, duration, question_limit, status = quiz
                
                # Parse schedule datetime
                try:
                    schedule_datetime = datetime.strptime(f"{date} {time_str}", "%Y-%m-%d %H:%M")
                except ValueError:
                    continue
                
                end_datetime = schedule_datetime + timedelta(minutes=duration)
                
                if status == 'pending':
                    if schedule_datetime <= current_time < end_datetime:
                        await announce_quiz_to_group(bot, quiz_id, quiz_name, duration, question_limit)
                        await update_quiz_status(quiz_id, 'active')
                    elif current_time >= end_datetime:
                        await update_quiz_status(quiz_id, 'ended')
                elif status == 'active':
                    if current_time >= end_datetime:
                        await announce_quiz_leaderboard(bot, quiz_id, quiz_name)
                        await delete_quiz_schedule(quiz_id)
            
            await asyncio.sleep(30)
        except Exception as e:
            print(f"Scheduler error: {e}")
            await asyncio.sleep(30)


async def announce_quiz_to_group(bot: Bot, quiz_id: int, quiz_name: str, duration: int, question_limit: int):
    """Announce quiz in the group"""
    
    if not GROUP_ID or GROUP_ID == 0:
        print(f"GROUP_ID not configured. Cannot announce quiz {quiz_id}")
        return
    
    text = f"""📢 **GNM/ANM Daily Live Quiz**

আজকের Quiz শুরু হয়েছে।

📝 Quiz: {quiz_name}
⏱ Duration: {duration} minutes
📊 Questions: {question_limit}

👇 নিচের Button-এ Click করুন
"""
    
    button = InlineKeyboardButton(
        text="🚀 Start Quiz",
        url=f"https://t.me/GNM_ANM_SLA_Quiz_Bot?start=quiz_{quiz_id}"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[[button]])
    
    try:
        await bot.send_message(
            chat_id=GROUP_ID,
            text=text,
            reply_markup=kb,
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Failed to announce quiz in group: {e}")


async def announce_quiz_leaderboard(bot: Bot, quiz_id: int, quiz_name: str):
    """Send final top 10 leaderboard to the group"""
    
    if not GROUP_ID or GROUP_ID == 0:
        print(f"GROUP_ID not configured. Cannot announce leaderboard for quiz {quiz_id}")
        return
    
    leaderboard = await get_quiz_leaderboard(quiz_id, limit=10)
    
    if not leaderboard:
        text = f"🏆 **{quiz_name} Result**\n\nNo quiz submissions were received." 
    else:
        text = f"🏆 **{quiz_name} Result**\n\n"
        for idx, (_, name, corr, wrg, scr) in enumerate(leaderboard, 1):
            if idx == 1:
                medal = "🥇"
            elif idx == 2:
                medal = "🥈"
            elif idx == 3:
                medal = "🥉"
            else:
                medal = f"{idx}."
            text += f"{medal} {name} - {scr}\n"
    
    try:
        await bot.send_message(
            chat_id=GROUP_ID,
            text=text,
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Failed to announce leaderboard in group: {e}")
