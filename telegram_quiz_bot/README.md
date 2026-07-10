# Telegram Group Quiz Bot

A Telegram bot that lets group admins schedule quizzes by uploading a
question file — privately, so students don't see the questions early.
Supports **multiple groups**, **multiple quizzes at different timestamps**,
**flexible question formats**, **marks & negative marking**, and a
**"wait for everyone" start gate**.

## Features

- **Private quiz setup.** DM the bot, run `/createquiz`, pick a group —
  uploading the file and answering setup questions never touches the group
  chat, so students can't see the questions early.
- **Flexible question format** — any number of options (not fixed to a–d),
  and questions can have one or several correct answers. Question numbering
  is added automatically by the bot.
- **No participant limit.** Any number of group members can answer — the
  bot just records every tap.
- **Up to 100+ questions per quiz**, paced automatically to avoid Telegram
  rate limits.
- **Marks & negative marking**, set per quiz when you create it.
- **"Ready" gate** — when the quiz's start time arrives, the bot posts a
  "✅ I'm Ready" button instead of dumping questions immediately. Questions
  are posted once at least 2 members tap it (or automatically after 3
  minutes, so it never gets stuck).
- **Auto reminder**, **auto results/leaderboard**, and **auto cleanup** of
  that quiz's data once it ends.
- **Cancel or edit** a quiz (title, marks, negative marking, timing, or the
  whole question set) any time before it starts, via `/myquizzes`.
- Every group's quizzes are isolated by chat ID — run this in as many
  groups as you like, with multiple quizzes scheduled at different times,
  fully independent of each other.

## Question file format

```
Question: SI unit of electric current is
(a) Volt
(b) Ohm
(c) Ampere
(d) Watt
Answer: c
```

- **Any number of options** — 2, 4, 5, or more, not limited to a–d.
- **Multiple correct answers** — list them comma-separated:
  `Answer: a,c` (members must select _all_ correct options and no wrong
  ones to get credit for that question).
- **No numbering needed** — the bot numbers questions itself (Q1, Q2, …)
  regardless of what's in the file.
- Works from `.txt` or `.docx` files. See `sample_quiz.txt` for a working
  example covering 2-option, 4-option, 5-option, and multi-answer
  questions.

## 1. Create your bot

