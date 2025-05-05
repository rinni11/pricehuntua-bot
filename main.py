import os
import aiohttp
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# /start команда з кнопкою
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location_button = KeyboardButton("Надіслати локацію 📍", request_location=True)
    reply_markup = ReplyKeyboardMarkup([[location_button]], resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text(
        "Привіт! Я бот BenzOK. Натисни кнопку нижче, щоб надіслати свою локацію й знайти дешеві АЗС поряд ⛽️",
        reply_markup=reply_markup
    )

# Обробка локації та пошук АЗС
async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location = update.message.location
    lat = location.latitude
    lon = location.longitude

    await update.message.reply_text("Шукаю найближчі АЗС поблизу… 🔍")

    url = (
        f"https://nominatim.openstreetmap.org/search?"
        f"q=gas+station&format=json&limit=3&"
        f"lat={lat}&lon={lon}&addressdetails=1"
    )

    headers = {
        "User-Agent": "BenzOK-Bot/1.0 (contact@example.com)"  # заміни email на свій
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            data = await resp.json()

    if not data:
        await update.message.reply_text("😕 Не знайдено АЗС поблизу.")
        return

    message = "📍 Найближчі АЗС:\n\n"
    for place in data:
        name = place.get("display_name", "Без назви")
        lat = place["lat"]
        lon = place["lon"]
        maps_url = f"https://www.google.com/maps?q={lat},{lon}"
        message += f"▪️ [{name}]({maps_url})\n\n"

    await update.message.reply_text(message, parse_mode="Markdown")

# Запуск бота
if __name__ == '__main__':
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise ValueError("❌ TELEGRAM_TOKEN не заданий!")

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.run_polling()
