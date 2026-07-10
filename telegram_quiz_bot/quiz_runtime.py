import asyncio
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest, RetryAfter, TimedOut, NetworkError

from config import QUESTION_TIME_SECONDS
from database import QuizDB

logger = logging.getLogger(__name__)

db = QuizDB()

READY_GATE_MIN_USERS = 2     # minimum members who must tap "Ready" to kick off the quiz
READY_GATE_TIMEOUT_SECONDS = 180  # fallback: start anyway after this long even if <2 are ready

# Short pause between the answer reveal and the next question, so the
# reveal doesn't get buried instantly.
REVEAL_PAUSE_SECONDS = 3

# Telegram's own bounds for a poll's open_period (auto-close timer).
POLL_OPEN_PERIOD_MIN = 5
POLL_OPEN_PERIOD_MAX = 600  # 10 minutes


async def _safe_call(coro_func, *args, max_retries=5, retry_on_timeout=True, **kwargs):
    """Calls a python-telegram-bot coroutine, retrying on Telegram's
    flood-control (RetryAfter) — which is always safe to retry, since a 429
    response means Telegram never processed the request — and, optionally,
    on transient network timeouts.

    `retry_on_timeout` should be False for anything that SENDS a new message
    or poll (as opposed to editing/closing one): a timeout there doesn't
    tell us whether the request actually went out, so blindly retrying can
    post the same question/notice twice. For edits/closes it's safe to
    retry either way since those are idempotent.
    """
    last_exc = None
    for attempt in range(max_retries):
        try:
            return await coro_func(*args, **kwargs)
        except RetryAfter as e:
            wait = float(getattr(e, "retry_after", 3)) + 0.5
            logger.warning("Flood control hit, sleeping %.1fs (attempt %d)", wait, attempt + 1)
            await asyncio.sleep(wait)
            last_exc = e
        except (TimedOut, NetworkError) as e:
            if not retry_on_timeout:
                raise
            logger.warning("Transient network error, retrying (attempt %d): %s", attempt + 1, e)
            await asyncio.sleep(2)
            last_exc = e
    try:
        return await coro_func(*args, **kwargs)
    except Exception as e:
        logger.error("Giving up after %d retries: %s", max_retries, e)
        raise last_exc or e


def _question_timer_seconds(quiz):
    """Per-quiz timer set at creation time, falling back to the .env default
    for quizzes created before that setting existed."""
    return quiz.get("question_time_sec") or QUESTION_TIME_SECONDS


def _poll_open_period(q_time):
    """Telegram only accepts an open_period between 5 and 600 seconds for a
    poll's own countdown. Whatever the admin configured gets clamped into
    that range so Telegram can drive the live countdown bar itself."""
    return max(POLL_OPEN_PERIOD_MIN, min(POLL_OPEN_PERIOD_MAX, q_time))


# ---------------- Ready gate ----------------
# (Unrelated to answering questions — still a plain inline button, since
# there's no native Telegram widget for "wait until N people are ready".)

async def run_quiz_ready_gate(context, quiz_id):
    """Posts the 'I'm Ready' button; the quiz only starts once enough members
    have tapped it (or automatically after a timeout)."""
    quiz = db.get_quiz(quiz_id)
    if not quiz or quiz["status"] != "scheduled":
        return

    chat_id = quiz["chat_id"]
    db.update_quiz_status(quiz_id, "ready_gate")

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("✅ I'm Ready (0)", callback_data=f"ready:{quiz_id}")]]
    )
    await _safe_call(
        context.bot.send_message,
        chat_id,
        f"🎯 Quiz '{quiz['name']}' is about to begin!\n"
        f"Tap the button below when you're ready.\n"
        f"The quiz starts once at least {READY_GATE_MIN_USERS} people are ready, "
        f"or automatically in {READY_GATE_TIMEOUT_SECONDS // 60} minute(s).",
        reply_markup=keyboard,
        retry_on_timeout=False,
    )

    context.job_queue.run_once(
        _ready_timeout_job, when=READY_GATE_TIMEOUT_SECONDS,
        data={"quiz_id": quiz_id}, name=f"readytimeout_{quiz_id}",
    )


async def _ready_timeout_job(context):
    await deliver_quiz_questions(context, context.job.data["quiz_id"])


