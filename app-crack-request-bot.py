from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler #, Filters
# from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
from telegram import ParseMode
import requests
from bs4 import BeautifulSoup
# import re
import logging
# from uuid import uuid4
# from telegram.utils.helpers import escape_markdown
# import random
from os.path import exists

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

telegram_bot_token = ''

queued_requests_file = "queued.txt"
cracked_requests_file = "cracked.txt"
uncracked_requests_file = "uncracked.txt"

def request(update, context):
    message_args = update.message.text.split(' ')
    try:
        requested_link = message_args[1]
    except IndexError:
        requested_link = None

    if requested_link != None:
        queued_flag = False
        cracked_flag = False
        uncracked_flag = False
        valid_link = True

        context.bot.send_message(chat_id=update.message.chat_id, text="Checking link and retrieving app name from it...")
        try:
            reqs = requests.get(requested_link)
            soup = BeautifulSoup(reqs.text, 'html.parser')
            for title in soup.find_all('title'):
                app_name = title.get_text().strip()
        except:
            valid_link = False

        if valid_link == True:
            context.bot.send_message(chat_id=update.message.chat_id, text="Checking if "+app_name+" has already been requested before...")
            f = open(queued_requests_file, "r")
            queued_apps = f.readlines()
            f.close()
            for queued_app in queued_apps:
                queued_link = queued_app.split('@@')[1].strip()
                if requested_link == queued_link:
                    context.bot.send_message(chat_id=update.message.chat_id, text=app_name+" has already been queued. Please wait for it to be worked upon.")
                    queued_flag = True
                    break

            if queued_flag == False:
                f = open(cracked_requests_file, "r")
                cracked_apps = f.readlines()
                f.close()
                for cracked_app in cracked_apps:
                    cracked_link = cracked_app.split('@@')[1].strip()
                    if requested_link == cracked_link:
                        crack_available_at_link = cracked_app.split('@@')[2].strip()
                        context.bot.send_message(chat_id=update.message.chat_id, text=app_name+" has already been cracked. Please find the crack at: "+crack_available_at_link)
                        cracked_flag = True
                        break

            if queued_flag == False and cracked_flag == False:
                f = open(uncracked_requests_file, "r")
                uncracked_apps = f.readlines()
                f.close()
                for uncracked_app in uncracked_apps:
                    uncracked_link = uncracked_app.split('@@')[1].strip()
                    if requested_link == uncracked_link:
                        # cannot_be_cracked_reason = uncracked_app.split('@@')[2]
                        context.bot.send_message(chat_id=update.message.chat_id, text=app_name+" cannot be cracked.")
                        uncracked_flag = True
                        break

            if queued_flag == False and cracked_flag == False and uncracked_flag == False:
                f = open(queued_requests_file, "a")
                f.write(app_name+"@@"+requested_link+"\n")
                f.close()
                context.bot.send_message(chat_id=update.message.chat_id, text=app_name+" added to queue.")
        else:
            context.bot.send_message(chat_id=update.message.chat_id, text="Invalid link")
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text="Link not found")

def cracked(update, context):
    message_args = update.message.text.split('@@')
    try:
        cracked_app_name = message_args[1].strip()
    except IndexError:
        cracked_app_name = None

    try:
        crack_link = message_args[2].strip()
    except IndexError:
        crack_link = None

    if cracked_app_name != None:
        if crack_link != None:
            context.bot.send_message(chat_id=update.message.chat_id, text="Removing "+cracked_app_name+" from queued list...")
            f = open(queued_requests_file, "r")
            queued_apps = f.readlines()
            f.close()

            f = open(queued_requests_file, "w")
            for queued_app in queued_apps:
                queued_app_name = queued_app.split("@@")[0].replace(u'\xa0', u' ').strip().strip('\u200e')
                context.bot.send_message(chat_id=update.message.chat_id, text=queued_app_name+"~~"+cracked_app_name)
                if queued_app_name == cracked_app_name:
                    # context.bot.send_message(chat_id=update.message.chat_id, text="line 111")
                    queued_app_link = queued_app.split("@@")[1].strip()
                if queued_app_name != cracked_app_name:
                    # context.bot.send_message(chat_id=update.message.chat_id, text="line 114")
                    f.write(queued_app)

            context.bot.send_message(chat_id=update.message.chat_id, text="Successfully removed "+cracked_app_name+" from queued list.")

            context.bot.send_message(chat_id=update.message.chat_id, text="Adding "+cracked_app_name+" to cracked app list.")
            f = open(cracked_requests_file, "a")
            f.write(cracked_app_name+"@@"+queued_app_link+"@@"+crack_link+"\n")
            f.close()
            context.bot.send_message(chat_id=update.message.chat_id, text=cracked_app_name+" added to cracked app list.")
        else:
            context.bot.send_message(chat_id=update.message.chat_id, text="Crack link not found. Please pass the crack link after app name.")
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text="App name not found. Please use the app name from /get_queued command.")

