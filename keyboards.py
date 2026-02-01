from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(
    KeyboardButton("👤 Профиль"),
    KeyboardButton("🪪 Паспорт")
)
main_kb.add(
    KeyboardButton("🏢 Фракции"),
    KeyboardButton("💰 Получить ЗП")
)

admin_kb = ReplyKeyboardMarkup(resize_keyboard=True)
admin_kb.add(
    KeyboardButton("🛠 Админ-панель")
)