async def handle_ready_click(update, context):
    query = update.callback_query
    quiz_id = query.data.split(":", 1)[1]
    quiz = db.get_quiz(quiz_id)
    if not quiz or quiz["status"] != "ready_gate":
        await query.answer("This quiz has already started or ended.", show_alert=True)
        return

    user = update.effective_user
    db.add_ready_click(quiz_id, user.id)
    count = db.count_ready_clicks(quiz_id)
    await query.answer(f"You're marked ready! ({count} ready)")

    try:
        await _safe_call(
            query.edit_message_reply_markup,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(f"✅ I'm Ready ({count})", callback_data=f"ready:{quiz_id}")]]
            ),
        )
    except Exception:
        pass

    if count >= READY_GATE_MIN_USERS:
        for job in context.job_queue.get_jobs_by_name(f"readytimeout_{quiz_id}"):
            job.schedule_removal()
        await deliver_quiz_questions(context, quiz_id)


# ---------------- Delivering questions (native Telegram polls, one at a time) ----------------

async def deliver_quiz_questions(context, quiz_id):
    """Kicks a quiz off: flips it to 'running' and posts question 1. Every
    question after that is posted by the per-question timer job, not by a
    loop — that's what keeps this safe from Telegram's flood limits and from
    stepping on a concurrently-firing 'end quiz' job."""
    if not db.try_start_quiz(quiz_id):
        return  # someone else already triggered delivery (or it was cancelled)

    quiz = db.get_quiz(quiz_id)
    chat_id = quiz["chat_id"]
    questions = db.get_questions(quiz_id)

    if not questions:
        await _safe_call(
            context.bot.send_message, chat_id, f"Quiz '{quiz['name']}' has no questions — skipping.",
            retry_on_timeout=False,
        )
        db.update_quiz_status(quiz_id, "cancelled")
        return

    marks_txt = f"✅ +{quiz['marks_per_question']:g} mark(s) for a fully correct answer"
    if quiz["negative_marks"] > 0:
        marks_txt += f"\n❌ -{quiz['negative_marks']:g} mark(s) for a wrong answer (single-answer questions only)"

    await _safe_call(
        context.bot.send_message,
        chat_id,
        f"🚀 Quiz '{quiz['name']}' has started!\n"
        f"{len(questions)} question(s) — {_question_timer_seconds(quiz)}s per question.\n"
        f"{marks_txt}\n\n"
        f"Each question is a Telegram poll — tap an option to answer. "
        f"Some questions may have more than one correct answer, in which case you can select "
        f"several options; partial credit applies (e.g. 1 of 2 correct options picked = half marks).\n\n"
        f"Polls are non-anonymous so results/marking can be tallied, but only you see your own pick "
        f"highlighted — no one else can see what you selected.\n"
        f"Good luck! 🍀",
        retry_on_timeout=False,
    )

    await _post_question(context, quiz_id, qnum=1)


