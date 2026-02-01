import sqlite3
from aiogram import Bot, Dispatcher, executor, types
from config import TOKEN, ADMIN_IDS
from keyboards import main_kb

bot = Bot(TOKEN)
dp = Dispatcher(bot)

db = sqlite3.connect("database.db")
sql = db.cursor()

# ================= БАЗА =================
sql.execute("""
CREATE TABLE IF NOT EXISTS users(
    tg_id INTEGER PRIMARY KEY,
    nickname TEXT,
    player_id TEXT,
    rp_name TEXT,
    faction TEXT,
    rank TEXT,
    balance INTEGER,
    warns INTEGER
)
""")

sql.execute("""
CREATE TABLE IF NOT EXISTS salary_requests(
    tg_id INTEGER,
    photo_id TEXT
)
""")
db.commit()

# ================= START =================
@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    sql.execute("SELECT tg_id FROM users WHERE tg_id=?", (msg.from_user.id,))
    if not sql.fetchone():
        await msg.answer(
            "🏔 Добро пожаловать в Adygea RP\n\n"
            "Отправь данные:\n"
            "Ник | PlayerID | Имя Фамилия"
        )
    else:
        await msg.answer("Главное меню:", reply_markup=main_kb)

# ================= РЕГИСТРАЦИЯ =================
@dp.message_handler(lambda m: "|" in m.text)
async def register(msg: types.Message):
    data = [x.strip() for x in msg.text.split("|")]
    if len(data) != 3:
        return

    sql.execute("INSERT OR IGNORE INTO users VALUES(?,?,?,?,?,?,?,?)", (
        msg.from_user.id,
        data[0],
        data[1],
        data[2],
        "Гражданин",
        "—",
        5000,
        0
    ))
    db.commit()

    await msg.answer("✅ Регистрация завершена", reply_markup=main_kb)

# ================= ПРОФИЛЬ =================
@dp.message_handler(text="👤 Профиль")
async def profile(msg: types.Message):
    sql.execute("SELECT * FROM users WHERE tg_id=?", (msg.from_user.id,))
    u = sql.fetchone()
    await msg.answer(
        f"👤 {u[3]}\n"
        f"🆔 {u[2]}\n"
        f"🏢 {u[4]}\n"
        f"🎖 {u[5]}\n"
        f"💰 {u[6]} ARP$\n"
        f"⚠️ Варны: {u[7]}"
    )

# ================= ПАСПОРТ =================
@dp.message_handler(text="🪪 Паспорт")
async def passport(msg: types.Message):
    sql.execute("SELECT rp_name, player_id, faction FROM users WHERE tg_id=?", (msg.from_user.id,))
    u = sql.fetchone()

    text = (
        "🪪 PASSPORT\n\n"
        f"ФИО: {u[0]}\n"
        f"ID: {u[1]}\n"
        f"Фракция: {u[2]}\n"
        "Проект: Adygea RP"
    )

    await msg.answer(text)

# ================= ФРАКЦИИ =================
@dp.message_handler(text="🏢 Фракции")
async def factions(msg: types.Message):
    await msg.answer(
        "🏢 Доступные фракции:\n"
        "1️⃣ Полиция\n"
        "2️⃣ Больница\n"
        "3️⃣ Такси\n\n"
        "Напиши: Вступить | Название"
    )

@dp.message_handler(lambda m: m.text.startswith("Вступить"))
async def join_faction(msg: types.Message):
    faction = msg.text.split("|")[1].strip()

    for admin in ADMIN_IDS:
        await bot.send_message(
            admin,
            f"📥 Заявка во фракцию\n"
            f"👤 {msg.from_user.id}\n"
            f"🏢 {faction}"
        )

    await msg.answer("📨 Заявка отправлена администрации")

# ================= ЗАРПЛАТА =================
@dp.message_handler(text="💰 Получить ЗП")
async def salary(msg: types.Message):
    await msg.answer("📸 Отправь скриншот для получения зарплаты")

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def salary_photo(msg: types.Message):
    file_id = msg.photo[-1].file_id
    sql.execute("INSERT INTO salary_requests VALUES(?,?)", (msg.from_user.id, file_id))
    db.commit()

    for admin in ADMIN_IDS:
        await bot.send_photo(
            admin,
            file_id,
            caption=f"💰 Запрос ЗП от {msg.from_user.id}"
        )

    await msg.answer("⏳ Скрин отправлен администрации")

# ================= АДМИН КОМАНДЫ =================
@dp.message_handler(commands=["give"])
async def give(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS:
        return

    _, uid, amount = msg.text.split()
    sql.execute("UPDATE users SET balance = balance + ? WHERE tg_id=?", (amount, uid))
    db.commit()
    await msg.answer("✅ Деньги выданы")

# ================= RUN =================
if __name__ == "__main__":
    executor.start_polling(dp)
