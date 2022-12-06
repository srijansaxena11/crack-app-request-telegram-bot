from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler
from telegram import ParseMode
import requests
from bs4 import BeautifulSoup
import logging
from os.path import exists

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

telegram_bot_token = ""
owner_id = ""

queued_requests_file = "queued.txt"
cracked_requests_file = "cracked.txt"
uncracked_requests_file = "uncracked.txt"
authorized_users_file = "authorized_users.txt"

def is_owner(update):
    allowed = False
    user = update.message.from_user
    if user.id == int(owner_id):
        allowed = True
    return allowed

def is_allowed(update):
    allowed = False
    if is_owner(update):
        allowed = True
    else:
        user = update.message.from_user
        user_id = user.id
        username = user.username
        f = open(authorized_users_file, "r")
        authorized_users = f.readlines()
        f.close()
        for authorized_user in authorized_users:
            if int(user_id) == int(authorized_user):
                allowed = True
                break
    return allowed

def authorize(update, context):
    if(is_owner(update)):
        allowed = False
        user = update.message.reply_to_message.from_user
        user_id = user.id
        username = user.username
        f = open(authorized_users_file, "r")
        authorized_users = f.readlines()
        f.close()
        for authorized_user in authorized_users:
            if int(user_id) == int(authorized_user):
                allowed = True
                break
        if allowed:
            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text='User already authorized.')
        else:  
            f = open(authorized_users_file, "a")
            f.write(str(user_id)+"\n")
            f.close()
            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text='User authorized.')
        conn.close()
    else:
        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text='You are not the owner. This command can only be used by owner of the bot.')

def unauthorize(update, context):
    if(is_owner(update)):
        allowed = False
        user = update.message.reply_to_message.from_user
        user_id = user.id
        username = user.username
        f = open(authorized_users_file, "r")
        authorized_users = f.readlines()
        f.close()
        for authorized_user in authorized_users:
            if int(user_id) == int(authorized_user):
                allowed = True
                break
        if allowed:
            f = open(authorized_users_file, "w")
            for authorized_user in authorized_users:
                if int(user_id) != int(authorized_user):
                    f.write(authorized_user)
        else:
            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text='User not authorized.')
        conn.close()
    else:
        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text='You are not the owner. This command can only be used by owner of the bot.')


def listauthusers(update, context):
    # if(is_allowed(update)):
    f = open(authorized_users_file, "r")
    authorized_users = f.readlines()
    f.close()
    authorized_users_list = ''
    for authorized_user in authorized_users:
        authorized_users_list += authorized_user+"\n"
    context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text=f'List of authorized users:\n{authorized_users_list}')
    # else:
    #     context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text='Who the f**k are you? You are not authorized.')    

def info(update, context):
    if(is_allowed(update)):
        try:
            user = update.message.reply_to_message.from_user
            user_id = user.id
            is_user_bot = user.is_bot
            user_first_name = user.first_name
            user_last_name = user.last_name if user.last_name is not None else ''
            user_username  = user.username if user.username is not None else ''
            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, 
                                     text=f'<b>User ID</b>: {user_id}\n<b>Is User Bot</b>: {is_user_bot}\n<b>User First Name</b>: {user_first_name}\n<b>User Last Name</b>: {user_last_name}\n<b>User username</b>: @{user_username}', 
                                     parse_mode='HTML')
        except:
            chat_id = update.message.chat_id
            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text=f'Current Chat ID: {chat_id}')
    else:
        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text='You are not authorized to use this command.')

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

        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Checking link and retrieving app name from it...")
        try:
            reqs = requests.get(requested_link)
            soup = BeautifulSoup(reqs.text, 'html.parser')
            for title in soup.find_all('title'):
                app_name = title.get_text().strip()
        except:
            valid_link = False

        if valid_link == True:
            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Checking if "+app_name+" has already been requested before...")
            f = open(queued_requests_file, "r")
            queued_apps = f.readlines()
            f.close()
            for queued_app in queued_apps:
                queued_link = queued_app.split('@@')[1].strip()
                if requested_link == queued_link:
                    context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text=app_name+" has already been queued. Please wait for it to be worked upon.")
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
                        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text=app_name+" has already been cracked. Please find the crack at: "+crack_available_at_link)
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
                        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text=app_name+" cannot be cracked.")
                        uncracked_flag = True
                        break

            if queued_flag == False and cracked_flag == False and uncracked_flag == False:
                f = open(queued_requests_file, "a")
                f.write(app_name+"@@"+requested_link+"\n")
                f.close()
                context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text=app_name+" added to queue.")
        else:
            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Invalid link")
    else:
        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Link not found")

