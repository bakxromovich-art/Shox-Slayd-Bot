import sqlite3

# Bot Token va Admin ID (O'zingizning Telegram ID raqamingizni yozing)
TOKEN = "8778903511:AAH8A99_g0qsPvIHqxjrFyyoRvaPShMlxSY"
ADMIN_ID = 8212010555  # O'zingizning raqamli ID'ingizni yozing

# Narxlar (so'mda)
PRICES = {
    "slayd": 5000,
    "kurs_ishi": 15000,
    "referat": 7000,
    "mustaqil_ish": 6000
}

# Ma'lumotlar bazasini yaratish
def init_db():
    conn = sqlite3.connect("bot_database.db", check_same_thread=False)
    cursor = conn.cursor()
    
    # Foydalanuvchilar jadvali
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 0,
            status TEXT DEFAULT 'user'
        )
    ''')
    
    # To'lovlar jadvali
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            pay_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            status TEXT DEFAULT 'pending'
        )
    ''')
    conn.commit()
    conn.close()

init_db()
