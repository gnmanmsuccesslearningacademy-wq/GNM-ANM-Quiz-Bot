# GNM/ANM Quiz Bot - Full User Guide

## 🎯 Overview
এই Bot ডিজাইন করা হয়েছে GNM/ANM Student দের জন্য একটি simple কিন্তু powerful Quiz workflow-এর জন্য।

Bot-এর workflow:
- Admin শুধু question upload করবে এবং quiz schedule করবে
- Bot নির্ধারিত সময়ে group-এ announce করবে
- Student button চাপলে private chat-এ quiz চালু হবে
- quiz শেষ হলে student score দেখাবে
- quiz শেষ হওয়ার পর group-এ শুধুমাত্র Top 10 leaderboard যাবে

---

## 📚 Table of Contents
- [Quick Summary](#-quick-summary)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Student Guide](#-student-guide)
- [Admin Guide](#-admin-guide)
- [Quiz Schedule Flow](#-quiz-schedule-flow)
- [Result Flow](#-result-flow)
- [Leaderboard](#-leaderboard)
- [Important Notes](#-important-notes)

---

## ✅ Quick Summary

Bot এখন নিচের ফ্লো ঠিকঠাক চলে:

1. Admin quiz schedule করে
2. Bot নির্ধারিত সময়ে group-এ announce করে
3. Student button চাপলে private chat-এ quiz শুরু হয়
4. Student private quiz দেয়
5. Quiz শেষে final score দেখায়
6. গ্রুপে শুধু top 10 leaderboard প্রকাশ করে

---

## 🛠️ Installation

### Requirements
- Python 3.8 বা তার উপরে
- Telegram bot token
- Admin Telegram ID
- Group chat ID (Bot group-এ add করা আছে)
- `requirements.txt` ফাইল থেকে dependency install

### Setup
```bash
cd Quiz_GnmAnm
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Run the bot
```bash
python main.py
```

---

## ⚙️ Configuration

`.env` ফাইলে নিচের তিনটি ভেরিয়েবল থাকা দরকার:

```env
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_admin_id_here
GROUP_ID=your_group_chat_id_here
```

- `BOT_TOKEN` = BotFather থেকে প্রাপ্ত token
- `ADMIN_ID` = আপনার Telegram user ID
- `GROUP_ID` = গ্রুপের chat ID যেখানে announce হবে

> গ্রুপ আইডি negative number হতে পারে, যেমন `-1001234567890`.

### কিভাবে Bot group-এ add করবেন
1. Telegram এ আপনার target group খুলুন
2. `Add Member` করে **Bot username** যোগ করুন
3. Bot কে `Admin` হিসেবে দিন না-ও, শুধুমাত্র member থাকার জন্য ঠিক আছে
4. group-এ `@username_to_id_bot` বা `@getidsbot` add করুন
   - group settings থেকে `Add Member` ক্লিক করে bot নামটি লিখুন
   - Bot কে group-এ যোগ করুন
5. group এ একটি normal message লিখুন, যেমন `hello`
6. bot-এর private chat-এ যান
   - `@username_to_id_bot` বা `@getidsbot` এ `/start` দিন
   - bot সাধারণত আপনার group message থেকে group ID বের করে দেয়
7. `GROUP_ID` হিসেবে সেই numeric value `.env` ফাইলে বসান

> যদি bot private chat-এ group ID না দেখে, তাহলে group এ `/id` বা `hello` লিখে আবার check করুন।

---

## 👨‍🎓 Student Guide

### 1. Bot Start করুন

- Telegram-এ আপনার bot open করুন
- `/start` দিন
- Bot আপনার নাম সংরক্ষণ করবে
- প্রথমবারে contact share করলে ভালো হয়

### 2. Quiz কীভাবে শুরু হয়

- Bot group-এ announce করবে:
  - `📢 GNM/ANM Daily Live Quiz`
  - `আজকের Quiz শুরু হয়েছে`
  - `⏱ Duration`, `📊 Questions`
  - `🚀 Start Quiz` button
- button চাপলে private chat-এ bot open হবে
- bot automatically বুঝবে quiz ID ধরে

### 3. Private Quiz দিবেন

- প্রথমে quiz বেছে নিতে হবে না
- `Start Quiz` button ক্লিক করলেই quiz শুরু হয়
- প্রশ্ন গুলো private chat-এ sequentially আসবে
- প্রতিটি প্রশ্নের নিচে option button থাকবে
- A/B/C/D এ ক্লিক করুন

### 4. Time Logic

- quiz ঠিক schedule শুরু হওয়ার আগে private quiz শুরু করা যাবে না
- schedule start time থেকে quiz চলবে
- `Duration` অনুযায়ী quiz automatic শেষ হবে
- যদি student সময়ের পরে join করে, তাহলে quiz আর শুরু হবে না
- যদি student সময়ের মধ্যে শুরু করে, তাহলে session end time পর্যন্ত দিতে পারবে

### 5. সম্পন্ন হলে

private chat-এ final result দেখাবে:
- Correct
- Wrong
- Score
- Negative
- Final

### 6. My Result

- `📊 My Result` button চাপলে আপনার quiz history দেখাবে
- আগে যেসব quiz করেছেন তার summary দেখাবে

---

## 👨‍💼 Admin Guide

### 1. Admin Login

- আপনার admin Telegram ID `.env` ফাইলে সেট করতে হবে
- Bot এ `/admin` দিলে admin panel খুলবে

### 2. Quiz Upload

Admin quiz upload process একইয় আছে:
- `📤 Upload Questions` বেছে নিন
- প্রশ্নের ফাইল upload করুন
- Bot questions database-এ সেভ করবে

### 3. Quiz Schedule

- `/admin` তারপর `📅 Schedule Quiz` দিন
- Bot আপনাকে steps দেখাবে

#### Schedule Steps
1. Quiz Name
   - উদাহরণ: `Daily Quiz #25`
2. Exam Name
   - উদাহরণ: `GNM ANM 2027`
3. Date
   - Format: `YYYY-MM-DD`
   - উদাহরণ: `2026-07-05`
4. Time
   - Format: `HH:MM` (24-hour)
   - উদাহরণ: `20:00`
5. Duration
   - মিনিটে দিন, যেমন `20`
6. Questions
   - সংখ্যা, যেমন `20`

### 4. Bot Behavior

- Bot quiz schedule হলে database-এ `pending` রাখে
- schedule time এ bot group-এ announce করে
- announce হলে quiz `active` হয়ে যায়
- announce time শুরু হলে student private থেকে quiz শুরু করবে

### 5. Important

- quiz start time এর আগে আপনি quiz schedule করবেন
- শুধুমাত্র `exam name` যেটা question database-এ আছে, সেটাই valid
- schedule time থেকে quiz শুরু হবে
- quiz end time auto হিসেব করা হবে

---

## 📅 Quiz Schedule Flow

### Database tables

Bot-এ এখন দুইটি প্রধান টেবিল আছে:

1. `quiz_schedule`
   - `id`
   - `quiz_name`
   - `exam`
   - `date`
   - `time`
   - `duration`
   - `question_limit`
   - `status`

2. `quiz_results`
   - `id`
   - `quiz_id`
   - `user_id`
   - `correct`
   - `wrong`
   - `score`
   - `submitted_at`

### Status lifecycle

- `pending` = quiz schedule হয়েছে, announce হওয়ার আগে
- `active` = group announce হয়েছে এবং student quiz session open হবে
- `ended` = quiz duration শেষ হয়েছে এবং leaderboard পাঠানো হয়েছে

---

## 🧠 Result Flow

### Final result দেখাবে

private chat-এ quiz শেষ হলে:
- Correct
- Wrong
- Score
- Negative
- Final

### Score calculation

- সঠিক উত্তর পেলে question marks যোগ হবে
- ভুল উত্তর হলে negative marks যোগ হবে
- শেষ ফলাফল `positive - negative` হিসেবে দেখানো হবে

### Database লেখে

- `quiz_results` টেবিলে result সেভ হয়
- `quiz_history` টেবিলে user history সেভ হয়
- `users` table-এ summary update হতে পারে

---

## 🏆 Leaderboard

### Group leaderboard

Quiz যখন `active` থেকে `ended` হবে:
- Bot automatic group-এ Top 10 leaderboard পাঠাবে
- শুধুমাত্র group-এ Top 10 publish হবে
- student private chat-এ score দেখলে group clean থাকবে

### Leaderboard format

```
🏆 Daily Quiz Result

🥇 Rahul - 19
🥈 Anup - 18
🥉 Riya - 17
```

---

## 📌 Important Notes

- Bot খুবই simple রাখতে হয়েছে — extra features বাদ দেওয়া হয়েছে
- প্রয়োজনীয় হচ্ছে শুধুমাত্র quiz upload + schedule
- group announce হবে only scheduled quiz time-এ
- quiz private chat-এ হবে, group-এ direct questions যাবে না
- Bot stability এর জন্য বেশি load নেই

---

## ✅ Complete Phases

1. Phase 1: `quiz_schedule` + `quiz_results` tables ✅
2. Phase 2: Admin schedule command ✅
3. Phase 3: Auto scheduler ✅
4. Phase 4: Deep link start ✅
5. Phase 5: Result save ✅
6. Phase 6: Leaderboard ✅

---

## 🧪 Testing Checklist

1. `/admin` দিয়ে quiz schedule করুন
2. নির্ধারিত সময়ে group-এ announce হয় কিনা দেখুন
3. `Start Quiz` button click করলে private chat open হয় কিনা দেখুন
4. quiz নিয়ে score বের হচ্ছে কিনা পরীক্ষা করুন
5. quiz শেষ হলে group-এ Top 10 leaderboard যাচ্ছে কিনা দেখুন

---

## 📞 Support

- যদি কোনো issue আসে, প্রথমে bot log এবং `.env` ভেরিয়েবল চেক করুন
- `GROUP_ID`, `ADMIN_ID`, `BOT_TOKEN` সঠিক আছে কিনা দেখুন
- quiz schedule সময়টি সঠিক `YYYY-MM-DD HH:MM` ফর্ম্যাটে দিন

---

## ✨ Final Note
এই guide-এ যেইটি দরকার সব লেখার চেষ্টা করেছি যাতে আপনার Bot ব্যবহার করা সহজ হয়।

Bot এখন ready for production workflow:
- Admin upload -> schedule -> auto announce -> private quiz -> result -> group leaderboard
