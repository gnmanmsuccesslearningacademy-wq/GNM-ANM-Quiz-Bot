from app.database.connection import get_db


# =========================
# CREATE TABLES
# =========================

async def create_tables():

    db = await get_db()

    # USERS
    await db.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        full_name TEXT,
        username TEXT,
        phone TEXT UNIQUE,
        join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_blocked INTEGER DEFAULT 0,
        total_quizzes INTEGER DEFAULT 0,
        total_correct INTEGER DEFAULT 0,
        total_wrong INTEGER DEFAULT 0,
        total_marks REAL DEFAULT 0,
        accuracy REAL DEFAULT 0,
        rank INTEGER DEFAULT 0
    )
    """)

    # QUESTIONS
    await db.execute("""
    CREATE TABLE IF NOT EXISTS questions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam TEXT,
        subject TEXT,
        chapter TEXT,
        question TEXT UNIQUE,
        option_a TEXT,
        option_b TEXT,
        option_c TEXT,
        option_d TEXT,
        correct_answer TEXT,
        explanation TEXT,
        difficulty TEXT DEFAULT 'Easy',
        marks REAL DEFAULT 1,
        negative_marks REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # QUIZ SESSIONS
    await db.execute("""
    CREATE TABLE IF NOT EXISTS quiz_sessions(
        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        score REAL DEFAULT 0,
        current_question INTEGER DEFAULT 1,
        total_question INTEGER DEFAULT 50,
        exam TEXT,
        subject TEXT,
        chapter TEXT,
        difficulty TEXT,
        quiz_type TEXT,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ended_at TIMESTAMP,
        status TEXT DEFAULT 'active',
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)

    # QUIZ RESPONSES (Track user answers)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS quiz_responses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        question_id INTEGER,
        user_answer TEXT,
        is_correct INTEGER,
        time_taken INTEGER,
        marked_for_review INTEGER DEFAULT 0,
        FOREIGN KEY (session_id) REFERENCES quiz_sessions(session_id),
        FOREIGN KEY (question_id) REFERENCES questions(id)
    )
    """)

    # USER STATS
    await db.execute("""
    CREATE TABLE IF NOT EXISTS user_stats(
        user_id INTEGER PRIMARY KEY,
        subject TEXT,
        correct_answers INTEGER DEFAULT 0,
        total_attempts INTEGER DEFAULT 0,
        accuracy REAL DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)

    # LEADERBOARD
    await db.execute("""
    CREATE TABLE IF NOT EXISTS leaderboard(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        rank_type TEXT,
        rank INTEGER,
        score REAL,
        quiz_count INTEGER,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)

    # BOOKMARKS
    await db.execute("""
    CREATE TABLE IF NOT EXISTS bookmarks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        question_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (question_id) REFERENCES questions(id)
    )
    """)

    # QUIZ HISTORY
    await db.execute("""
    CREATE TABLE IF NOT EXISTS quiz_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        quiz_id INTEGER,
        score REAL,
        total_marks REAL,
        accuracy REAL,
        quiz_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)

    # NOTICES
    await db.execute("""
    CREATE TABLE IF NOT EXISTS notices(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        admin_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP
    )
    """)

    # SCHEDULED QUIZZES (For live exams)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS scheduled_quizzes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        total_questions INTEGER,
        total_marks REAL,
        exam_type TEXT,
        created_by INTEGER
    )
    """)

    # EXAM RESULTS
    await db.execute("""
    CREATE TABLE IF NOT EXISTS exam_results(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_id INTEGER,
        user_id INTEGER,
        score REAL,
        rank INTEGER,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (exam_id) REFERENCES scheduled_quizzes(id),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)

    # QUIZ SCHEDULE (Simple Daily Quiz)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS quiz_schedule(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_name TEXT,
        exam TEXT,
        date TEXT,
        time TEXT,
        duration INTEGER,
        question_limit INTEGER,
        status TEXT DEFAULT 'pending',
        group_message_id INTEGER,
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # QUIZ RESULTS (Simple Quiz Results)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS quiz_results(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_id INTEGER,
        user_id INTEGER,
        correct INTEGER DEFAULT 0,
        wrong INTEGER DEFAULT 0,
        score REAL DEFAULT 0,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (quiz_id) REFERENCES quiz_schedule(id),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)

    await db.commit()
    await db.close()



# =========================
# USER FUNCTIONS
# =========================

async def add_user(user_id, full_name, username):

    db = await get_db()

    await db.execute(
        """
        INSERT OR IGNORE INTO users
        (user_id, full_name, username)
        VALUES(?,?,?)
        """,
        (user_id, full_name, username)
    )

    await db.commit()
    await db.close()


async def update_phone(user_id, phone):

    db = await get_db()

    await db.execute(
        """
        UPDATE users
        SET phone=?
        WHERE user_id=?
        """,
        (phone, user_id)
    )

    await db.commit()
    await db.close()


async def get_user(user_id):

    db = await get_db()

    cursor = await db.execute(
        """
        SELECT *
        FROM users
        WHERE user_id=?
        """,
        (user_id,)
    )

    user = await cursor.fetchone()

    await cursor.close()
    await db.close()

    return user


# =========================
# QUESTION FUNCTIONS
# =========================

async def add_question(
    exam,
    subject,
    chapter,
    question,
    option_a,
    option_b,
    option_c,
    option_d,
    correct_answer,
    explanation=None,
    difficulty="Easy",
    marks=1,
    negative_marks=0
):

    db = await get_db()

    await db.execute(
        """
        INSERT OR IGNORE INTO questions(
            exam,
            subject,
            chapter,
            question,
            option_a,
            option_b,
            option_c,
            option_d,
            correct_answer,
            explanation,
            difficulty,
            marks,
            negative_marks
        )
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            exam,
            subject,
            chapter,
            question,
            option_a,
            option_b,
            option_c,
            option_d,
            correct_answer,
            explanation,
            difficulty,
            marks,
            negative_marks
        )
    )

    await db.commit()
    await db.close()