1. Open Telegram, message [@BotFather](https://t.me/BotFather).
2. Send `/newbot` and follow the prompts to get a **bot token**.
3. Add your bot to each group you want it to run quizzes in, and make it a
   **group admin** (needed to post messages and manage the quiz buttons).
4. Start a **private chat** with your bot at least once (search its
   username → Start) — Telegram requires this before a bot can message you
   privately, and `/createquiz` runs privately by default.

## 2. Install & configure

Requires Python **3.11 or 3.12** (python-telegram-bot is not yet compatible
with Python 3.14 — if `py -0` shows multiple versions on Windows, create the
venv with `py -3.12 -m venv venv`).

```bash
cd telegram_quiz_bot
python -m venv venv
source venv/bin/activate      # Windows (Git Bash): source venv/Scripts/activate
pip install -r requirements.txt

cp .env.example .env
# then edit .env and paste your BOT_TOKEN
```

## 3. Run the bot

```bash
python bot.py
```

deactivate
rm -rf venv
py -3.12 -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
python --version

You should see `Bot started. Polling for updates...`.

## 4. Create a quiz (privately)

1. DM the bot and send `/createquiz`.
2. Tap the group you want the quiz posted to (the bot lists groups where
   you're an admin and it's already a member — add it to the group first if
   it doesn't show up).
3. Upload the question file.
4. Answer the prompts: **quiz name**, **start time**
   (`YYYY-MM-DD HH:MM`, or `now`), **duration** (minutes), **reminder**
   (minutes before start, `0` for none), **marks per correct answer**, and
   **negative marking per wrong answer** (`0` for none).
5. Confirm with ✅.

Repeat as many times as you like, for the same group or different ones —
each quiz runs independently, at its own scheduled time.

> `/createquiz` also still works if run directly inside a group (handy for
> quick tests), but the bot will warn you that the file will be visible to
> everyone there.

## 5. What happens automatically

1. **Reminder** — posted in the group X minutes before start, with the
   question count, duration, and marking scheme.
2. **Ready gate** — at start time, the bot posts an "✅ I'm Ready" button.
   Questions are delivered once 2+ members tap it, or automatically after 3
   minutes regardless.
3. **Questions — one at a time, as native Telegram polls.** Each question is
   posted as a real Telegram poll and stays open for `QUESTION_TIME_SECONDS`
   (20s by default, clamped to Telegram's 5–600s poll limit; set it in
   `.env`). Telegram itself drives the live countdown bar and the instant
   tap response — no message-editing flicker on our end.
   - **Single-answer questions** post as a native **quiz poll**: tapping an
     option instantly shows that member a ✅/❌, and once it closes everyone
     sees the "Final results" bar with the correct option checked and a
     **View Votes** link (poll is non-anonymous).
   - **Multi-answer ("select all that apply") questions** post as a regular
     poll with multiple selection enabled — Telegram's quiz mode only
     supports one correct option, so these can't use it. The bot posts a
     short follow-up message with the correct combination once the poll
     closes, since Telegram won't mark these right/wrong itself.
     Pacing one question per timer — instead of firing all of them in a tight
     loop — is what keeps a 100-question quiz from tripping Telegram's flood
     limits partway through; any flood-control errors that do occur are
     retried automatically.
4. **End** — once the last question's timer closes, the bot posts a
   leaderboard (marks-based, ties broken by number of fully-correct
   answers) and **deletes that quiz's data** from the database. A
   safety-net timer also exists in case delivery ever gets stuck.

### Scoring rules

- A question is "correct" only if a member's final selection **exactly**
  matches the answer key (all correct options, no wrong ones).
- Marks are only deducted for questions a member actually attempted —
  skipping a question never costs negative marks.

## 6. Manage a quiz before it starts

DM the bot `/myquizzes` to see quizzes you've scheduled that haven't
started yet. Tap one to:

- Edit the **title**, **marks**, **negative marking**, **start time**,
  **duration**, or **reminder** (changing timing automatically
  reschedules the quiz).
- **Replace the questions** entirely by uploading a new file.
- **Cancel** the quiz — this notifies the group and wipes the quiz's data.

Once a quiz has started (past the ready gate), it can no longer be edited
or cancelled through this menu.

## Notes & limits

- Questions are posted one at a time, each held open for
  `QUESTION_TIME_SECONDS` (20s by default) before the answer is revealed and
  the next one goes out — so a 100-question quiz takes roughly
  `100 × (QUESTION_TIME_SECONDS + a few seconds)` to run. Any Telegram
  flood-control errors along the way are retried automatically rather than
  silently killing the rest of the quiz.
- Inline keyboard buttons have a per-button label limit (~90 characters
  here) — very long option text gets truncated.
- The bot only allows actual Telegram group admins (or IDs listed in
  `EXTRA_ADMIN_IDS` in `.env`) to run `/createquiz`.
- Quiz management (`/myquizzes`) only shows quizzes _you_ created — if
  another admin created one, they manage it from their own DM.
- Data is stored locally in a SQLite file (`quizbot.db` by default) — no
  external services required.

## Project structure

```
telegram_quiz_bot/
├── bot.py               # entry point, wires everything together
├── config.py             # reads .env settings
├── database.py            # SQLite storage layer
├── parser.py               # parses .txt/.docx question files
├── scheduler.py            # schedules reminder/start/end jobs per quiz
├── quiz_runtime.py          # ready gate, posts questions, scores, cleans up
├── handlers/
│   ├── admin.py              # /createquiz conversation flow
│   └── manage.py             # /myquizzes cancel/edit flow
├── requirements.txt
├── .env.example
└── sample_quiz.txt          # example question file covering all formats
```
