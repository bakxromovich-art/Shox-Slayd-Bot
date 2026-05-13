import telebot
from telebot import types
import sqlite3
import config

bot = telebot.TeleBot(config.TOKEN)

def get_db():
    conn = sqlite3.connect("bot_database.db", check_same_thread=False)
    return conn, conn.cursor()

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    conn, cursor = get_db()
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (uid,))
    conn.commit()
    conn.close()
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📚 Xizmatlar", "💰 Hisobni to'ldirish")
    markup.add("🌐 HEMIS tizimi", "👤 Kabinet")
    if uid == config.ADMIN_ID:
        markup.add("👑 Admin Panel")
    
    bot.send_message(message.chat.id, f"Salom, {message.from_user.first_name}! Botga xush kelibsiz.", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "💰 Hisobni to'ldirish")
def fill_balance(message):
    msg = bot.send_message(message.chat.id, "To'lov miqdorini kiriting (so'mda):\nMasalan: 10000")
    bot.register_next_step_handler(msg, process_payment)

def process_payment(message):
    try:
        amount = int(message.text)
        uid = message.from_user.id
        conn, cursor = get_db()
        cursor.execute("INSERT INTO payments (user_id, amount) VALUES (?, ?)", (uid, amount))
        pay_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        bot.send_message(message.chat.id, f"Sizning #{pay_id} raqamli so'rovingiz adminga yuborildi. Tasdiqlashni kuting.")
        
        admin_markup = types.InlineKeyboardMarkup()
        admin_markup.add(
            types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"pay_yes_{pay_id}"),
            types.InlineKeyboardButton("❌ Rad etish", callback_data=f"pay_no_{pay_id}")
        )
        bot.send_message(config.ADMIN_ID, f"🔔 Yangi to'lov!\nFoydalanuvchi: {uid}\nMikdor: {amount} so'm", reply_markup=admin_markup)
    except:
        bot.send_message(message.chat.id, "Faqat raqam kiriting!")

@bot.callback_query_handler(func=lambda call: call.data.startswith("pay_"))
def admin_payment_decision(call):
    if call.from_user.id != config.ADMIN_ID: return
    _, decision, pay_id = call.data.split("_")
    conn, cursor = get_db()
    cursor.execute("SELECT user_id, amount, status FROM payments WHERE pay_id = ?", (pay_id,))
    payment = cursor.fetchone()
    
    if payment and payment[2] == 'pending':
        uid, amount = payment[0], payment[1]
        if decision == "yes":
            cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, uid))
            cursor.execute("UPDATE payments SET status = 'approved' WHERE pay_id = ?", (pay_id,))
            bot.send_message(uid, f"✅ To'lovingiz tasdiqlandi! Hisobingizga {amount} so'm qo'shildi.")
            bot.answer_callback_query(call.id, "To'lov tasdiqlandi")
        else:
            cursor.execute("UPDATE payments SET status = 'rejected' WHERE pay_id = ?", (pay_id,))
            bot.send_message(uid, "❌ To'lovingiz admin tomonidan rad etildi.")
            bot.answer_callback_query(call.id, "To'lov rad etildi")
        conn.commit()
    conn.close()

@bot.message_handler(func=lambda m: m.text == "🌐 HEMIS tizimi")
def hemis_system(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Tizimga kirish", url="https://hemis.uz"))
    bot.send_message(message.chat.id, "HEMIS talabalar tizimiga kirish uchun quyidagi tugmani bosing:", reply_markup=markup)

bot.polling(none_stop=True)
      