async def get_random_question():

    db = await get_db()

    cursor = await db.execute("""
        SELECT *
        FROM questions
        ORDER BY RANDOM()
        LIMIT 1
    """)

    question = await cursor.fetchone()

    await cursor.close()
    await db.close()

    return question


async def get_question_by_id(question_id):

    db = await get_db()

    cursor = await db.execute(
        """
        SELECT *
        FROM questions
        WHERE id=?
        """,
        (question_id,)
    )

    question = await cursor.fetchone()

    await cursor.close()
    await db.close()

    return question


# =========================
# QUIZ SESSION
# =========================

async def start_quiz_session(user_id):

    db = await get_db()

    cursor = await db.execute(
        """
        SELECT COUNT(*)
        FROM questions
        """
    )
    total_questions = await cursor.fetchone()
    await cursor.close()

    total_question_count = total_questions[0] if total_questions else 0

    await db.execute(
        """
        INSERT OR REPLACE INTO quiz_sessions(
            user_id,
            score,
            current_question,
            total_question
        )
        VALUES(?,?,?,?)
        """,
        (
            user_id,
            0,
            1,
            total_question_count
        )
    )

    await db.commit()
    await db.close()


async def get_quiz_session(user_id):

    db = await get_db()

    cursor = await db.execute(
        """
        SELECT *
        FROM quiz_sessions
        WHERE user_id=?
        """,
        (user_id,)
    )

    session = await cursor.fetchone()

    await cursor.close()
    await db.close()

    return session


async def update_score(user_id):

    db = await get_db()

    await db.execute(
        """
        UPDATE quiz_sessions
        SET score = score + 1
        WHERE user_id=?
        """,
        (user_id,)
    )

    await db.commit()
    await db.close()