def uncracked(update, context):
    message_args = update.message.text.split('@@')
    try:
        uncracked_app_name = message_args[1].strip()
    except IndexError:
        uncracked_app_name = None

    if uncracked_app_name != None:
        context.bot.send_message(chat_id=update.message.chat_id, text="Removing "+uncracked_app_name+" from queued list...")
        f = open(queued_requests_file, "r")
        queued_apps = f.readlines()
        f.close()

        f = open(queued_requests_file, "w")
        for queued_app in queued_apps:
            queued_app_name = queued_app.split("@@")[0].replace(u'\xa0', u' ').strip().strip('\u200e')
            # context.bot.send_message(chat_id=update.message.chat_id, text=queued_app_name+"~~"+cracked_app_name)
            if queued_app_name == uncracked_app_name:
                # context.bot.send_message(chat_id=update.message.chat_id, text="line 111")
                queued_app_link = queued_app.split("@@")[1].strip()
            if queued_app_name != uncracked_app_name:
                # context.bot.send_message(chat_id=update.message.chat_id, text="line 114")
                f.write(queued_app)

        context.bot.send_message(chat_id=update.message.chat_id, text="Successfully removed "+uncracked_app_name+" from queued list.")

        context.bot.send_message(chat_id=update.message.chat_id, text="Adding "+uncracked_app_name+" to uncracked app list.")
        f = open(uncracked_requests_file, "a")
        f.write(uncracked_app_name+"@@"+queued_app_link+"\n")
        f.close()
        context.bot.send_message(chat_id=update.message.chat_id, text=uncracked_app_name+" added to uncracked/cra app list.")
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text="App name not found. Please use the app name from /get_queued command.")

def get_queued(update, context):
    f = open(queued_requests_file, "r")
    queued_apps = f.readlines()
    f.close()
    queued_app_msg = ''
    for queued_app in queued_apps:
        queued_app_name = queued_app.split('@@')[0].strip()
        queued_app_link = queued_app.split('@@')[1].strip()
        queued_app_msg += "`"+queued_app_name+"`: "+queued_app_link+"\n"

    context.bot.send_message(chat_id=update.message.chat_id, text="Following apps are queued:\n"+queued_app_msg, parse_mode=ParseMode.MARKDOWN)

def get_cracked(update, context):
    f = open(cracked_requests_file, "r")
    cracked_apps = f.readlines()
    f.close()
    cracked_app_msg = ''
    for cracked_app in cracked_apps:
        cracked_app_name = cracked_app.split('@@')[0].strip()
        cracked_app_link = cracked_app.split('@@')[1].strip()
        crack_available_at_link = cracked_app.split('@@')[2].strip()
        cracked_app_msg += "`"+cracked_app_name+"`: "+crack_available_at_link+"\n"

    context.bot.send_message(chat_id=update.message.chat_id, text="Following apps are cracked:\n"+cracked_app_msg, parse_mode=ParseMode.MARKDOWN)

def get_uncracked(update, context):
    f = open(uncracked_requests_file, "r")
    uncracked_apps = f.readlines()
    f.close()
    uncracked_app_msg = ''
    for uncracked_app in uncracked_apps:
        uncracked_app_name = uncracked_app.split('@@')[0].strip()
        uncracked_app_link = uncracked_app.split('@@')[1].strip()
        uncracked_app_msg += "`"+uncracked_app_name+"`: "+uncracked_app_link+"\n"

    context.bot.send_message(chat_id=update.message.chat_id, text="Following apps cannot be cracked:\n"+uncracked_app_msg, parse_mode=ParseMode.MARKDOWN)

def start(update, context):
    #context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")
    context.bot.send_message(chat_id=update.message.chat_id, text="start placeholder")

# def inlinequery(bot, update):
#     print("Inside inlinequery()")
#     """Handle the inline query."""
#     query = update.inline_query.query
#     results = [
#         InlineQueryResultArticle(
#             id=uuid4(),
#             title="Query",
#             input_message_content=InputTextMessageContent(
#                 query))]
#     update.inline_query.answer(results)

def main():
    if exists(queued_requests_file) == False:
        f = open(queued_requests_file, "x")
        f.close()
    if exists(cracked_requests_file) == False:
        f = open(cracked_requests_file, "x")
        f.close()
    if exists(uncracked_requests_file) == False:
        f = open(uncracked_requests_file, "x")
        f.close()
    updater = Updater(telegram_bot_token)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start',start))
    dp.add_handler(CommandHandler('request',request))
    dp.add_handler(CommandHandler('cracked',cracked))
    dp.add_handler(CommandHandler('uncracked',uncracked))
    dp.add_handler(CommandHandler('get_queued',get_queued))
    dp.add_handler(CommandHandler('get_cracked',get_cracked))
    dp.add_handler(CommandHandler('get_uncracked',get_uncracked))

    # dp.add_handler(InlineQueryHandler(inlinequery))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
