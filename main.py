import os
import telebot
import requests
import random
import string
import time
import names

# جلب التوكن من Railway Variables
API_TOKEN = os.getenv('8488920682:AAGhoJ-R5q5Xd4nVULrdmSxM2YfSch6j2RU')
bot = telebot.TeleBot(API_TOKEN)

def get_headers(Country='US', Language='en'):
    # جلسة Requests للحفاظ على الـ Cookies تلقائياً
    session = requests.Session()
    try:
        an_agent = f'Mozilla/5.0 (Linux; Android {random.randint(9,13)}; SM-G{random.randint(900,999)}F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36'
        
        # محاكاة الدخول من رابط خارجي لتضليل انستقرام
        res = session.get("https://www.google.com/search?q=instagram+signup", headers={'user-agent': an_agent}, timeout=20)
        
        # طلب الصفحة الرئيسية لجلب الـ Cookies الأساسية
        r_init = session.get('https://www.instagram.com/accounts/emailsignup/', headers={'user-agent': an_agent}, timeout=20)
        
        # استخراج البيانات اللازمة من الصفحة
        try:
            appid = r_init.text.split('APP_ID":"')[1].split('"')[0]
            rollout = r_init.text.split('rollout_hash":"')[1].split('"')[0]
            csrf = r_init.text.split('csrf_token":"')[1].split('"')[0]
        except:
            # قيم افتراضية في حال فشل الاستخراج
            appid = "936619743392459"
            rollout = "1"
            csrf = session.cookies.get('csrftoken', '')

        headers = {
            'authority': 'www.instagram.com',
            'accept': '*/*',
            'accept-language': 'ar,en-US;q=0.9,en;q=0.8',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.instagram.com',
            'referer': 'https://www.instagram.com/accounts/emailsignup/',
            'user-agent': an_agent,
            'x-asbd-id': '129477',
            'x-csrftoken': csrf,
            'x-ig-app-id': str(appid),
            'x-instagram-ajax': str(rollout),
            'x-requested-with': 'XMLHttpRequest',
        }
        return headers, session
    except Exception as e:
        print(f"Error: {e}")
        return None, None

# --- إدارة الجلسات ---
user_sessions = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 أهلاً بك! أنا بوت إنشاء حسابات انستقرام.\nأرسل البريد الإلكتروني الآن:")

@bot.message_handler(func=lambda m: True)
def handle_email(message):
    chat_id = message.chat.id
    email = message.text.strip()

    if "@" not in email:
        bot.reply_to(message, "❌ البريد غير صحيح.")
        return

    msg = bot.send_message(chat_id, "⏳ جاري محاولة الاتصال بانستقرام...")
    
    headers, session = get_headers()
    if not headers:
        bot.edit_message_text("❌ انستقرام يرفض الاتصال من هذا السيرفر حالياً. جرب لاحقاً أو استخدم بروكسي.", chat_id, msg.message_id)
        return

    try:
        # إرسال الكود
        data = {'email': email}
        # تحديث الـ CSRF من الكوكيز الحقيقية
        headers['x-csrftoken'] = session.cookies.get('csrftoken', headers['x-csrftoken'])
        
        response = session.post('https://www.instagram.com/api/v1/accounts/send_verify_email/', 
                                headers=headers, data=data, timeout=20)
        
        if 'email_sent":true' in response.text:
            user_sessions[chat_id] = {'email': email, 'headers': headers, 'session': session}
            bot.edit_message_text(f"📩 أرسلت الكود إلى {email}\nأرسل الكود هنا:", chat_id, msg.message_id)
            bot.register_next_step_handler(message, verify_code)
        else:
            bot.edit_message_text(f"⚠️ انستقرام رفض الإرسال:\n`{response.text[:100]}`", chat_id, msg.message_id, parse_mode="Markdown")
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ: {e}", chat_id, msg.message_id)

def verify_code(message):
    chat_id = message.chat.id
    code = message.text.strip()
    
    if chat_id not in user_sessions: return

    s_data = user_sessions[chat_id]
    session = s_data['session']
    headers = s_data['headers']
    
    msg = bot.send_message(chat_id, "⏳ جاري التحقق...")

    try:
        headers['referer'] = 'https://www.instagram.com/accounts/signup/emailConfirmation/'
        data = {'code': code, 'email': s_data['email']}
        
        res = session.post('https://www.instagram.com/api/v1/accounts/check_confirmation_code/', 
                          headers=headers, data=data, timeout=20)
        
        if 'status":"ok' in res.text:
            signup_code = res.json()['signup_code']
            
            # تكملة البيانات تلقائياً
            name = names.get_full_name().replace(" ", "_").lower()
            pwd = "".join(random.choices(string.ascii_letters + string.digits, k=10))
            
            # إنشاء الحساب
            create_data = {
                'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{round(time.time())}:{pwd}',
                'email': s_data['email'],
                'username': name + str(random.randint(10,99)),
                'first_name': names.get_first_name(),
                'month': random.randint(1,12), 'day': random.randint(1,28), 'year': random.randint(1995,2005),
                'client_id': session.cookies.get('mid'),
                'seamless_login_enabled': '1',
                'tos_version': 'row',
                'force_sign_up_code': signup_code,
            }
            
            final = session.post('https://www.instagram.com/api/v1/web/accounts/web_create_ajax/', 
                                headers=headers, data=create_data, timeout=20)
            
            if '"account_created":true' in final.text:
                bot.edit_message_text(f"✅ تم الإنشاء!\n👤 اليوزر: `{create_data['username']}`\n🔑 الباس: `{pwd}`", chat_id, msg.message_id, parse_mode="Markdown")
            else:
                bot.edit_message_text(f"❌ فشل الإنشاء النهائي: {final.text[:100]}", chat_id, msg.message_id)
        else:
            bot.edit_message_text("❌ الكود غلط.", chat_id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ: {e}", chat_id, msg.message_id)

bot.infinity_polling()