async def next_question(user_id):

    db = await get_db()

    await db.execute(
        """
        UPDATE quiz_sessions
        SET current_question=current_question+1
        WHERE user_id=?
        """,
        (user_id,)
    )

    await db.commit()
    await db.close()


# =========================
# USER STATS & PROFILE
# =========================

async def get_user_stats(user_id):
    """Get user profile with all statistics"""
    db = await get_db()
    
    cursor = await db.execute(
        """
        SELECT user_id, full_name, phone, join_date, 
               total_quizzes, total_correct, total_wrong, 
               total_marks, accuracy, rank
        FROM users
        WHERE user_id=?
        """,
        (user_id,)
    )
    
    stats = await cursor.fetchone()
    await cursor.close()
    await db.close()
    
    return stats


async def update_user_stats(user_id, correct, wrong, marks):
    """Update user statistics after quiz completion"""
    db = await get_db()
    
    await db.execute(
        """
        UPDATE users
        SET total_quizzes = total_quizzes + 1,
            total_correct = total_correct + ?,
            total_wrong = total_wrong + ?,
            total_marks = total_marks + ?
        WHERE user_id=?
        """,
        (correct, wrong, marks, user_id)
    )
    
    await db.commit()
    await db.close()


async def get_leaderboard(rank_type="all_time", limit=10):
    """Get leaderboard by type (daily, weekly, monthly, all_time)"""
    db = await get_db()
    
    cursor = await db.execute(
        """
        SELECT u.user_id, u.full_name, u.total_marks, u.accuracy, u.rank
        FROM users u
        WHERE u.is_blocked=0
        ORDER BY u.total_marks DESC
        LIMIT ?
        """,
        (limit,)
    )
    
    leaderboard = await cursor.fetchall()
    await cursor.close()
    await db.close()
    
    return leaderboard


async def add_bookmark(user_id, question_id):
    """Bookmark a question for review"""
    db = await get_db()
    
    await db.execute(
        """
        INSERT OR IGNORE INTO bookmarks(user_id, question_id)
        VALUES(?,?)
        """,
        (user_id, question_id)
    )
    
    await db.commit()
    await db.close()


async def get_bookmarks(user_id):
    """Get all bookmarked questions for user"""
    db = await get_db()
    
    cursor = await db.execute(
        """
        SELECT q.* FROM questions q
        INNER JOIN bookmarks b ON q.id = b.question_id
        WHERE b.user_id=?
        """,
        (user_id,)
    )
    
    bookmarks = await cursor.fetchall()
    await cursor.close()
    await db.close()
    
    return bookmarks


async def get_quiz_history(user_id, limit=10):
    """Get user's quiz history"""
    db = await get_db()
    
    cursor = await db.execute(
        """
        SELECT id, quiz_id, score, total_marks, accuracy, quiz_date
        FROM quiz_history
        WHERE user_id=?
        ORDER BY quiz_date DESC
        LIMIT ?
        """,
        (user_id, limit)
    )
    
    history = await cursor.fetchall()
    await cursor.close()
    await db.close()
    
    return history


# =========================
# QUIZ RESPONSES
# =========================

async def save_quiz_response(session_id, question_id, user_answer, is_correct, time_taken):
    """Save user's answer for a question"""
    db = await get_db()
    
    await db.execute(
        """
        INSERT INTO quiz_responses(session_id, question_id, user_answer, is_correct, time_taken)
        VALUES(?,?,?,?,?)
        """,
        (session_id, question_id, user_answer, is_correct, time_taken)
    )
    
    await db.commit()
    await db.close()


# =========================
# NOTICES
# =========================

async def get_notices():
    """Get all active notices"""
    db = await get_db()
    
    cursor = await db.execute(
        """
        SELECT id, title, content, created_at
        FROM notices
        WHERE expires_at IS NULL OR expires_at > datetime('now')
        ORDER BY created_at DESC
        """
    )
    
    notices = await cursor.fetchall()
    await cursor.close()
    await db.close()
    
    return notices


