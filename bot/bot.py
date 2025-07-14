import os
import requests
from dotenv import load_dotenv
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

load_dotenv()
# load_dotenv(dotenv_path="/var/www/shakarim-admission-bot/.env")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL")

# Обработчик команды /start
def start(update: Update, context: CallbackContext) -> None:
    """Отправляет приветственное сообщение при команде /start."""
    user_first_name = update.effective_user.first_name
    welcome_message = (
        f"👋 Привет, {user_first_name}!\n\n"
        f'Я бот-помощник для поступающих в НАО "Шәкәрім университет". '
        f"Задайте мне вопрос о поступлении, и я постараюсь на него ответить.\n\n"
        f"Например:\n"
        f"- Какие документы нужны для поступления?\n"
        f"- Какие есть гранты?\n"
        f"- Когда начинается прием документов?"
    )
    update.message.reply_text(welcome_message)

# Обработчик команды /help
def help_command(update: Update, context: CallbackContext) -> None:
    """Отправляет информацию о возможностях бота при команде /help."""
    help_message = (
        "🔍 Вот что я умею:\n\n"
        '- Отвечать на вопросы о поступлении в НАО "Шәкәрім университет"\n'
        "- Предоставлять информацию о грантах, документах и сроках\n"
        "- Помогать с процессом поступления\n\n"
        "Просто напишите свой вопрос, и я постараюсь помочь!"
    )
    update.message.reply_text(help_message)

# Обработчик текстовых сообщений
def handle_message(update: Update, context: CallbackContext) -> None:
    """Обрабатывает текстовые сообщения и отправляет ответ от Gemini AI с использованием базы знаний."""
    user_question = update.message.text
    
    # "печатает..."
    context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action='typing'
    )
    
    try:
        session_id = str(update.effective_chat.id)  # используем Telegram chat ID
        response = requests.get(
            f"{API_BASE_URL}/smart_ask_gemini/",
            params={"question": user_question, "session_id": session_id}
        )
        
        if response.status_code == 200:
            answer = response.json().get("answer", "Извините, я не смог найти ответ на ваш вопрос.")
            update.message.reply_text(answer)
        else:
            update.message.reply_text(
                "Извините, произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже."
            )
    except Exception as e:
        update.message.reply_text(
            "Извините, произошла ошибка. Пожалуйста, попробуйте позже."
        )

def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()