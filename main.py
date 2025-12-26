import telebot
import requests
import random
import string
import time
import names
import os
from telebot import types

# --- إعدادات البوت ---
API_TOKEN = '8488920682:AAGhoJ-R5q5Xd4nVULrdmSxM2YfSch6j2RU' # استبدله بالتوكن الخاص بك
bot = telebot.TeleBot(API_TOKEN)

# قاموس لتخزين بيانات المستخدمين مؤقتاً
user_data = {}

# --- الدوال المساعدة (نفس منطق الكود الأصلي) ---

def get_headers(Country='US', Language='en'):
    try:
        an_agent = f'Mozilla/5.0 (Linux; Android {random.randint(9,13)}; {"".join(random.choices(string.ascii_uppercase, k=3))}{random.randint(111,999)}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36'
        
        # الحصول على datr من فيسبوك
        res = requests.get("https://www.facebook.com/", headers={'user-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}, timeout=30)
        js_datr = res.text.split('["_js_datr","')[1].split('",')[0]
        
        # الحصول على cookies من انستقرام
        r = requests.get('https://www.instagram.com/api/v1/web/accounts/login/ajax/', headers={'user-agent': an_agent}, timeout=30).cookies
        
        # الحصول على appid و rollout_hash
        headers_init = {
            'authority': 'www.instagram.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': f'{Language}-{Country},en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
            'cookie': f'dpr=3; csrftoken={r["csrftoken"]}; mid={r["mid"]}; ig_nrcb=1; ig_did={r["ig_did"]}; datr={js_datr}',
            'user-agent': an_agent,
        }
        response1 = requests.get('https://www.instagram.com/', headers=headers_init, timeout=30)
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
            'user-agent': an_agent,
            'x-csrftoken': r["csrftoken"],
            'x-ig-app-id': str(appid),
            'x-instagram-ajax': str(rollout),
            'x-requested-with': 'XMLHttpRequest',
            'x-web-device-id': r["ig_did"],
        }
        return headers
    except:
        return None

def Get_UserName(Headers, Name, Email):
    try:
        data = {'email': Email, 'name': Name + str(random.randint(1, 99))}
        response = requests.post('https://www.instagram.com/api/v1/web/accounts/username_suggestions/', headers=Headers, data=data, timeout=30)
        if 'status":"ok' in response.text:
            return random.choice(response.json()['suggestions'])
    except: return Name + str(random.randint(100, 999))

# --- أوامر البوت ---

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "👋 أهلاً بك في بوت إنشاء حسابات انستقرام.\n\nأرسل الآن **البريد الإلكتروني** الذي تريد استخدامه:")
    bot.register_next_step_handler(message, process_email)

def process_email(message):
    email = message.text
    chat_id = message.chat.id
    
    msg = bot.send_message(chat_id, "⏳ جاري تحضير البيانات وطلب رمز التحقق...")
    
    headers = get_headers()
    if not headers:
        bot.edit_message_text("❌ فشل الاتصال بخوادم انستقرام. حاول لاحقاً.", chat_id, msg.message_id)
        return

    # محاولة إرسال الرمز
    try:
        data = {
            'device_id': headers['cookie'].split('mid=')[1].split(';')[0],
            'email': email,
        }
        response = requests.post('https://www.instagram.com/api/v1/accounts/send_verify_email/', headers=headers, data=data, timeout=30)
        
        if 'email_sent":true' in response.text:
            user_data[chat_id] = {'email': email, 'headers': headers}
            bot.edit_message_text(f"✅ تم إرسال رمز التحقق إلى: {email}\n\nأرسل الرمز المكون من 6 أرقام الآن:", chat_id, msg.message_id)
            bot.register_next_step_handler(message, process_code)
        else:
            bot.edit_message_text(f"❌ لم يرسل انستقرام الرمز. السبب:\n{response.text[:200]}", chat_id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ غير متوقع: {str(e)}", chat_id, msg.message_id)

def process_code(message):
    chat_id = message.chat.id
    code = message.text
    
    if chat_id not in user_data:
        bot.send_message(chat_id, "⚠️ حدث خطأ في الجلسة، ابدأ من جديد باستخدام /start")
        return

    email = user_data[chat_id]['email']
    headers = user_data[chat_id]['headers']
    
    msg = bot.send_message(chat_id, "🔄 جاري التحقق من الرمز وإنشاء الحساب...")

    try:
        # التحقق من الكود
        headers['referer'] = 'https://www.instagram.com/accounts/signup/emailConfirmation/'
        val_data = {
            'code': code,
            'device_id': headers['cookie'].split('mid=')[1].split(';')[0],
            'email': email,
        }
        res_val = requests.post('https://www.instagram.com/api/v1/accounts/check_confirmation_code/', headers=headers, data=val_data, timeout=30)
        
        if 'status":"ok' in res_val.text:
            signup_code = res_val.json()['signup_code']
            
            # إنشاء الحساب
            firstname = names.get_first_name()
            username = Get_UserName(headers, firstname, email)
            password = firstname.strip() + '@' + str(random.randint(111, 999))
            
            create_data = {
                'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{round(time.time())}:{password}',
                'email': email,
                'username': username,
                'first_name': firstname,
                'month': random.randint(1, 12),
                'day': random.randint(1, 28),
                'year': random.randint(1990, 2001),
                'client_id': headers['cookie'].split('mid=')[1].split(';')[0],
                'seamless_login_enabled': '1',
                'tos_version': 'row',
                'force_sign_up_code': signup_code,
            }
            
            res_create = requests.post('https://www.instagram.com/api/v1/web/accounts/web_create_ajax/', headers=headers, data=create_data, timeout=30)
            
            if '"account_created":true' in res_create.text:
                result = (
                    f"🎉 **تم إنشاء الحساب بنجاح!**\n\n"
                    f"👤 **Username:** `{username}`\n"
                    f"🔑 **Password:** `{password}`\n\n"
                    f"⚙️ **SessionID:** `{res_create.cookies.get('sessionid', 'N/A')}`\n"
                )
                bot.edit_message_text(result, chat_id, msg.message_id, parse_mode="Markdown")
            else:
                bot.edit_message_text(f"❌ فشل إنشاء الحساب النهائي:\n{res_create.text[:200]}", chat_id, msg.message_id)
        else:
            bot.edit_message_text("❌ الرمز غير صحيح أو انتهت صلاحيته.", chat_id, msg.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ: {str(e)}", chat_id, msg.message_id)

print("البوت يعمل الآن...")
bot.infinity_polling()