# =========================
# SCHEDULED QUIZZES
# =========================

async def add_scheduled_quiz(name, description, start_time, end_time, total_questions, total_marks, exam_type, admin_id):
    """Add a new scheduled quiz"""
    db = await get_db()
    
    await db.execute(
        """
        INSERT INTO scheduled_quizzes(name, description, start_time, end_time, total_questions, total_marks, exam_type, created_by)
        VALUES(?,?,?,?,?,?,?,?)
        """,
        (name, description, start_time, end_time, total_questions, total_marks, exam_type, admin_id)
    )
    
    await db.commit()
    await db.close()


async def get_scheduled_quizzes():
    """Get all active and upcoming scheduled quizzes"""
    db = await get_db()
    
    cursor = await db.execute(
        """
        SELECT id, name, description, start_time, end_time, total_questions, total_marks
        FROM scheduled_quizzes
        WHERE end_time > datetime('now')
        ORDER BY start_time ASC
        """
    )
    
    quizzes = await cursor.fetchall()
    await cursor.close()
    await db.close()
    
    return quizzes


async def get_questions_by_exam(exam_name, limit=50):
    """Get questions for a specific exam or related exam terms"""
    db = await get_db()
    exam_key = exam_name.strip().lower()

    # Try exact exam/subject/chapter match first
    cursor = await db.execute(
        """
        SELECT *
        FROM questions
        WHERE LOWER(exam) = ? OR LOWER(subject) = ? OR LOWER(chapter) = ?
        ORDER BY RANDOM()
        LIMIT ?
        """,
        (exam_key, exam_key, exam_key, limit)
    )

    questions = await cursor.fetchall()
    await cursor.close()

    if questions:
        await db.close()
        return questions

    # Fall back to tokenized partial search for broader match
    tokens = [token.strip().lower() for token in exam_name.split() if token.strip()]
    if not tokens:
        await db.close()
        return []

    where_clauses = []
    params = []
    for token in tokens:
        where_clauses.append("(LOWER(exam) LIKE ? OR LOWER(subject) LIKE ? OR LOWER(chapter) LIKE ?)")
        params.extend([f"%{token}%", f"%{token}%", f"%{token}%"])

    query = f"""
        SELECT *
        FROM questions
        WHERE {' OR '.join(where_clauses)}
        ORDER BY RANDOM()
        LIMIT ?
        """
    params.append(limit)

    cursor = await db.execute(query, params)
    questions = await cursor.fetchall()
    await cursor.close()
    await db.close()

    return questions


async def get_available_exams():
    """Get all available exam names from questions table"""
    db = await get_db()
    
    cursor = await db.execute(
        """
        SELECT DISTINCT exam
        FROM questions
        WHERE exam IS NOT NULL AND exam != ''
        ORDER BY exam ASC
        """
    )
    
    exams = await cursor.fetchall()
    await cursor.close()
    await db.close()
    
    return [exam[0] for exam in exams] if exams else []


async def delete_all_scheduled_quizzes():
    """Delete all scheduled quizzes"""
    try:
        db = await get_db()
        
        await db.execute("DELETE FROM scheduled_quizzes")
        
        await db.commit()
        await db.close()
    except Exception as e:
        raise Exception(f"Failed to delete all quizzes: {str(e)}")


async def delete_scheduled_quiz(quiz_id):
    """Delete a specific scheduled quiz"""
    db = await get_db()
    
    await db.execute(
        "DELETE FROM scheduled_quizzes WHERE id=?",
        (quiz_id,)
    )
    
    await db.commit()
    await db.close()


# =========================
# SIMPLE QUIZ SCHEDULE (Daily Quiz)
# =========================

