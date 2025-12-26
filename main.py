import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import random, string, time, os, names, requests

# نفس المتغيرات والألوان (ملف IG-Maker.py السابق)
rd, gn, lgn, yw, lrd, be, pe = '\033[00;31m', '\033[00;32m', '\033[01;32m', '\033[01;33m', '\033[01;31m', '\033[94m', '\033[01;35m'
cn, k, g = '\033[00;36m', '\033[90m','\033[38;5;130m'

# نفس الدوال من الكود السابق (get_headers, Get_UserName, Send_SMS, Validate_Code, Create_Acc)

# متغيرات التخزين المؤقت
user_data = {}

# أوامر البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔐 *بوت إنشاء حسابات إنستغرام*\n\n"
        "📧 أرسل بريدك الإلكتروني لبدء العملية\n"
        "⚠️ هذا للاستخدام التعليمي فقط!",
        parse_mode='Markdown'
    )

async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text
    user_id = update.effective_user.id
    
    # تخزين بيانات المستخدم
    user_data[user_id] = {'email': email, 'step': 'email'}
    
    # إنشاء headers (بنفس الدوال الأصلية)
    headers = get_headers(Country='US', Language='en')
    
    # إرسال الرمز
    result = Send_SMS(headers, email)
    
    if 'email_sent":true' in result:
        user_data[user_id]['headers'] = headers
        await update.message.reply_text(
            f"✅ تم إرسال رمز التحقق إلى: {email}\n"
            "📩 الرجاء إرسال الرمز المكون من 6 أرقام"
        )
    else:
        await update.message.reply_text("❌ فشل في إرسال الرمز!")

async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    code = update.message.text
    
    if user_id not in user_data:
        await update.message.reply_text("❌ الرجاء البدء من جديد باستخدام /start")
        return
    
    headers = user_data[user_id]['headers']
    email = user_data[user_id]['email']
    
    # التحقق من الرمز
    response = Validate_Code(headers, email, code)
    
    if response and 'status":"ok' in response.text:
        signup_code = response.json()['signup_code']
        
        # إنشاء الحساب
        Create_Acc(headers, email, signup_code)
        
        # هنا يمكنك إرسال النتائج للمستخدم
        await update.message.reply_text(
            "✅ تم إنشاء الحساب بنجاح!\n"
            "🔑 تم حفظ البيانات في السجلات"
        )
        
        # مسح بيانات المستخدم
        del user_data[user_id]
    else:
        await update.message.reply_text("❌ رمز تحقق غير صحيح!")

# الدالة الرئيسية
def main():
    # توكن البوت الخاص بك
    TOKEN = "8488920682:AAEp45yVtWWuVWEIj8eV2P07uwDkXWrNHwI"
    
    # إنشاء التطبيق
    application = Application.builder().token(TOKEN).build()
    
    # إضافة المعالجات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # تشغيل البوت
    application.run_polling()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id in user_data:
        step = user_data[user_id].get('step', '')
        
        if step == 'email':
            await handle_email(update, context)
            user_data[user_id]['step'] = 'code'
        elif step == 'code':
            await handle_code(update, context)
    else:
        # إذا كان النص يشبه بريد إلكتروني
        if '@' in update.message.text and '.' in update.message.text:
            await handle_email(update, context)
        else:
            await update.message.reply_text("📧 الرجاء إرسال بريدك الإلكتروني أولا")

if __name__ == "__main__":
    main()
