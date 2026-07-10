import json
import sqlite3
import threading
from collections import defaultdict

from config import DB_PATH


class QuizDB:
    """Thread-safe SQLite wrapper for the quiz bot.

    Each group's quizzes are isolated by chat_id, so the bot naturally
    supports many groups running independent, simultaneously scheduled
    quizzes.
    """

    _lock = threading.Lock()

    def __init__(self, path=DB_PATH):
        self.path = path
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._lock, self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS quizzes (
                    id TEXT PRIMARY KEY,
                    chat_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    duration_min INTEGER NOT NULL,
                    reminder_min INTEGER NOT NULL,
                    marks_per_question REAL NOT NULL DEFAULT 1,
                    negative_marks REAL NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'scheduled',
                    current_qnum INTEGER NOT NULL DEFAULT 0,
                    active_question_id INTEGER,
                    question_time_sec INTEGER NOT NULL DEFAULT 20,
                    created_by INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    quiz_id TEXT NOT NULL,
                    qnum INTEGER NOT NULL,
                    question TEXT NOT NULL,
                    options TEXT NOT NULL,
                    correct_indices TEXT NOT NULL,
                    message_id INTEGER,
                    poll_id TEXT,
                    FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
                );

                CREATE TABLE IF NOT EXISTS selections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    quiz_id TEXT NOT NULL,
                    question_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    username TEXT,
                    option_index INTEGER NOT NULL,
                    UNIQUE(question_id, user_id, option_index)
                );

                CREATE TABLE IF NOT EXISTS ready_clicks (
                    quiz_id TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    PRIMARY KEY (quiz_id, user_id)
                );

                CREATE TABLE IF NOT EXISTS groups (
                    chat_id INTEGER PRIMARY KEY,
                    title TEXT
                );
                """
            )
            # Migrate older DB files (created before per-question pacing was
            # added) that already have a `quizzes` table but are missing the
            # new tracking columns.
            existing_cols = {r["name"] for r in conn.execute("PRAGMA table_info(quizzes)").fetchall()}
            if "current_qnum" not in existing_cols:
                conn.execute("ALTER TABLE quizzes ADD COLUMN current_qnum INTEGER NOT NULL DEFAULT 0")
            if "active_question_id" not in existing_cols:
                conn.execute("ALTER TABLE quizzes ADD COLUMN active_question_id INTEGER")
            if "question_time_sec" not in existing_cols:
                conn.execute("ALTER TABLE quizzes ADD COLUMN question_time_sec INTEGER NOT NULL DEFAULT 20")

            existing_q_cols = {r["name"] for r in conn.execute("PRAGMA table_info(questions)").fetchall()}
            if "poll_id" not in existing_q_cols:
                conn.execute("ALTER TABLE questions ADD COLUMN poll_id TEXT")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_questions_poll_id ON questions(poll_id)")

    # ---------------- Groups ----------------
    def upsert_group(self, chat_id, title):
        with self._lock, self._connect() as conn:
            conn.execute(
                "INSERT INTO groups (chat_id, title) VALUES (?, ?) "
                "ON CONFLICT(chat_id) DO UPDATE SET title=excluded.title",
                (chat_id, title),
            )

    def remove_group(self, chat_id):
        with self._lock, self._connect() as conn:
            conn.execute("DELETE FROM groups WHERE chat_id=?", (chat_id,))

    def list_groups(self):
        with self._lock, self._connect() as conn:
            rows = conn.execute("SELECT * FROM groups ORDER BY title").fetchall()
            return [dict(r) for r in rows]

    # ---------------- Quiz ----------------
    def create_quiz(self, quiz_id, chat_id, name, start_time, duration_min, reminder_min,
                     marks_per_question, negative_marks, created_by, question_time_sec=20):
        with self._lock, self._connect() as conn:
            conn.execute(
                "INSERT INTO quizzes (id, chat_id, name, start_time, duration_min, reminder_min, "
                "marks_per_question, negative_marks, created_by, question_time_sec) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (quiz_id, chat_id, name, start_time, duration_min, reminder_min,
                 marks_per_question, negative_marks, created_by, question_time_sec),
            )

    def get_quiz(self, quiz_id):
        with self._lock, self._connect() as conn:
            row = conn.execute("SELECT * FROM quizzes WHERE id=?", (quiz_id,)).fetchone()
            return dict(row) if row else None

    def update_quiz_status(self, quiz_id, status):
        with self._lock, self._connect() as conn:
            conn.execute("UPDATE quizzes SET status=? WHERE id=?", (status, quiz_id))

    def try_start_quiz(self, quiz_id):
        """Atomically flips ready_gate -> running. Returns True only for the
        caller that actually performed the transition, so a ready-click and
        a timeout firing at the same moment can't both deliver questions."""
        with self._lock, self._connect() as conn:
            cur = conn.execute(
                "UPDATE quizzes SET status='running' WHERE id=? AND status='ready_gate'", (quiz_id,)
            )
            return cur.rowcount > 0

    def update_quiz_field(self, quiz_id, **fields):
        if not fields:
            return
        cols = ", ".join(f"{k}=?" for k in fields)
        values = list(fields.values()) + [quiz_id]
        with self._lock, self._connect() as conn:
            conn.execute(f"UPDATE quizzes SET {cols} WHERE id=?", values)

    def advance_to_question(self, quiz_id, qnum, question_id):
        """Atomically records which question is now the active/open one.
        Used both for normal delivery and for resuming after a restart."""
        with self._lock, self._connect() as conn:
            conn.execute(
                "UPDATE quizzes SET current_qnum=?, active_question_id=? WHERE id=?",
                (qnum, question_id, quiz_id),
            )

    def clear_active_question(self, quiz_id):
        with self._lock, self._connect() as conn:
            conn.execute("UPDATE quizzes SET active_question_id=NULL WHERE id=?", (quiz_id,))

    def get_scheduled_quizzes(self):
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM quizzes WHERE status IN ('scheduled', 'ready_gate', 'running')"
            ).fetchall()
            return [dict(r) for r in rows]

    def list_manageable_quizzes(self, user_id):
        """Quizzes still in 'scheduled' status (not yet started) created by this admin."""
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM quizzes WHERE status='scheduled' AND created_by=? ORDER BY start_time",
                (user_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def delete_quiz_data(self, quiz_id):
        with self._lock, self._connect() as conn:
            conn.execute("DELETE FROM selections WHERE quiz_id=?", (quiz_id,))
            conn.execute("DELETE FROM ready_clicks WHERE quiz_id=?", (quiz_id,))
            conn.execute("DELETE FROM questions WHERE quiz_id=?", (quiz_id,))
            conn.execute("DELETE FROM quizzes WHERE id=?", (quiz_id,))

    # ---------------- Questions ----------------
    def add_question(self, quiz_id, qnum, question, options, correct_indices):
        with self._lock, self._connect() as conn:
            conn.execute(
                "INSERT INTO questions (quiz_id, qnum, question, options, correct_indices) "
                "VALUES (?, ?, ?, ?, ?)",
                (quiz_id, qnum, question, json.dumps(options), json.dumps(correct_indices)),
            )

    def replace_questions(self, quiz_id, questions):
        """Wipes existing questions/selections for this quiz and inserts a new set."""
        with self._lock, self._connect() as conn:
            conn.execute("DELETE FROM selections WHERE quiz_id=?", (quiz_id,))
            conn.execute("DELETE FROM questions WHERE quiz_id=?", (quiz_id,))
            for i, q in enumerate(questions, start=1):
                conn.execute(
                    "INSERT INTO questions (quiz_id, qnum, question, options, correct_indices) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (quiz_id, i, q["question"], json.dumps(q["options"]), json.dumps(q["correct_indices"])),
                )

    def get_questions(self, quiz_id):
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM questions WHERE quiz_id=? ORDER BY qnum", (quiz_id,)
            ).fetchall()
            result = []
            for r in rows:
                d = dict(r)
                d["options"] = json.loads(d["options"])
                d["correct_indices"] = json.loads(d["correct_indices"])
                result.append(d)
            return result

    def get_question(self, question_id):
        with self._lock, self._connect() as conn:
            row = conn.execute("SELECT * FROM questions WHERE id=?", (question_id,)).fetchone()
            if not row:
                return None
            d = dict(row)
            d["options"] = json.loads(d["options"])
            d["correct_indices"] = json.loads(d["correct_indices"])
            return d

    def set_question_poll_info(self, question_id, message_id, poll_id):
        """Records which Telegram poll (native quiz/poll message) a question
        was delivered as, so an incoming `poll_answer` update — which only
        carries Telegram's own poll_id, not our question_id — can be mapped
        back to the right question."""
        with self._lock, self._connect() as conn:
            conn.execute(
                "UPDATE questions SET message_id=?, poll_id=? WHERE id=?",
                (message_id, poll_id, question_id),
            )

    def get_question_by_poll_id(self, poll_id):
        with self._lock, self._connect() as conn:
            row = conn.execute("SELECT * FROM questions WHERE poll_id=?", (poll_id,)).fetchone()
            if not row:
                return None
            d = dict(row)
            d["options"] = json.loads(d["options"])
            d["correct_indices"] = json.loads(d["correct_indices"])
            return d

    # ---------------- Selections (answers) ----------------
    def get_user_selection(self, question_id, user_id):
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                "SELECT option_index FROM selections WHERE question_id=? AND user_id=?",
                (question_id, user_id),
            ).fetchall()
            return set(r["option_index"] for r in rows)

    def add_selection(self, quiz_id, question_id, user_id, username, option_index):
        with self._lock, self._connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO selections (quiz_id, question_id, user_id, username, option_index) "
                "VALUES (?, ?, ?, ?, ?)",
                (quiz_id, question_id, user_id, username, option_index),
            )

    def remove_selection(self, question_id, user_id, option_index):
        with self._lock, self._connect() as conn:
            conn.execute(
                "DELETE FROM selections WHERE question_id=? AND user_id=? AND option_index=?",
                (question_id, user_id, option_index),
            )

    def clear_selection(self, question_id, user_id):
        with self._lock, self._connect() as conn:
            conn.execute("DELETE FROM selections WHERE question_id=? AND user_id=?", (question_id, user_id))

    def get_question_selections(self, question_id):
        """Returns {user_id: set(option_index)} for everyone who answered this question."""
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                "SELECT user_id, option_index FROM selections WHERE question_id=?", (question_id,)
            ).fetchall()
        result = defaultdict(set)
        for r in rows:
            result[r["user_id"]].add(r["option_index"])
        return result

    # ---------------- Ready gate ----------------
    def add_ready_click(self, quiz_id, user_id):
        with self._lock, self._connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO ready_clicks (quiz_id, user_id) VALUES (?, ?)", (quiz_id, user_id)
            )

    def count_ready_clicks(self, quiz_id):
        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*) as c FROM ready_clicks WHERE quiz_id=?", (quiz_id,)
            ).fetchone()
            return row["c"]

    # ---------------- Leaderboard ----------------
    def compute_leaderboard(self, quiz_id, marks_per_question, negative_marks):
        with self._lock, self._connect() as conn:
            q_rows = conn.execute(
                "SELECT id, correct_indices FROM questions WHERE quiz_id=?", (quiz_id,)
            ).fetchall()
            q_correct = {r["id"]: set(json.loads(r["correct_indices"])) for r in q_rows}

            rows = conn.execute(
                "SELECT question_id, user_id, username, option_index FROM selections WHERE quiz_id=?",
                (quiz_id,),
            ).fetchall()

        user_answers = defaultdict(lambda: defaultdict(set))
        usernames = {}
        for r in rows:
            user_answers[r["user_id"]][r["question_id"]].add(r["option_index"])
            usernames[r["user_id"]] = r["username"]

        results = []
        for user_id, qmap in user_answers.items():
            score = 0.0
            correct_count = 0
            for qid, selected in qmap.items():
                correct = q_correct.get(qid, set())
                if not correct:
                    continue
                if len(correct) > 1:
                    # Multi-answer question: give proportional ("divide rule")
                    # credit for however many of the correct options were
                    # picked — e.g. 1 of 2 correct options = 0.5 marks.
                    # Picking zero correct options scores 0, not negative;
                    # negative marking only applies to single-answer questions.
                    correct_selected = selected & correct
                    fraction = len(correct_selected) / len(correct)
                    score += fraction * marks_per_question
                    if selected == correct:
                        correct_count += 1
                else:
                    if selected == correct:
                        score += marks_per_question
                        correct_count += 1
                    elif selected:
                        score -= negative_marks
            results.append(
                {"user_id": user_id, "username": usernames[user_id], "score": score, "correct": correct_count}
            )

        results.sort(key=lambda r: (-r["score"], -r["correct"]))
        return results