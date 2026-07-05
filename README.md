# GNM / ANM Quiz Bot

## 📚 একটি অনলাইন Quiz Platform Telegram এর মাধ্যমে

![Status](https://img.shields.io/badge/status-active-green)
![License](https://img.shields.io/badge/license-private-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)

---

## 🎯 বৈশিষ্ট্য

✅ **Live Quiz** - সময়সীমা সহ competitive exams  
✅ **Practice Mode** - নিজের গতিতে শেখার সুবিধা  
✅ **Leaderboard** - Real-time ranking system  
✅ **Performance Tracking** - বিস্তারিত statistics  
✅ **Admin Dashboard** - সম্পূর্ণ management system  
✅ **Multiple File Formats** - Excel, Word, Text support  
✅ **Notifications** - Important updates এবং announcements  

---

## 📖 ডকুমেন্টেশন

### 👨‍🎓 [Student User Guide](USER_GUIDE.md#-student-guide)
Students এর জন্য সম্পূর্ণ guide:
- Quiz কিভাবে নিতে হয়
- Practice mode ব্যবহার
- Leaderboard tracking
- Performance analysis

### 👨‍💼 [Admin User Guide](USER_GUIDE.md#-admin-guide)
Admin দের জন্য সম্পূর্ণ guide:
- Questions upload করা
- Live Quiz schedule করা
- Statistics দেখা
- Database management

### 📋 [Quick Reference Guide](QUICK_REFERENCE.md)
দ্রুত reference এর জন্য:
- Commands reference
- File format examples
- Score calculation
- Troubleshooting tips

---

## 🚀 দ্রুত শুরু করুন

### ছাত্রদের জন্য:
1. Telegram এ **@GNM_ANM_Quiz_Bot** খুঁজুন
2. **Start** button ক্লিক করুন
3. Phone number verify করুন
4. **Quiz নিতে শুরু করুন!**

### Admin দের জন্য:
1. Bot থেকে `/admin` command দিন
2. Admin panel খুলবে
3. **Questions upload করুন** বা **Quiz schedule করুন**
4. **System manage করুন!**

---

## 📚 প্রধান Features

### 📝 Live Quiz
- ⏰ Time-limited competitive exams
- 🏆 Real-time ranking
- 📊 Instant results
- 💡 Full explanations

### 📖 Practice Mode
- ∞ Unlimited attempts
- 📚 Chapter-wise learning
- ⭐ Difficulty levels
- 🎯 Progressive learning

### 🏆 Leaderboard
- 📅 Daily rankings
- 📆 Weekly rankings
- 📊 Monthly rankings
- 🏆 All-time rankings

### 📊 Statistics & Analytics
- 📈 Performance tracking
- 🎯 Accuracy analysis
- 📋 Quiz history
- 🔍 Subject-wise stats

### 👨‍💼 Admin Dashboard
- 📤 Bulk question import
- 📅 Quiz scheduling
- 📢 Broadcasting messages
- 💾 Database backup
- 🔍 User management

---

## 📂 Project Structure

```
Quiz_GnmAnm/
├── app/
│   ├── database/
│   │   ├── connection.py      # Database connection
│   │   └── models.py          # Database models & queries
│   ├── handlers/
│   │   ├── start.py           # Start command handler
│   │   ├── quiz.py            # Quiz handler
│   │   ├── practice.py        # Practice mode
│   │   ├── leaderboard.py     # Leaderboard
│   │   ├── user.py            # User profile
│   │   ├── admin.py           # Admin panel
│   │   ├── admin_dashboard.py # Admin dashboard
│   │   ├── upload.py          # Question upload
│   │   ├── live_exam.py       # Live exams
│   │   ├── notice.py          # Notices
│   │   └── external.py        # External links
│   ├── keyboards/
│   │   ├── main_menu.py       # Main menu buttons
│   │   ├── quiz_keyboard.py   # Quiz buttons
│   │   └── contact.py         # Contact buttons
│   ├── states/
│   │   ├── quiz_states.py     # Quiz FSM states
│   │   └── upload_state.py    # Upload FSM states
│   ├── services/
│   │   ├── importer.py        # File importer
│   │   ├── excel_import.py    # Excel import service
│   │   ├── docx_import.py     # Word import service
│   │   └── txt_import.py      # Text import service
│   └── utils/
│       └── helpers.py         # Utility functions
├── config.py                  # Configuration
├── main.py                    # Bot entry point
├── requirements.txt           # Dependencies
├── USER_GUIDE.md             # User guide
├── QUICK_REFERENCE.md        # Quick reference
└── README.md                 # This file
```

---

## 🛠️ ইনস্টলেশন

### প্রয়োজনীয় জিনিস:
- Python 3.8 বা তার উপরে
- pip (Python package manager)
- Telegram Account
- Bot Token (BotFather থেকে)

### ধাপ 1: Repository Clone করুন
```bash
git clone <repository-url>
cd Quiz_GnmAnm
```

### ধাপ 2: Virtual Environment তৈরি করুন
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# বা
venv\Scripts\activate     # Windows
```

### ধাপ 3: Dependencies Install করুন
```bash
pip install -r requirements.txt
```

### ধাপ 4: Configuration Setup করুন
`.env` ফাইল তৈরি করুন:
```
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_admin_id_here
DATABASE_URL=quiz_database.db
```

### ধাপ 5: Bot চালান
```bash
python main.py
```

---

## 📝 Configuration

### config.py ফাইল
```python
BOT_TOKEN = "your_token_here"           # BotFather থেকে পান
ADMIN_ID = 123456789                    # আপনার Telegram ID
DATABASE_PATH = "data/quiz_database.db" # Database location
MAX_QUESTIONS_PER_QUIZ = 50             # Default questions
```

---

## 🗄️ Database

### Tables:
- **users** - User information
- **questions** - Quiz questions
- **quiz_sessions** - Active quiz sessions
- **quiz_responses** - User answers
- **scheduled_quizzes** - Scheduled live exams
- **exam_results** - Quiz results
- **leaderboard** - Rankings
- **notices** - Announcements

---

## 🤝 কিভাবে অবদান রাখবেন

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📞 সাপোর্ট

### সমস্যা বা প্রশ্ন?
1. [USER_GUIDE.md](USER_GUIDE.md) এর FAQs দেখুন
2. [QUICK_REFERENCE.md](QUICK_REFERENCE.md) চেক করুন
3. Admin এর সাথে যোগাযোগ করুন

---

## 📜 লাইসেন্স

এই প্রজেক্ট private এবং GNM/ANM Students এর জন্য।

---

## 👥 ক্রেডিট

### তৈরিকারী:
- **Developer Team** - GNM ANM Success Learning Academy

### ব্যবহৃত প্রযুক্তি:
- [aiogram](https://github.com/aiogram/aiogram) - Telegram Bot API
- [aiosqlite](https://github.com/omnilib/aiosqlite) - Async SQLite
- [python-docx](https://github.com/python-openxml/python-docx) - Word document handling
- [openpyxl](https://openpyxl.readthedocs.io/) - Excel handling

---

## 🔄 আপডেট হিস্টরি

### v1.0 (2026-07-05)
- ✅ Initial release
- ✅ Live Quiz feature
- ✅ Practice mode
- ✅ Admin dashboard
- ✅ Question upload system
- ✅ Leaderboard
- ✅ User statistics

---

## 🎯 ভবিষ্যতের Features

📋 Planned Features:
- [ ] Video lectures integration
- [ ] Advanced analytics
- [ ] Mobile app version
- [ ] Group quizzes
- [ ] Study materials
- [ ] Custom certificates
- [ ] One-on-one tutoring
- [ ] Progress tracking dashboard

---

## 📊 Statistics

- **Total Questions**: কয়েকটি হাজার
- **Total Users**: বাড়ছে
- **Quiz Attempts**: বৃদ্ধি পাচ্ছে
- **Uptime**: ৯৯%+

---

## 🌟 হাইলাইট

```
✨ User-friendly interface
✨ Real-time leaderboard
✨ Comprehensive analytics
✨ Easy question management
✨ Multiple quiz types
✨ Instant results
✨ Full explanations
✨ Mobile responsive
```

---

## 📅 উল্লেখযোগ্য তারিখ

| ইভেন্ট | তারিখ |
|--------|-------|
| Project শুরু | 2026-07-01 |
| Beta Release | 2026-07-05 |
| Full Launch | TBD |

---

## 🚀 দ্রুত লিংক

- 📖 [User Guide](USER_GUIDE.md) - সম্পূর্ণ ব্যবহারকারী গাইড
- 📋 [Quick Reference](QUICK_REFERENCE.md) - দ্রুত reference গাইড
- 🤖 [Bot](https://t.me/GNM_ANM_Quiz_Bot) - Telegram Bot link
- 📧 Contact - Admin এর সাথে যোগাযোগ করুন

---

**Happy Learning! 🎓**

Last Updated: 2026-07-05
