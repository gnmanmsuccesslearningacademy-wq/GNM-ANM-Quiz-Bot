"""
Common utilities and helper functions for the bot
"""

def calculate_accuracy(correct, total):
    """Calculate accuracy percentage"""
    if total == 0:
        return 0
    return round((correct / total) * 100, 2)


def format_user_stats(stats):
    """Format user statistics for display"""
    if not stats:
        return None
    
    user_id, name, phone, join_date, total_quizzes, total_correct, total_wrong, total_marks, accuracy, rank = stats
    
    return f"""
👤 **Your Profile**

Name: {name}
Phone: {phone}
Joined: {join_date}

📊 **Statistics**
Total Quizzes: {total_quizzes}
Correct Answers: {total_correct}
Wrong Answers: {total_wrong}
Total Marks: {total_marks}
Accuracy: {accuracy}%
Rank: {rank}
"""


def format_leaderboard(leaderboard):
    """Format leaderboard for display"""
    if not leaderboard:
        return "🏆 No data available"
    
    text = "🏆 **LEADERBOARD**\n\n"
    for idx, (user_id, name, marks, accuracy, rank) in enumerate(leaderboard, 1):
        text += f"{idx}. {name}\n"
        text += f"   Marks: {marks} | Accuracy: {accuracy}%\n\n"
    
    return text


def format_quiz_result(score, total, marks, accuracy):
    """Format quiz result for display"""
    return f"""
✅ **QUIZ COMPLETED**

Score: {score}/{total}
Total Marks: {marks}
Accuracy: {accuracy}%

📊 Keep practicing to improve!
"""


def get_difficulty_level(difficulty):
    """Get emoji for difficulty level"""
    levels = {
        "Easy": "🟢",
        "Medium": "🟡",
        "Hard": "🔴"
    }
    return levels.get(difficulty, "⚪")


def validate_phone(phone):
    """Validate phone number"""
    if not phone or len(phone) < 10:
        return False
    return phone.isdigit()