async def _post_question(context, quiz_id, qnum):
    """Posts question number `qnum` as a native Telegram poll and arms the
    job that closes it and moves on. If `qnum` is past the last question,
    ends the quiz instead."""
    quiz = db.get_quiz(quiz_id)
    if not quiz or quiz["status"] != "running":
        return

    questions = db.get_questions(quiz_id)
    if qnum > len(questions):
        await run_quiz_end(context, quiz_id)
        return

    q = questions[qnum - 1]
    chat_id = quiz["chat_id"]
    q_time = _question_timer_seconds(quiz)
    open_period = _poll_open_period(q_time)
    is_multi = len(q["correct_indices"]) > 1

    # Telegram's own limits: poll question <=300 chars, each option <=100 chars.
    question_text = f"Q{q['qnum']}. {q['question']}"
    if len(question_text) > 300:
        question_text = question_text[:299] + "…"
    options = [opt if len(opt) <= 100 else opt[:99] + "…" for opt in q["options"]]

    try:
        if is_multi:
            # Native quiz-mode polls only support a single correct option,
            # so multi-answer questions use a regular (non-quiz) poll with
            # multiple selection enabled instead. Telegram won't mark these
            # correct/wrong itself — we post a text reveal for those once
            # the poll closes.
            msg = await _safe_call(
                context.bot.send_poll,
                chat_id,
                question_text,
                options,
                is_anonymous=False,
                allows_multiple_answers=True,
                open_period=open_period,
                retry_on_timeout=False,
            )
        else:
            # Native quiz-mode poll: Telegram itself shows the live
            # countdown bar, instantly marks each tap right/wrong for that
            # user, and (being non-anonymous) offers "View Votes" — all
            # handled client-side, no message edits needed from us.
            msg = await _safe_call(
                context.bot.send_poll,
                chat_id,
                question_text,
                options,
                is_anonymous=False,
                type="quiz",
                correct_option_id=q["correct_indices"][0],
                open_period=open_period,
                retry_on_timeout=False,
            )
    except Exception:
        # Couldn't post this question at all — skip it rather than stall
        # the whole quiz forever, and move on to the next one.
        logger.error("Failed to post question %s for quiz %s, skipping it.", q["id"], quiz_id)
        db.advance_to_question(quiz_id, qnum, None)
        db.clear_active_question(quiz_id)
        await _post_question(context, quiz_id, qnum + 1)
        return

    db.set_question_poll_info(q["id"], msg.message_id, msg.poll.id)
    db.advance_to_question(quiz_id, qnum, q["id"])

    # Advance shortly after Telegram's own open_period elapses, so our
    # bookkeeping (tallying answers, posting the next question) happens
    # right after the poll has actually auto-closed on Telegram's side.
    context.job_queue.run_once(
        _question_timer_job,
        when=open_period + 2,
        data={"quiz_id": quiz_id, "question_id": q["id"], "qnum": qnum},
        name=f"qtimer_{quiz_id}_{q['id']}",
    )


async def _question_timer_job(context):
    data = context.job.data
    await _close_and_advance(context, data["quiz_id"], data["question_id"], data["qnum"])


async def _close_and_advance(context, quiz_id, question_id, qnum):
    """Closes the poll for the given question (if it's still the active
    one) and moves on to the next question. Safe to call more than once —
    e.g. from a resumed startup — since it checks the quiz is still
    'running' and that this question is still the active one before doing
    anything."""
    quiz = db.get_quiz(quiz_id)
    if not quiz or quiz["status"] != "running" or quiz["active_question_id"] != question_id:
        return  # already closed by something else, or quiz ended/cancelled

    for job in context.job_queue.get_jobs_by_name(f"qtimer_{quiz_id}_{question_id}"):
        job.schedule_removal()

    question = db.get_question(question_id)
    if question:
        if question.get("message_id"):
            try:
                # Telegram auto-closes the poll itself once open_period
                # elapses, which is the normal case by the time we get here
                # — so stop_poll failing with BadRequest ("Poll can't be
                # stopped") is expected, not an error, and must NOT go
                # through _safe_call's retry loop: BadRequest is a subclass
                # of NetworkError in python-telegram-bot, so it was being
                # retried 5x with backoff there, which is exactly what was
                # adding a 15-20s gap before the next question. We still
                # call stop_poll directly (not skip it) to guarantee it's
                # actually shut before we tally votes — e.g. after a
                # restart, where open_period never got to run at all.
                await context.bot.stop_poll(quiz["chat_id"], question["message_id"])
            except BadRequest:
                pass  # already closed by Telegram itself - nothing to do
            except (TimedOut, NetworkError) as e:
                logger.warning("stop_poll transient failure for question %s: %s", question_id, e)

        is_multi = len(question["correct_indices"]) > 1
        if is_multi:
            # Regular (non-quiz) polls have no Bot API way to mark options
            # correct/wrong on the poll itself — that overlay only exists
            # for quiz-type polls, which only support one correct answer.
            # So for multi-answer questions we post this as a follow-up
            # message instead, formatted as a per-option checklist (like
            # the poll's own result bars) so it reads as close to "the same
            # UI" as possible even though it's technically a separate
            # message underneath the poll.
            correct_set = set(question["correct_indices"])
            selections = db.get_question_selections(question_id)
            exact_correct = sum(1 for sel in selections.values() if sel == correct_set)
            total_answered = len(selections)

            vote_counts = {}
            for sel in selections.values():
                for opt_idx in sel:
                    vote_counts[opt_idx] = vote_counts.get(opt_idx, 0) + 1

            lines = [f"☑️ Q{question['qnum']} results:"]
            for i, opt in enumerate(question["options"]):
                mark = "✅" if i in correct_set else "▫️"
                lines.append(f"{mark} {opt} — {vote_counts.get(i, 0)} vote(s)")
            lines.append(
                f"👥 {exact_correct}/{total_answered} selected exactly the right option(s) "
                f"(partial credit applies to the rest)"
            )
            reveal_text = "\n".join(lines)
            try:
                await _safe_call(context.bot.send_message, quiz["chat_id"], reveal_text, retry_on_timeout=False)
            except Exception:
                logger.warning("Could not send multi-answer reveal for question %s", question_id)
        # Single-answer questions need no extra message: the native quiz
        # poll already shows each participant the correct/wrong mark and
        # the group-visible result bars once it closes.

    db.clear_active_question(quiz_id)
    await asyncio.sleep(REVEAL_PAUSE_SECONDS)
    await _post_question(context, quiz_id, qnum + 1)


