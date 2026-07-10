from datetime import datetime, timedelta

import pytz

from config import TIMEZONE, QUESTION_TIME_SECONDS
from database import QuizDB

db = QuizDB()
TZ = pytz.timezone(TIMEZONE)


def schedule_quiz_jobs(application, quiz_id):
    """Schedules the reminder / start / end jobs for one quiz.

    Job names are namespaced by quiz_id, so many quizzes — across the same
    group or different groups — can be scheduled independently at the same
    time without clashing.
    """
    quiz = db.get_quiz(quiz_id)
    if not quiz:
        return

    start_dt = datetime.fromisoformat(quiz["start_time"])
    now = datetime.now(TZ)

    # Safety net: if the bot was offline and the start time already passed,
    # kick the quiz off almost immediately instead of silently skipping it.
    if start_dt <= now:
        start_dt = now + timedelta(seconds=5)

    reminder_min = quiz["reminder_min"]
    jq = application.job_queue

    if reminder_min > 0:
        reminder_dt = start_dt - timedelta(minutes=reminder_min)
        if reminder_dt > now:
            jq.run_once(
                _send_reminder,
                when=reminder_dt,
                data={"quiz_id": quiz_id},
                name=f"reminder_{quiz_id}",
            )

    jq.run_once(
        _start_quiz,
        when=start_dt,
        data={"quiz_id": quiz_id},
        name=f"start_{quiz_id}",
    )

    arm_end_safety_job(application, quiz_id, from_dt=start_dt)


def arm_end_safety_job(application, quiz_id, from_dt=None):
    """(Re-)arms the safety-net 'end quiz' job.

    Questions are delivered one at a time, each held open for
    QUESTION_TIME_SECONDS, so the real pacing comes from that per-question
    timer chain — not from `duration_min`. This job only exists as a
    fallback in case that chain gets stuck (e.g. a crash mid-quiz), so it's
    given a generous cushion on top of however long delivering everything
    should actually take. `from_dt` defaults to now, which is what you want
    when re-arming after a restart for a quiz that's already underway.
    """
    quiz = db.get_quiz(quiz_id)
    if not quiz:
        return

    now = datetime.now(TZ)
    from_dt = from_dt or now

    num_questions = len(db.get_questions(quiz_id))
    q_time = quiz.get("question_time_sec") or QUESTION_TIME_SECONDS
    per_question_runtime = num_questions * (q_time + 5)  # +5s reveal pause/margin
    safety_seconds = max(quiz["duration_min"] * 60, per_question_runtime) + 120
    end_dt = from_dt + timedelta(seconds=safety_seconds)
    if end_dt <= now:
        end_dt = now + timedelta(seconds=safety_seconds)

    for job in application.job_queue.get_jobs_by_name(f"end_{quiz_id}"):
        job.schedule_removal()

    application.job_queue.run_once(
        _end_quiz,
        when=end_dt,
        data={"quiz_id": quiz_id},
        name=f"end_{quiz_id}",
    )


def remove_quiz_jobs(application, quiz_id):
    """Cancels any pending reminder/start/end/ready-timeout jobs for a quiz.
    Used when an admin cancels or edits the timing of a scheduled quiz."""
    jq = application.job_queue
    for prefix in ("reminder", "start", "end", "readytimeout"):
        for job in jq.get_jobs_by_name(f"{prefix}_{quiz_id}"):
            job.schedule_removal()


async def _send_reminder(context):
    quiz_id = context.job.data["quiz_id"]
    quiz = db.get_quiz(quiz_id)
    if not quiz or quiz["status"] != "scheduled":
        return

    from database import QuizDB
    questions = QuizDB().get_questions(quiz_id)
    start_dt = datetime.fromisoformat(quiz["start_time"])

    marks_line = f"✅ +{quiz['marks_per_question']:g} per correct"
    if quiz["negative_marks"] > 0:
        marks_line += f"   ❌ -{quiz['negative_marks']:g} per wrong"

    q_time = quiz.get("question_time_sec") or QUESTION_TIME_SECONDS

    await context.bot.send_message(
        chat_id=quiz["chat_id"],
        text=(
            f"⏰ Reminder — '{quiz['name']}' starts in {quiz['reminder_min']} minute(s)!\n\n"
            f"🕒 Start: {start_dt.strftime('%I:%M %p')}\n"
            f"📝 Questions: {len(questions)}\n"
            f"⏱ {q_time}s per question\n"
            f"{marks_line}\n\n"
            f"Get ready — a 'Ready' button will appear here when it's time! 🎯"
        ),
    )


async def _start_quiz(context):
    from quiz_runtime import run_quiz_ready_gate
    await run_quiz_ready_gate(context, context.job.data["quiz_id"])


async def _end_quiz(context):
    from quiz_runtime import run_quiz_end
    await run_quiz_end(context, context.job.data["quiz_id"])