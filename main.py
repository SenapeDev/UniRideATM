from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler
from dotenv import load_dotenv
import subprocess
import logging
import os

# configure the logging module
logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# load the environment variables
load_dotenv()
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID"))
TOKEN = os.getenv("TOKEN")

# check if the environment variables are set
if AUTHORIZED_USER_ID is None or TOKEN is None:
    logging.error("Please set the environment variables AUTHORIZED_USER_ID and TOKEN.")
    exit(1)

# function to handle the /start command
async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    # check if the user is authorized
    if user_id != AUTHORIZED_USER_ID:
        logging.warning(f"Unauthorized access attempt by user {user_id}.")
        await update.message.reply_text("❌ Action not allowed.")

        # send to the authorized user a message with the unauthorized user id
        await context.bot.send_message(chat_id=AUTHORIZED_USER_ID, text=f"⚠️ Tentativo di accesso non autorizzato da un utente #{user_id}.")
        return
    
    logging.info(f"User {user_id} started the bot.")
    
    # choose the destination with the buttons
    btn0 = InlineKeyboardButton('Università 🎓️', callback_data='0')
    btn1 = InlineKeyboardButton('Casa 🏠️', callback_data='1')
    inline_kb = InlineKeyboardMarkup([[btn0, btn1]])

    await update.message.reply_text('Seleziona la tua destinazione 🧭', reply_markup=inline_kb)


# function to handle the button callback
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    arg1 = query.data

    try:
        if arg1 == 'start':
            logging.info(f"User {user_id} requested a new trip.")
            
            # choose the destination with the buttons
            btn0 = InlineKeyboardButton('Università 🎓️', callback_data='0')
            btn1 = InlineKeyboardButton('Casa 🏠️', callback_data='1')
            inline_kb = InlineKeyboardMarkup([[btn0, btn1]])
            
            # edit the original message to show the destination selection
            await query.edit_message_text('Seleziona la tua destinazione 🧭', reply_markup=inline_kb)

        else:
            logging.info(f"User {user_id} selected option {arg1}.")

            # edit the message to show the loading message
            await query.edit_message_text('⌛ Sto cercando le informazioni...')

            # run the scraper script with the selected option
            output = subprocess.run(["python3", "./scraper.py", arg1], capture_output=True)

            # edit the message with the output of the scraper script
            await query.edit_message_text(output.stdout.decode())
            
            # ask the user if they want to make another search
            await query.message.reply_text('Vuoi fare un\'altra ricerca?', 
                                           reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Cerca una nuova corsa 🔍️', callback_data='start')]]))
    except Exception as e:
        logging.error(f"An error occurred for user {user_id}: {str(e)}")
        await query.message.reply_text('🚫 Si è verificato un errore, riprova più tardi.')


def main() -> None:
    # build the application with the token
    application = Application.builder().token(TOKEN).build()

    # add the handler for the /start command
    application.add_handler(CommandHandler('start', start))
    
    # add the handler for the button callback
    application.add_handler(CallbackQueryHandler(button))

    # run polling to start the bot
    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()