async def add_quiz_schedule(quiz_name, exam, date, time, duration, question_limit, created_by):
    """Add a new quiz schedule"""
    db = await get_db()
    
    cursor = await db.execute(
        """
        INSERT INTO quiz_schedule(quiz_name, exam, date, time, duration, question_limit, status, created_by)
        VALUES(?,?,?,?,?,?,?,?)
        """,
        (quiz_name, exam, date, time, duration, question_limit, 'pending', created_by)
    )
    
    quiz_id = cursor.lastrowid
    await db.commit()
    await db.close()
    
    return quiz_id


async def get_quiz_schedule_by_id(quiz_id):
    """Get quiz schedule by ID"""
    db = await get_db()
    
    cursor = await db.execute(
        """
        SELECT id, quiz_name, exam, date, time, duration, question_limit, status
        FROM quiz_schedule
        WHERE id = ?
        """,
        (quiz_id,)
    )
    
    quiz = await cursor.fetchone()
    await cursor.close()
    await db.close()
    
    return quiz


async def get_all_quiz_schedules():
    """Get all quiz schedules"""
    db = await get_db()
    
    cursor = await db.execute(
        """
        SELECT id, quiz_name, exam, date, time, duration, question_limit, status
        FROM quiz_schedule
        ORDER BY date DESC, time DESC
        """
    )
    
    quizzes = await cursor.fetchall()
    await cursor.close()
    await db.close()
    
    return quizzes


async def update_quiz_status(quiz_id, status):
    """Update quiz status (pending, active, ended)"""
    db = await get_db()
    
    await db.execute(
        """
        UPDATE quiz_schedule
        SET status = ?
        WHERE id = ?
        """,
        (status, quiz_id)
    )
    
    await db.commit()
    await db.close()


async def delete_quiz_schedule(quiz_id):
    """Delete a quiz schedule from the database"""
    db = await get_db()
    
    await db.execute(
        """
        DELETE FROM quiz_schedule
        WHERE id = ?
        """,
        (quiz_id,)
    )
    
    await db.commit()
    await db.close()


async def save_quiz_result(quiz_id, user_id, correct, wrong, score):
    """Save quiz result for a student"""
    db = await get_db()
    
    await db.execute(
        """
        INSERT INTO quiz_results(quiz_id, user_id, correct, wrong, score)
        VALUES(?,?,?,?,?)
        """,
        (quiz_id, user_id, correct, wrong, score)
    )
    
    await db.commit()
    await db.close()


async def save_quiz_history(user_id, quiz_id, score, total_marks, accuracy):
    """Save quiz history for user reporting"""
    db = await get_db()
    
    await db.execute(
        """
        INSERT INTO quiz_history(user_id, quiz_id, score, total_marks, accuracy)
        VALUES(?,?,?,?,?)
        """,
        (user_id, quiz_id, score, total_marks, accuracy)
    )
    
    await db.commit()
    await db.close()


async def get_quiz_leaderboard(quiz_id, limit=10):
    """Get top 10 scorers for a quiz"""
    db = await get_db()
    
    cursor = await db.execute(
        """
        SELECT users.user_id, users.full_name, quiz_results.correct, quiz_results.wrong, quiz_results.score
        FROM quiz_results
        JOIN users ON quiz_results.user_id = users.user_id
        WHERE quiz_results.quiz_id = ?
        ORDER BY quiz_results.score DESC
        LIMIT ?
        """,
        (quiz_id, limit)
    )
    
    results = await cursor.fetchall()
    await cursor.close()
    await db.close()
    
    return results


async def get_user_quiz_result(quiz_id, user_id):
    """Get a specific user's quiz result"""
    db = await get_db()
    
    cursor = await db.execute(
        """
        SELECT correct, wrong, score, submitted_at
        FROM quiz_results
        WHERE quiz_id = ? AND user_id = ?
        """,
        (quiz_id, user_id)
    )
    
    result = await cursor.fetchone()
    await cursor.close()
    await db.close()
    
    return result