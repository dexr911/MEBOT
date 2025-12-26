import os
import telebot
import requests
import random
import time
import names

# تأكد من إضافة BOT_TOKEN في Railway Variables
API_TOKEN = os.getenv('BOT_TOKEN8488920682:AAGhoJ-R5q5Xd4nVULrdmSxM2YfSch6j2RUPI_TOKEN)

def get_headers():
    session = requests.Session()
    # استخدام User-Agent حديث جداً لجهاز Galaxy S23
    user_agent = "Mozilla/5.0 (Linux; Android 13; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36"
    
    try:
        # طلب الصفحة الرئيسية أولاً لبناء الثقة
        base_res = session.get("https://www.instagram.com/", headers={"User-Agent": user_agent}, timeout=15)
        csrf = session.cookies.get('csrftoken') or "missing"
        
        headers = {
            'authority': 'www.instagram.com',
            'accept': '*/*',
            'accept-language': 'ar-YE,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.instagram.com',
            'referer': 'https://www.instagram.com/accounts/emailsignup/',
            'user-agent': user_agent,
            'x-csrftoken': csrf,
            'x-ig-app-id': '936619743392459', # ID الثابت لتطبيق الويب
            'x-requested-with': 'XMLHttpRequest',
        }
        return headers, session
    except:
        return None, None

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🛠 جاري فحص الاتصال... أرسل الإيميل للتجربة:")

@bot.message_handler(func=lambda m: True)
def handle_email(message):
    chat_id = message.chat.id
    email = message.text.strip()
    
    msg = bot.send_message(chat_id, "📡 محاولة اختراق حماية انستقرام...")
    
    headers, session = get_headers()
    if not headers or headers['x-csrftoken'] == "missing":
        bot.edit_message_text("❌ انستقرام كشف السيرفر (Railway IP Blocked). الحل الوحيد هو إضافة بروكسي.", chat_id, msg.message_id)
        return

    try:
        data = {'email': email}
        res = session.post('https://www.instagram.com/api/v1/accounts/send_verify_email/', 
                          headers=headers, data=data, timeout=15)
        
        if 'email_sent":true' in res.text:
            bot.edit_message_text(f"✅ نجحت المعجزة! أرسلت الكود إلى {email}. أرسله الآن:", chat_id, msg.message_id)
            # هنا تكمل دالة verify_code السابقة...
        else:
            bot.edit_message_text(f"⚠️ رفض الطلب. الرد:\n`{res.text[:100]}`", chat_id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ اتصال: {e}", chat_id, msg.message_id)

bot.infinity_polling()
