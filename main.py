import logging
import threading
import time
from telegram import Update, error as telegram_error
from telegram.ext import Updater, CommandHandler, CallbackContext

# Set up basic logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Global flag to control spamming
is_spamming = False

# Define the spam function
def spam(update: Update, context: CallbackContext) -> None:
    global is_spamming
    chat_id = update.message.chat_id
    auth_users = [admin.user.id for admin in context.bot.get_chat_administrators(chat_id)]
    if update.message.from_user.id in auth_users:
        if is_spamming:  # Check if spamming is already in progress
            update.message.reply_text('Already spamming. Please wait or use /stop to halt.')
            return
        if context.args:  # Check if there is at least one word after the /spam command
            custom_message = ' '.join(context.args)
            is_spamming = True
            threading.Thread(target=send_spam_messages, args=(context, chat_id, custom_message)).start()
        else:
            # Prompt the user to include a message
            update.message.reply_text("Please include a message to spam. For example: /spam Hello there!")

# Define the stop function
def stop(update: Update, context: CallbackContext) -> None:
    global is_spamming
    is_spamming = False  # Disable spamming
    update.message.reply_text('Spamming stopped. The bot is now silent.')

# Function to send spam messages
def send_spam_messages(context: CallbackContext, chat_id: int, message: str) -> None:
    global is_spamming
    while is_spamming:
        try:
            context.bot.send_message(chat_id, text=message)
            time.sleep(10)  # Sleep duration to respect the rate limit
        except telegram_error.RetryAfter as e:
            logger.warning(f"Rate limit exceeded. Sleeping for {e.retry_after} seconds.")
            time.sleep(e.retry_after)
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            break

# Define the main function
def main() -> None:
    updater = Updater("6770944351:AAEgtPSRiyZQWfMpnINDp1SPLH6yC7ln5Rk", use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("spam", spam, pass_args=True))
    dispatcher.add_handler(CommandHandler("stop", stop))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
