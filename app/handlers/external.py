from aiogram import Router, F
from aiogram.types import Message
from aiogram.utils.markdown import hlink

router = Router()


@router.message(F.text == "🎥 YouTube")
async def youtube_channel(message: Message):
    """Open YouTube channel"""
    
    youtube_link = "https://www.youtube.com/@gnmanm"
    
    text = f"""🎥 **GNM / ANM YOUTUBE CHANNEL**

Subscribe to our channel for:
📚 Complete study material
📖 Chapter-wise lectures
✏️ Tips and tricks
🎯 Exam preparation

{hlink("▶️ SUBSCRIBE NOW", youtube_link)}

Latest Videos:
1. Anatomy - Skeletal System
2. Physiology - Nervous System
3. Pathology - Inflammation

Don't forget to hit the bell icon for notifications!
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = [
        [InlineKeyboardButton(text="▶️ Visit Channel", url=youtube_link)],
        [InlineKeyboardButton(text="🎞️ Latest Videos", callback_data="yt_latest")],
        [InlineKeyboardButton(text="Back", callback_data="yt_back")]
    ]
    
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "yt_latest")
async def latest_videos(callback_query):
    """Show latest videos"""
    
    text = """🎬 **LATEST VIDEOS**

1. 📚 Anatomy - Skeletal System
   Duration: 45:32
   Views: 1.2K
   
2. 📖 Physiology - Nervous System
   Duration: 38:15
   Views: 892
   
3. 🔬 Pathology - Inflammation
   Duration: 52:10
   Views: 756

Subscribe to get more!
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = [[InlineKeyboardButton(text="Back", callback_data="yt_back")]]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=kb)
    await callback_query.answer()


@router.callback_query(F.data == "yt_back")
async def yt_back(callback_query):
    """Back"""
    await callback_query.message.delete()
    await callback_query.answer()


# =====================
# PAID COURSE
# =====================

@router.message(F.text == "💎 Paid Course")
async def paid_course(message: Message):
    """Show paid course options"""
    
    text = """💎 **PREMIUM COURSES**

🔒 Unlock All Features:

📚 **Complete GNM Course Pack**
- All 50 subjects coverage
- 1000+ questions
- Video explanations
- Live doubt sessions
- Certificate included

💰 Price: ₹499/month
   OR ₹4999/year (Save 17%)

📖 **ANM Specialty Course**
- Nursing fundamentals
- Community health
- Advanced topics
- 500+ questions

💰 Price: ₹299/month
   OR ₹2999/year

🎁 **Special Offer**
Get 50% OFF on yearly plans!
Use Coupon: SUMMER50

What would you like to do?
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = [
        [InlineKeyboardButton(text="🛒 Buy GNM Course", callback_data="course_gnm")],
        [InlineKeyboardButton(text="🛒 Buy ANM Course", callback_data="course_anm")],
        [InlineKeyboardButton(text="🎟️ Enter Coupon", callback_data="course_coupon")],
        [InlineKeyboardButton(text="Back", callback_data="course_back")]
    ]
    
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "course_gnm")
async def buy_gnm_course(callback_query):
    """Buy GNM course"""
    
    text = """🛒 **BUY GNM COURSE**

Select your plan:

1️⃣ Monthly - ₹499
   - 1 month validity
   - All features
   - Cancel anytime

2️⃣ Yearly - ₹4999 (Save ₹498!)
   - 12 months validity
   - Priority support
   - Free exam simulations

Select payment method:
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = [
        [InlineKeyboardButton(text="💳 Card/UPI - ₹499", callback_data="pay_gnm_monthly")],
        [InlineKeyboardButton(text="💳 Card/UPI - ₹4999", callback_data="pay_gnm_yearly")],
        [InlineKeyboardButton(text="Back", callback_data="course_back")]
    ]
    
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=kb)
    await callback_query.answer()


@router.callback_query(F.data == "course_anm")
async def buy_anm_course(callback_query):
    """Buy ANM course"""
    
    text = """🛒 **BUY ANM COURSE**

Select your plan:

1️⃣ Monthly - ₹299
   - 1 month validity
   
2️⃣ Yearly - ₹2999 (Save ₹471!)
   - 12 months validity

Select payment method:
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = [
        [InlineKeyboardButton(text="💳 Card/UPI - ₹299", callback_data="pay_anm_monthly")],
        [InlineKeyboardButton(text="💳 Card/UPI - ₹2999", callback_data="pay_anm_yearly")],
        [InlineKeyboardButton(text="Back", callback_data="course_back")]
    ]
    
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=kb)
    await callback_query.answer()


@router.callback_query(F.data == "course_coupon")
async def apply_coupon(callback_query):
    """Apply coupon"""
    
    text = """🎟️ **APPLY COUPON CODE**

Enter your coupon code:

Example: SUMMER50

Type the code to apply discount.
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = [[InlineKeyboardButton(text="Back", callback_data="course_back")]]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=kb)
    await callback_query.answer()


@router.callback_query(F.data.startswith("pay_"))
async def payment_gateway(callback_query):
    """Redirect to payment"""
    
    text = """✅ **PAYMENT PROCESSING**

🔄 Redirecting to payment gateway...

Secure payment by: Razorpay/PayPal

Do not refresh or go back.

Processing order...
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = [[InlineKeyboardButton(text="Cancel", callback_data="course_back")]]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=kb)
    await callback_query.answer("Payment gateway will open in browser...")


@router.callback_query(F.data == "course_back")
async def course_back(callback_query):
    """Back"""
    await callback_query.message.delete()
    await callback_query.answer()