async def handle_poll_answer(update, context):
    """Telegram sends this for every answer/answer-change on a non-anonymous
    poll we posted. We mirror it into our own `selections` table so scoring
    (marks, negative marking, partial credit) can be computed the same way
    it always was."""
    pa = update.poll_answer
    question = db.get_question_by_poll_id(pa.poll_id)
    if not question:
        return  # not one of ours, or already cleaned up

    quiz_id = question["quiz_id"]
    quiz = db.get_quiz(quiz_id)
    if not quiz or quiz["status"] != "running" or quiz["active_question_id"] != question["id"]:
        return  # answer arrived after this question already closed — ignore it

    user = pa.user
    db.clear_selection(question["id"], user.id)
    for option_index in pa.option_ids:
        db.add_selection(quiz_id, question["id"], user.id, user.username or user.full_name, option_index)


# ---------------- Resuming after a restart ----------------

async def resume_running_quiz(context, quiz_id):
    """Called on bot startup for quizzes that were mid-delivery when the bot
    went down. job_queue jobs don't survive a restart, so we can't know how
    much time was left on the active poll — we just close it out (Telegram
    keeps the poll itself intact/answerable until we explicitly stop it) and
    continue with the next question."""
    quiz = db.get_quiz(quiz_id)
    if not quiz or quiz["status"] != "running":
        return

    if quiz["active_question_id"]:
        await _close_and_advance(context, quiz_id, quiz["active_question_id"], quiz["current_qnum"])
    else:
        await _post_question(context, quiz_id, quiz["current_qnum"] + 1)


# ---------------- Ending the quiz ----------------

async def run_quiz_end(context, quiz_id):
    quiz = db.get_quiz(quiz_id)
    if not quiz or quiz["status"] == "cancelled":
        return

    # Cancel any still-pending per-question timer jobs so none of them can
    # fire after the quiz (and its data) is gone.
    if getattr(context, "job_queue", None):
        for job in list(context.job_queue.jobs()):
            if job.name and job.name.startswith(f"qtimer_{quiz_id}_"):
                job.schedule_removal()

    chat_id = quiz["chat_id"]
    questions = db.get_questions(quiz_id)

    leaderboard = db.compute_leaderboard(quiz_id, quiz["marks_per_question"], quiz["negative_marks"])
    participant_count = len(leaderboard)

    if not leaderboard:
        text = f"🏁 Quiz '{quiz['name']}' has ended. No one answered any question. 😢"
    else:
        shown = leaderboard[:20]  # top 20, or everyone if fewer than 20 answered
        medals = ["🥇", "🥈", "🥉"]
        lines = [f"🏁 Quiz '{quiz['name']}' has ended!", f"👥 {participant_count} participant(s)", "", "🏆 Leaderboard:"]
        for i, row in enumerate(shown):
            prefix = medals[i] if i < 3 else f"{i + 1}."
            lines.append(
                f"{prefix} {row['username']} — {row['score']:g} marks ({row['correct']}/{len(questions)} correct)"
            )
        if participant_count > len(shown):
            lines.append(f"\n…and {participant_count - len(shown)} more participant(s).")
        text = "\n".join(lines)

    await _safe_call(context.bot.send_message, chat_id, text, retry_on_timeout=False)

    # Requirement: clean up everything related to a finished quiz
    db.delete_quiz_data(quiz_id)