def cracked(update, context):
    if(is_allowed(update)):
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
                context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Removing "+cracked_app_name+" from queued list...")
                f = open(queued_requests_file, "r")
                queued_apps = f.readlines()
                f.close()

                f = open(queued_requests_file, "w")
                for queued_app in queued_apps:
                    queued_app_name = queued_app.split("@@")[0].replace(u'\xa0', u' ').strip().strip('\u200e')
                    context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text=queued_app_name+"~~"+cracked_app_name)
                    if queued_app_name == cracked_app_name:
                        queued_app_link = queued_app.split("@@")[1].strip()
                    if queued_app_name != cracked_app_name:
                        f.write(queued_app)

                context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Successfully removed "+cracked_app_name+" from queued list.")

                context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Adding "+cracked_app_name+" to cracked app list.")
                f = open(cracked_requests_file, "a")
                f.write(cracked_app_name+"@@"+queued_app_link+"@@"+crack_link+"\n")
                f.close()
                context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text=cracked_app_name+" added to cracked app list.")
            else:
                context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Crack link not found. Please pass the crack link after app name.")
        else:
            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="App name not found. Please use the app name from /get_queued command.")
    else:
        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text='You are not authorized to use this command.')

def uncracked(update, context):
    if(is_allowed(update)):
        message_args = update.message.text.split('@@')
        try:
            uncracked_app_name = message_args[1].strip()
        except IndexError:
            uncracked_app_name = None

        if uncracked_app_name != None:
            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Removing "+uncracked_app_name+" from queued list...")
            f = open(queued_requests_file, "r")
            queued_apps = f.readlines()
            f.close()

            f = open(queued_requests_file, "w")
            for queued_app in queued_apps:
                queued_app_name = queued_app.split("@@")[0].replace(u'\xa0', u' ').strip().strip('\u200e')
                if queued_app_name == uncracked_app_name:
                    queued_app_link = queued_app.split("@@")[1].strip()
                if queued_app_name != uncracked_app_name:
                    f.write(queued_app)

            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Successfully removed "+uncracked_app_name+" from queued list.")

            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Adding "+uncracked_app_name+" to uncracked app list.")
            f = open(uncracked_requests_file, "a")
            f.write(uncracked_app_name+"@@"+queued_app_link+"\n")
            f.close()
            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text=uncracked_app_name+" added to uncracked/cra app list.")
        else:
            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="App name not found. Please use the app name from /get_queued command.")
    else:
        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text='You are not authorized to use this command.')

def get_queued(update, context):
    f = open(queued_requests_file, "r")
    queued_apps = f.readlines()
    f.close()
    queued_app_msg = ''
    for queued_app in queued_apps:
        queued_app_name = queued_app.split('@@')[0].strip()
        queued_app_link = queued_app.split('@@')[1].strip()
        queued_app_msg += "`"+queued_app_name+"`: "+queued_app_link+"\n"

    context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Following apps are queued:\n"+queued_app_msg, parse_mode=ParseMode.MARKDOWN)

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

    context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Following apps are cracked:\n"+cracked_app_msg, parse_mode=ParseMode.MARKDOWN)

def get_uncracked(update, context):
    f = open(uncracked_requests_file, "r")
    uncracked_apps = f.readlines()
    f.close()
    uncracked_app_msg = ''
    for uncracked_app in uncracked_apps:
        uncracked_app_name = uncracked_app.split('@@')[0].strip()
        uncracked_app_link = uncracked_app.split('@@')[1].strip()
        uncracked_app_msg += "`"+uncracked_app_name+"`: "+uncracked_app_link+"\n"

    context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Following apps cannot be cracked:\n"+uncracked_app_msg, parse_mode=ParseMode.MARKDOWN)

def start(update, context):
    #context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")
    context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Use /help for list of commands")

def help(update, context):
    #context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")
    help_msg = '1. authorize: /authorize (reply to user message to authorize the user)\n2. unauthorize: /unauthorize (reply to user message to unauthorize the user)\n3. info: /info (reply to user message to get user info)\n4. request: /request <link of app from app store>\n5. get_queued: /get_queued\n6. get_cracked: /get_cracked\n7. get_uncracked: /get_uncracked\n8. cracked: /cracked@@<name of app as shown by /get_queued command>@@<link where crack is uploaded>\n9. uncracked: /uncracked@@<name of app as shown by /get_queued command>'
    context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text=help_msg)

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
    if exists(authorized_users_file) == False:
        f = open(authorized_users_file, "x")
        f.close()
    updater = Updater(telegram_bot_token)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start',start))
    dp.add_handler(CommandHandler('help',help))
    dp.add_handler(CommandHandler('authorize',authorize))
    dp.add_handler(CommandHandler('unauthorize',unauthorize))
    dp.add_handler(CommandHandler('listauthusers',listauthusers))
    dp.add_handler(CommandHandler('info',info))
    dp.add_handler(CommandHandler('request',request))
    dp.add_handler(CommandHandler('cracked',cracked))
    dp.add_handler(CommandHandler('uncracked',uncracked))
    dp.add_handler(CommandHandler('get_queued',get_queued))
    dp.add_handler(CommandHandler('get_cracked',get_cracked))
    dp.add_handler(CommandHandler('get_uncracked',get_uncracked))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
