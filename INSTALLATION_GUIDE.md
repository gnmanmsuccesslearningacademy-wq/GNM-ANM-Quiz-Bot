# 🔧 Installation & Setup Guide

## 📋 বিষয়বস্তু
- [সিস্টেম প্রয়োজনীয়তা](#-সিস্টেম-প্রয়োজনীয়তা)
- [ধাপে ধাপে ইনস্টলেশন](#-ধাপে-ধাপে-ইনস্টলেশন)
- [Bot Configuration](#-bot-configuration)
- [প্রথম চালু](#-প্রথম-চালু)
- [Troubleshooting](#-troubleshooting)

---

## 💻 সিস্টেম প্রয়োজনীয়তা

### মিনিমাম সিস্টেম:
- **OS**: Windows 10/11, macOS, Linux
- **Python**: 3.8 বা উপরে
- **RAM**: 512 MB (প্রস্তাবিত 2 GB)
- **Storage**: 1 GB (database এবং files এর জন্য)
- **Internet**: সবসময় থাকা দরকার

### Python Check করুন:
```bash
python --version
# Output: Python 3.8.0 বা তার উপরে
```

---

## 🚀 ধাপে ধাপে ইনস্টলেশন

### ✅ ধাপ 1: Python ইনস্টল করুন

**Windows এ:**
1. https://www.python.org/downloads/ এ যান
2. **"Download Python 3.x"** ক্লিক করুন
3. Installer run করুন
4. **"Add Python to PATH"** এ চেক দিন
5. **"Install Now"** ক্লিক করুন

**macOS এ:**
```bash
brew install python@3.9
```

**Linux এ:**
```bash
sudo apt-get install python3 python3-pip
```

### ✅ ধাপ 2: Repository Clone করুন

```bash
# Repository download করুন
git clone <repository-url>

# Folder এ যান
cd Quiz_GnmAnm
```

### ✅ ধাপ 3: Virtual Environment তৈরি করুন

**Windows এ:**
```bash
# Virtual environment তৈরি করুন
python -m venv venv

# Activate করুন
venv\Scripts\activate

# Activate হলে prompt এ (venv) দেখাবে
```

**macOS/Linux এ:**
```bash
# Virtual environment তৈরি করুন
python3 -m venv venv

# Activate করুন
source venv/bin/activate

# Activate হলে prompt এ (venv) দেখাবে
```

### ✅ ধাপ 4: Dependencies Install করুন

```bash
# requirements.txt থেকে সব প্যাকেজ install করুন
pip install -r requirements.txt
```

**সময় লাগবে:** 2-5 মিনিট

**যদি error আসে:**
```bash
# pip update করুন
pip install --upgrade pip

# আবার চেষ্টা করুন
pip install -r requirements.txt
```

### ✅ ধাপ 5: .env File তৈরি করুন

**Windows এ (Command Prompt):**
```bash
echo. > .env
```

**macOS/Linux এ:**
```bash
touch .env
```

**Text Editor এ খুলুন এবং লিখুন:**
```env
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_admin_user_id_here
DATABASE_URL=data/quiz_database.db
```

---

## 🤖 Bot Configuration

### Step 1: Telegram Bot তৈরি করুন

1. **Telegram এ BotFather খুঁজুন** (@BotFather)
2. **/start** message পাঠান
3. **/newbot** command দিন
4. Bot এর নাম দিন (যেমন: GNM ANM Quiz Bot)
5. Bot এর username দিন (যেমন: gnm_anm_quiz_bot)
6. **Bot Token পাবেন** - এটি copy করুন

### Step 2: আপনার Admin ID পান

1. **InstanceChecker Bot খুঁজুন** (@InstanceCheckerBot)
2. **/start** message পাঠান
3. **আপনার User ID পাবেন** - এটি copy করুন

### Step 3: .env File Update করুন

**.env ফাইলে লিখুন:**
```env
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
ADMIN_ID=987654321
DATABASE_URL=data/quiz_database.db
```

**Example:**
```
✅ BOT_TOKEN - BotFather থেকে পান (দীর্ঘ নম্বর)
✅ ADMIN_ID - আপনার Telegram ID (9-10 digit number)
✅ DATABASE_URL - database file location
```

---

## 🎯 প্রথম চালু

### Step 1: Database Initialize করুন

```bash
# প্রথমে virtual environment activate আছে কিনা চেক করুন
# (venv) দেখাবে তাহলে সব ঠিক

# Database tables তৈরি করুন
python insert_test_data.py
```

**Output হওয়া উচিত:**
```
====================================
   Database Tables Created
====================================
```

### Step 2: Bot চালান

```bash
# Bot start করুন
python main.py
```

**সফল Output:**
```
====================================
   GNM ANM QUIZ BOT STARTED
====================================
```

**যদি এই message দেখেন তাহলে সব ঠিক আছে!**

---

## ✅ সেটআপ যাচাই করুন

### Bot Test করুন:

1. **Telegram এ আপনার Bot খুঁজুন** (@bot_username)
2. **/start** command দিন
3. Bot respond করবে - যদি করে তাহলে সেটআপ সফল!

### Admin Panel Test করুন:

```bash
/admin
```

Admin ID এ login করলে admin dashboard দেখতে পাবেন।

---

## 🐛 Troubleshooting

### সমস্যা 1: "ModuleNotFoundError"
```bash
❌ Error: ModuleNotFoundError: No module named 'aiogram'

✅ সমাধান:
pip install -r requirements.txt
```

### সমস্যা 2: "KeyError" or Bot responds না
```bash
❌ Error: KeyError: 'BOT_TOKEN'

✅ সমাধান:
1. .env file পরীক্ষা করুন
2. BOT_TOKEN সঠিক আছে কিনা check করুন
3. Bot restart করুন
```

### সমস্যা 3: Database error
```bash
❌ Error: sqlite3.DatabaseError

✅ সমাধান:
1. data folder আছে কিনা check করুন
2. python insert_test_data.py run করুন
3. Bot restart করুন
```

### সমস্যা 4: Port already in use
```bash
❌ Error: Address already in use

✅ সমাধান:
1. অন্য python process বন্ধ করুন
2. Computer restart করুন
3. Different terminal এ চেষ্টা করুন
```

### সমস্যা 5: Bot hangs/freezes
```bash
❌ Bot response দিচ্ছে না

✅ সমাধান:
1. Ctrl+C দিয়ে bot stop করুন
2. Internet connection check করুন
3. Bot টোকেন valid আছে কিনা check করুন
4. Bot restart করুন
```

---

## 📋 Setup Checklist

Bot চালানোর আগে এই checklist complete করুন:

```
✅ Python 3.8+ installed
✅ Repository cloned
✅ Virtual environment created
✅ Virtual environment activated
✅ requirements.txt installed
✅ .env file created
✅ BOT_TOKEN added to .env
✅ ADMIN_ID added to .env
✅ Database initialized
✅ Bot test করা হয়েছে
```

---

## 🚀 Production Deployment

### Live Server এ Deploy করার জন্য:

#### Option 1: Heroku এ Deploy করুন
1. Heroku account তৈরি করুন
2. Procfile তৈরি করুন
3. `git push heroku main`

#### Option 2: VPS এ Deploy করুন
1. Linux VPS rent করুন
2. Python install করুন
3. Git clone করুন
4. `nohup python main.py &` দিয়ে চালান

#### Option 3: Cloud services (AWS, Google Cloud, etc.)

---

## 🔐 Security Setup

### .env File সুরক্ষা:
```bash
# .gitignore এ add করুন
echo ".env" >> .gitignore
```

### Bot Token সুরক্ষা:
- Token public করবেন না
- GitHub এ commit করবেন না
- শুধু .env এ রাখুন

### Database সুরক্ষা:
- Regular backup নিন
- Download করে safe রাখুন

---

## 📝 Maintenance Commands

### Bot restart করুন:
```bash
# Ctrl+C দিয়ে stop করুন
# তারপর আবার python main.py দিন
```

### Virtual environment deactivate করুন:
```bash
deactivate
```

### Database backup নিন:
```bash
# data folder copy করুন
# অথবা admin panel থেকে backup নিন
```

### Logs দেখুন:
```bash
# Bot output follow করুন
# সরাসরি terminal এ দেখা যাবে
```

---

## 🎓 Next Steps

সেটআপ সম্পন্ন হলে:

1. **[USER_GUIDE.md](USER_GUIDE.md)** পড়ুন
2. **Questions Upload করুন** (`/upload` command)
3. **Quiz Schedule করুন** (`/admin` → Schedule Quiz)
4. **Students add করুন**
5. **System monitor করুন**

---

## 📞 সাহায্য প্রয়োজন?

### Common Issues:
- 🔗 [Troubleshooting](#-troubleshooting)
- 📖 [USER_GUIDE.md](USER_GUIDE.md)
- 📋 [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

---

## 🎉 সেটআপ সম্পন্ন!

আপনার GNM ANM Quiz Bot এখন **LIVE** এবং **READY TO USE**! 🚀

**Happy Teaching & Learning!** 📚

---

**Last Updated:** 2026-07-05  
**Version:** 1.0  
**Created for:** GNM ANM Success Learning Academy
