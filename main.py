import asyncio
import random
import string
import time
import os
import names
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========== نفس دوال IG-Maker.py الأصلية ==========
rd, gn, lgn, yw, lrd, be, pe = '\033[00;31m', '\033[00;32m', '\033[01;32m', '\033[01;33m', '\033[01;31m', '\033[94m', '\033[01;35m'
cn, k, g = '\033[00;36m', '\033[90m','\033[38;5;130m'
true = f'{rd}[{lgn}+{rd}]{gn} '
false = f'{rd}[{lrd}-{rd}] '

proxies = None

def get_headers(Country, Language):
    while True:
        try:
            an_agent = f'Mozilla/5.0 (Linux; Android {random.randint(9,13)}; {"".join(random.choices(string.ascii_uppercase, k=3))}{random.randint(111,999)}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36'
            
            res = requests.get("https://www.facebook.com/", 
                             headers={'user-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'},
                             proxies=proxies, timeout=30)
            js_datr = res.text.split('["_js_datr","')[1].split('",')[0]
            
            r = requests.get('https://www.instagram.com/api/v1/web/accounts/login/ajax/',
                           headers={'user-agent': an_agent},
                           proxies=proxies, timeout=30).cookies

            headers1 = {
                'authority': 'www.instagram.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': f'{Language}-{Country},en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
                'cookie': f'dpr=3; csrftoken={r["csrftoken"]}; mid={r["mid"]}; ig_nrcb=1; ig_did={r["ig_did"]}; datr={js_datr}',
                'sec-ch-prefers-color-scheme': 'light',
                'sec-ch-ua': '"Chromium";v="111", "Not(A:Brand";v="8"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': an_agent,
                'viewport-width': '980',
            }
            
            response1 = requests.get('https://www.instagram.com/', headers=headers1, proxies=proxies, timeout=30)
            appid = response1.text.split('APP_ID":"')[1].split('"')[0]
            rollout = response1.text.split('rollout_hash":"')[1].split('"')[0]
            
            headers = {
                'authority': 'www.instagram.com',
                'accept': '*/*',
                'accept-language': f'{Language}-{Country},en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
                'content-type': 'application/x-www-form-urlencoded',
                'cookie': f'dpr=3; csrftoken={r["csrftoken"]}; mid={r["mid"]}; ig_nrcb=1; ig_did={r["ig_did"]}; datr={js_datr}',
                'origin': 'https://www.instagram.com',
                'referer': 'https://www.instagram.com/accounts/signup/email/',
                'sec-ch-prefers-color-scheme': 'light',
                'sec-ch-ua': '"Chromium";v="111", "Not(A:Brand";v="8"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': an_agent,
                'viewport-width': '360',
                'x-asbd-id': '198387',
                'x-csrftoken': r["csrftoken"],
                'x-ig-app-id': str(appid),
                'x-ig-www-claim': '0',
                'x-instagram-ajax': str(rollout),
                'x-requested-with': 'XMLHttpRequest',
                'x-web-device-id': r["ig_did"],
            }
            return headers
        except Exception as E:
            print(f'{false}Error in Connection: {E}')
            time.sleep(2)

# الدوال الأخرى (Get_UserName, Send_SMS, Validate_Code, Create_Acc)
# ... (ضع الدوال الأصلية هنا دون تغيير)

# ========== جزء بوت تليجرام ==========
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /start"""
    try:
        user = update.effective_user
        await update.message.reply_text(
            f"مرحباً {user.first_name}! 👋\n\n"
            "🔐 *بوت إنشاء حسابات إنستغرام*\n\n"
            "📧 **أرسل بريدك الإلكتروني** لبدء العملية\n\n"
            "⚠️ *ملاحظة:* هذا الكود للأغراض التعليمية فقط\n"
            "والاستخدام الفعلي قد ينتهك شروط الخدمة",
            parse_mode='Markdown'
        )
        print(f"{true}User {user.id} started the bot")
    except Exception as e:
        print(f"{false}Error in start: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الرسائل العامة"""
    try:
        user_id = update.effective_user.id
        text = update.message.text.strip()
        
        print(f"{true}Message from {user_id}: {text}")
        
        # إذا كان النص يحتوي على @ فهو بريد إلكتروني
        if '@' in text and '.' in text and user_id not in user_data:
            await process_email(update, text, user_id)
        elif user_id in user_data:
            if user_data[user_id]['step'] == 'code':
                await process_code(update, text, user_id)
        else:
            await update.message.reply_text(
                "📧 الرجاء إرسال بريدك الإلكتروني أولاً\n"
                "أو استخدم /start للبدء"
            )
    except Exception as e:
        print(f"{false}Error in handle_message: {e}")
        await update.message.reply_text("❌ حدث خطأ، حاول مرة أخرى")

async def process_email(update: Update, email: str, user_id: int):
    """معالجة البريد الإلكتروني"""
    try:
        await update.message.reply_text("⏳ جاري التحضير...")
        
        headers = get_headers(Country='US', Language='en')
        result = Send_SMS(headers, email)
        
        if result and 'email_sent":true' in result:
            user_data[user_id] = {
                'email': email,
                'headers': headers,
                'step': 'code'
            }
            await update.message.reply_text(
                f"✅ تم إرسال رمز التحقق إلى:\n`{email}`\n\n"
                "📩 **أرسل الرمز المكون من 6 أرقام**",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("❌ فشل في إرسال الرمز!")
    except Exception as e:
        print(f"{false}Error in process_email: {e}")
        await update.message.reply_text("❌ حدث خطأ أثناء إرسال الرمز")

async def process_code(update: Update, code: str, user_id: int):
    """معالجة رمز التحقق"""
    try:
        if user_id not in user_data:
            await update.message.reply_text("❌ جلسة منتهية، ابدأ من جديد")
            return
        
        email = user_data[user_id]['email']
        headers = user_data[user_id]['headers']
        
        await update.message.reply_text("⏳ جاري التحقق من الرمز...")
        
        response = Validate_Code(headers, email, code)
        
        if response and hasattr(response, 'text') and 'status":"ok' in response.text:
            signup_code = response.json()['signup_code']
            await update.message.reply_text("✅ الرمز صحيح! جاري إنشاء الحساب...")
            
            # إنشاء الحساب
            Create_Acc(headers, email, signup_code)
            
            await update.message.reply_text(
                "✨ *تم إنشاء الحساب بنجاح!*\n\n"
                "🔑 تم حفظ البيانات في سجلات النظام\n"
                "⚠️ تذكر أن هذا للأغراض التعليمية فقط",
                parse_mode='Markdown'
            )
            
            # تنظيف البيانات
            if user_id in user_data:
                del user_data[user_id]
        else:
            await update.message.reply_text("❌ رمز تحقق غير صحيح!")
    except Exception as e:
        print(f"{false}Error in process_code: {e}")
        await update.message.reply_text("❌ حدث خطأ أثناء التحقق")

def main():
    """الدالة الرئيسية لتشغيل البوت"""
    # 🔧 ضع توكن البوت هنا
    TOKEN = "8488920682:AAGhoJ-R5q5Xd4nVULrdmSxM2YfSch6j2RU"  # استبدل هذا بالتوكن الحقيقي
    
    print(f"{true}Starting Telegram Bot...")
    
    try:
        # إنشاء التطبيق
        application = Application.builder().token(TOKEN).build()
        
        # إضافة المعالجات
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print(f"{true}Bot is running...")
        print(f"{true}Press Ctrl+C to stop")
        
        # تشغيل البوت
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        print(f"{false}Fatal error: {e}")

if __name__ == "__main__":
    main()
