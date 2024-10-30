import logging
import nest_asyncio
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
from datetime import time, datetime

# Задаем токен
TOKEN = "7785736910:AAGL4dbNuxtY8JJtcDDb5PmH2isgZTJXw9I"

# Включаем логирование
logging.basicConfig(
    filename='bot_logs.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Список пользователей для уведомлений
subscribed_users = set()

# Команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [KeyboardButton("/schedule"), KeyboardButton("/idea")],
        [KeyboardButton("/events"), KeyboardButton("/help")],
        [KeyboardButton("/notify_on"), KeyboardButton("/notify_off")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Привет! Я бот для сервера Minecraft. Выберите команду:", reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Доступные команды:\n"
        "/schedule - расписание событий\n"
        "/idea - предложить идею\n"
        "/events - информация об ивентах\n"
        "/notify_on - включить уведомления о запуске сервера\n"
        "/notify_off - отключить уведомления о запуске сервера\n"
    )

async def schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    schedule_text = (
        "Расписание гейтов:\n"
        "13:30 — первый гейт\n"
        "15:30 — промежуточный гейт\n"
        "18:30 — второй гейт\n"
    )
    await update.message.reply_text(schedule_text)

async def idea_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Напишите вашу идею, и я передам её разработчикам.")

async def events_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    events_text = (
        "План подготовки к Хэллоуину:\n"
        "🕷️ На время недели Хэллоуина будет включен Спаун мобов (22.10.24)\n"
        "🛒 Каждый день на базах игроков будут появляться сундуки с ресурсами для подготовки к Хэллоуину (21.10.24)\n"
        "❇️ Спавн мобов усилится (30.10.24)\n"
        "😈 Конкурс на лучшее украшение базы к Хэллоуину (31.10.24)\n"
    )
    await update.message.reply_text(events_text)

async def notify_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    subscribed_users.add(user_id)
    await update.message.reply_text("Вы подписаны на уведомления о запуске сервера.")

async def notify_off(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    subscribed_users.discard(user_id)
    await update.message.reply_text("Вы отписаны от уведомлений о запуске сервера.")

async def send_notifications(app: Application) -> None:
    notification_times = [time(13, 30), time(15, 30), time(18, 30)]
    while True:
        now = datetime.now().time()
        if any(now.hour == t.hour and now.minute == t.minute for t in notification_times):
            for user_id in subscribed_users:
                await app.bot.send_message(chat_id=user_id, text="Сервер открылся!")
            await asyncio.sleep(60)  # Ждем минуту, чтобы избежать повторной отправки
        await asyncio.sleep(30)  # Проверка каждые 30 секунд

async def main() -> None:
    app = Application.builder().token(TOKEN).build()

    # Обработка команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("schedule", schedule_command))
    app.add_handler(CommandHandler("idea", idea_command))
    app.add_handler(CommandHandler("events", events_command))
    app.add_handler(CommandHandler("notify_on", notify_on))
    app.add_handler(CommandHandler("notify_off", notify_off))

    # Запускаем функцию уведомлений
    app.create_task(send_notifications(app))

    # Запуск бота
    await app.initialize()
    await app.run_polling()

if __name__ == '__main__':
    nest_asyncio.apply()
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if 'already running' in str(e):
            asyncio.run(main())
