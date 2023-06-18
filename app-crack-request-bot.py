import requests
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ParseMode
from bs4 import BeautifulSoup


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
telegram_bot_token = ""
owner_id = ""
queued_requests_file = "queued.txt"
cracked_requests_file = "cracked.txt"
uncracked_requests_file = "uncracked.txt"
authorized_users_file = "authorized_users.txt"
authorized_topics_file = "authorized_topics.txt"


def get_authorized_file(id, file):
    with open(file, "r") as f:
        for auth in f.readlines():
            if int(auth) == int(id):
                return True
    return False


def get_topic_id(update, context):
    if is_allowed(update):
        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text=f"Topic ID: `{update.message.reply_to_message.message_id}`", parse_mode=ParseMode.MARKDOWN)
    else:
        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="You are not authorized to use this command.")


def is_owner(update):
    if update.message.from_user.id == int(owner_id):
        return True
    return False


def is_allowed(update):
    if is_owner(update):
        return True
    else:
        return get_authorized_file(update.message.from_user.id, authorized_users_file)
        

def is_topic_allowed(update):
    if update.message.chat.type == "supergroup":
        if update.message.reply_to_message:
            topic_id = update.message.reply_to_message.message_id
        else:
            topic_id = update.message.chat.id
        return get_authorized_file(topic_id, authorized_topics_file)
    else:
        return True


def authorize(update, context):
    if not is_owner(update):
        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="You are not the owner. This command can only be used by owner of the bot.")
        return
    user_id = update.message.reply_to_message.from_user
    if get_authorized_file(user_id, authorized_users_file):
        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text='User already authorized.')
    else:  
        with open(authorized_users_file, "a") as f:
            f.write(f"{user_id}\n")
        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text='User authorized.')


def authorize_topic(update, context):
    if not is_owner(update):
        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text='You are not the owner. This command can only be used by owner of the bot.')
        return

    if update.message.reply_to_message:
        topic_id = update.message.reply_to_message.message_id
    else:
        topic_id = update.message.chat_id

    if get_authorized_file(topic_id, authorized_topics_file):
        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text='Topic already authorized.')
    else:  
        with open(authorized_topics_file, "a") as f:
            f.write(f"{topic_id}\n")
        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text='Topic authorized.')


def unauthorize(update, context):
    if not is_owner(update):
        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text='You are not the owner. This command can only be used by owner of the bot.')
        return
    user_id = update.message.reply_to_message.from_user.id
    if not get_authorized_file(user_id, authorized_users_file):
        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text='User not authorized.')
        return
    with open(authorized_users_file, "r") as auf:
        authorized_users = auf.readlines()
    with open(authorized_users_file, "w") as f:
        f.writelines(auth for auth in authorized_users if int(auth.strip()) != int(user_id))
    context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text='User unauthorized.')


def unauthorize_topic(update, context):
    if not is_owner(update):
        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text='You are not the owner. This command can only be used by owner of the bot.')
        return

    if update.message.reply_to_message:
        topic_id = update.message.reply_to_message.message_id
    else:
        topic_id = update.message.chat.id

    if not get_authorized_file(topic_id, authorized_topics_file):
        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text='Topic not authorized.')
        return

    with open(authorized_topics_file, "r") as atfr:
        authorized_topics = atfr.readlines()
    with open(authorized_topics_file, "w") as atfw:
        atfw.writelines(auth for auth in authorized_topics if int(auth.strip()) != int(topic_id))
    context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text='Topic unauthorized.')
        

def listauthusers(update, context):
    if not is_allowed(update):
        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text='You are not authorized to use this command.')
        return

    with open(authorized_users_file, "r") as f:
        authorized_users_list = ""
        for authorized_user in f.readlines():
            authorized_users_list += f"{authorized_user}\n"

    context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text=f'List of authorized users:\n{authorized_users_list}')
        

def listauthtopics(update, context):
    if not is_allowed(update):
        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text='You are not authorized to use this command.')
        return
    with open(authorized_topics_file, "r") as f:
        authorized_topics_list = ""
        for authorized_topic in f.readlines():
            authorized_topics_list += f"{authorized_topic}\n"
    context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text=f'List of authorized topics:\n{authorized_topics_list}')
        

def info(update, context):
    if not is_allowed(update):
        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text='You are not authorized to use this command.')
        return
    try:
        user = update.message.reply_to_message.from_user
        user_id = user.id
        is_user_bot = user.is_bot
        user_first_name = user.first_name
        user_last_name = user.last_name if user.last_name else 'No last name detected'
        user_username  = user.username if user.username else 'No username deteted'
        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, 
                                text=f'<b>User ID</b>: {user_id}\n<b>Is User Bot</b>: {is_user_bot}\n<b>User First Name</b>: {user_first_name}\n<b>User Last Name</b>: {user_last_name}\n<b>User username</b>: @{user_username}', 
                                parse_mode='HTML')
    except:
        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text=f'Current Chat ID: {update.message.chat_id}')

def request(update, context):
    if(is_topic_allowed(update)):
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

            message = context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Checking link and retrieving app name from it...")
            try:
                reqs = requests.get(requested_link)
                soup = BeautifulSoup(reqs.text, 'html.parser')
                for title in soup.find_all('title'):
                    app_name = title.get_text().replace(u'\xa0', u' ').strip().strip('\u200e')
            except:
                valid_link = False

            if valid_link == True:
                context.bot.edit_message_text(chat_id=update.message.chat_id, message_id=message.message_id, text="Checking if " + app_name + " has already been requested before...")
                f = open(queued_requests_file, "r")
                queued_apps = f.readlines()
                f.close()
                for queued_app in queued_apps:
                    queued_link = queued_app.split('@@')[1].strip()
                    if requested_link == queued_link:
                        context.bot.edit_message_text(chat_id=update.message.chat_id, message_id=message.message_id, text=app_name + " has already been queued. Please wait for it to be worked upon.")
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
                            context.bot.edit_message_text(chat_id=update.message.chat_id, message_id=message.message_id, text=app_name + " has already been cracked. Please find the crack at: " + crack_available_at_link)
                            cracked_flag = True
                            break

                if queued_flag == False and cracked_flag == False:
                    f = open(uncracked_requests_file, "r")
                    uncracked_apps = f.readlines()
                    f.close()
                    for uncracked_app in uncracked_apps:
                        uncracked_link = uncracked_app.split('@@')[1].strip()
                        if requested_link == uncracked_link:
                            context.bot.edit_message_text(chat_id=update.message.chat_id, message_id=message.message_id, text=app_name + " cannot be cracked.")
                            uncracked_flag = True
                            break

                if queued_flag == False and cracked_flag == False and uncracked_flag == False:
                    f = open(queued_requests_file, "a")
                    f.write(app_name + "@@" + requested_link + "\n")
                    f.close()
            
                    context.bot.edit_message_text(chat_id=update.message.chat_id, message_id=message.message_id, text=app_name + " added to queue.")
            else:
                sent_message = context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Invalid link")
                context.bot.deleteMessage(message_id=update.message.message_id, chat_id=update.message.chat_id)
                context.bot.deleteMessage(message_id=sent_message.message_id, chat_id=update.message.chat_id)
        else:
            sent_message = context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Link not found")
            context.bot.deleteMessage(message_id=update.message.message_id, chat_id=update.message.chat_id)
            context.bot.deleteMessage(message_id=sent_message.message_id, chat_id=update.message.chat_id)

def cracked(update, context):
    if(is_allowed(update)):
        message_args = update.message.text.split(' ')
        try:
            cracked_app_link = message_args[1].strip()
        except IndexError:
            cracked_app_link = None

        try:
            crack_link = message_args[2].strip()
        except IndexError:
            crack_link = None

        if cracked_app_link != None:
            if crack_link != None:
                valid_link = True
                context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Checking link and retrieving app name from it...")
                try:
                    reqs = requests.get(cracked_app_link)
                    soup = BeautifulSoup(reqs.text, 'html.parser')
                    for title in soup.find_all('title'):
                        cracked_app_name = title.get_text().replace(u'\xa0', u' ').strip().strip('\u200e')
                except:
                    valid_link = False

                if valid_link == True: 
                    context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Removing "+cracked_app_name+" from queued list...")
                    f = open(queued_requests_file, "r")
                    queued_apps = f.readlines()
                    f.close()

                    f = open(queued_requests_file, "w")
                    for queued_app in queued_apps:
                        queued_app_name = queued_app.split("@@")[0].replace(u'\xa0', u' ').strip().strip('\u200e')
                        if queued_app_name == cracked_app_name:
                            queued_app_link = queued_app.split("@@")[1].strip()
                        if queued_app_name != cracked_app_name:
                            f.write(queued_app)

                    context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Successfully removed "+cracked_app_name+" from queued list.")

                    context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Adding "+cracked_app_name+" to cracked app list.")
                    f = open(cracked_requests_file, "a")
                    f.write(cracked_app_name+"@@"+cracked_app_link+"@@"+crack_link+"\n")
                    f.close()
                    context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text=cracked_app_name+" added to cracked app list.")
                else:
                    sent_message = context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Invalid link")
            else:
                context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Crack link not found. Please pass the crack link after app name.")
        else:
            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="App link not found. Please provide the link of app which is cracked.")
    else:
        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text='You are not authorized to use this command.')

def uncracked(update, context):
    if(is_allowed(update)):
        message_args = update.message.text.split(' ')
        try:
            uncracked_app_link = message_args[1].strip()
        except IndexError:
            uncracked_app_link = None

        if uncracked_app_link != None:
            valid_link = True
            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Checking link and retrieving app name from it...")
            try:
                reqs = requests.get(uncracked_app_link)
                soup = BeautifulSoup(reqs.text, 'html.parser')
                for title in soup.find_all('title'):
                    uncracked_app_name = title.get_text().replace(u'\xa0', u' ').strip().strip('\u200e')
            except:
                valid_link = False

            if valid_link == True:
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
                f.write(uncracked_app_name+"@@"+uncracked_app_link+"\n")
                f.close()
                context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text=uncracked_app_name+" added to uncracked/cra app list.")
            else:
                sent_message = context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Invalid link")
        else:
            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="App link not found. Please provide the link of app which is cracked.")
    else:
        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text='You are not authorized to use this command.')

def get_queued(update, context):
    if(is_topic_allowed(update)):
        f = open(queued_requests_file, "r")
        queued_apps = f.readlines()
        f.close()
        queued_app_msg = ''
        characters_count = 0
        msg_sent_flag = False
        for queued_app in queued_apps:
            queued_app_name = queued_app.split('@@')[0].strip()
            queued_app_link = queued_app.split('@@')[1].strip()
            queued_app_msg += "`"+queued_app_name+"`: "+queued_app_link+"\n\n"
            characters_count += len(queued_app_msg)
            if (characters_count>9000):
                context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Following apps are queued:\n"+queued_app_msg, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
                queued_app_msg = ''
                characters_count = 0
                msg_sent_flag = True
        if (msg_sent_flag == False):
            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Following apps are queued:\n"+queued_app_msg, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        
    else:
        sent_message = context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Topic not authorized")
        context.bot.deleteMessage (message_id = update.message.message_id, chat_id = update.message.chat_id)
        context.bot.deleteMessage (message_id = sent_message.message_id, chat_id = update.message.chat_id)


def get_cracked(update, context):
    if(is_topic_allowed(update)):
        f = open(cracked_requests_file, "r")
        cracked_apps = f.readlines()
        f.close()
        cracked_app_msg = ''
        characters_count = 0
        msg_sent_flag = False
        for cracked_app in cracked_apps:
            cracked_app_name = cracked_app.split('@@')[0].strip()
            cracked_app_link = cracked_app.split('@@')[1].strip()
            crack_available_at_link = cracked_app.split('@@')[2].strip()
            cracked_app_msg += cracked_app_name+": "+crack_available_at_link+"\n\n"
            characters_count += len(cracked_app_msg)
            if (characters_count>9000):
                context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Following apps are cracked:\n"+cracked_app_msg, disable_web_page_preview=True)
                cracked_app_msg = ''
                characters_count = 0
                msg_sent_flag = True
        if (msg_sent_flag == False):
            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Following apps are cracked:\n"+cracked_app_msg, disable_web_page_preview=True)
    else:
        sent_message = context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Topic not authorized")

def get_uncracked(update, context):
    if(is_topic_allowed(update)):
        f = open(uncracked_requests_file, "r")
        uncracked_apps = f.readlines()
        f.close()
        uncracked_app_msg = ''
        characters_count = 0
        msg_sent_flag = False
        for uncracked_app in uncracked_apps:
            uncracked_app_name = uncracked_app.split('@@')[0].strip()
            uncracked_app_link = uncracked_app.split('@@')[1].strip()
            uncracked_app_msg += "`"+uncracked_app_name+"`: "+uncracked_app_link+"\n\n"
            characters_count += len(uncracked_app_msg)
            if (characters_count>9000):
                context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Following apps cannot be cracked:\n"+uncracked_app_msg, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
                uncracked_app_msg = ''
                characters_count = 0
                msg_sent_flag = True
        if (msg_sent_flag == False):
            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Following apps are cracked:\n"+cracked_app_msg, disable_web_page_preview=True)
    else:
        sent_message = context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Topic not authorized")

def remove(update, context):
    if not is_allowed(update):
        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text='You are not authorized to use this command.')
        return
    message_args = update.message.text.split(' ')
    try:
        app_link = message_args[1].strip()
    except IndexError:
        app_link = None

    if app_link != None:
        queued_flag = False
        cracked_flag = False
        uncracked_flag = False
        valid_link = True

        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Checking link and retrieving app name from it...")
        try:
            reqs = requests.get(app_link)
            soup = BeautifulSoup(reqs.text, 'html.parser')
            for title in soup.find_all('title'):
                app_name = title.get_text().replace(u'\xa0', u' ').strip().strip('\u200e')
        except:
            valid_link = False

            if valid_link == True:
                context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Checking "+app_name+" in queued list...")
                f = open(queued_requests_file, "r")
                queued_apps = f.readlines()
                f.close()
                for queued_app in queued_apps:
                    queued_app_name = queued_app.split("@@")[0].replace(u'\xa0', u' ').strip().strip('\u200e')
                    queued_app_link = queued_app.split('@@')[1].strip()
                    if queued_app_name == app_name:
                        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text=app_name+" found in queued list. Removing...")
                        f = open(queued_requests_file, "w")
                        for queued_app in queued_apps:
                            queued_app_name = queued_app.split("@@")[0].replace(u'\xa0', u' ').strip().strip('\u200e')
                            queued_app_link = queued_app.split('@@')[1].strip()
                            # print(queued_app_name+"\n"+queued_app_link+"\n"+app_link)
                            if queued_app_name != app_name:
                                f.write(queued_app_name+"@@"+queued_app_link+"\n")
                        queued_flag = True
                        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text=app_name+" removed from queued list.")
                        break

                if queued_flag == False:
                    context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text=app_name+" not found in queued list. Checking in cracked list...")
                    f = open(cracked_requests_file, "r")
                    cracked_apps = f.readlines()
                    f.close()
                    for cracked_app in cracked_apps:
                        cracked_app_name = cracked_app.split("@@")[0].replace(u'\xa0', u' ').strip().strip('\u200e')
                        cracked_app_link = cracked_app.split('@@')[1].strip()
                        if cracked_app_name == app_name:
                            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text=app_name+" found in cracked list. Removing...")
                            f = open(cracked_requests_file, "w")
                            for cracked_app in cracked_apps:
                                cracked_app_name = cracked_app.split("@@")[0].replace(u'\xa0', u' ').strip().strip('\u200e')
                                cracked_app_link = cracked_app.split('@@')[1].strip()
                                crack_link = cracked_app.split('@@')[2].strip()
                                if cracked_app_name != app_name:
                                    f.write(cracked_app_name+"@@"+cracked_app_link+"@@"+crack_link+"\n")
                            cracked_flag = True
                            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text=app_name+" removed from cracked list.")
                            break

                if queued_flag == False and cracked_flag == False:
                    context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text=app_name+" not found in queued and cracked list. Checking in uncracked list...")
                    f = open(uncracked_requests_file, "r")
                    uncracked_apps = f.readlines()
                    f.close()
                    for uncracked_app in uncracked_apps:
                        uncracked_app_name = uncracked_app.split("@@")[0].replace(u'\xa0', u' ').strip().strip('\u200e')
                        uncracked_app_link = uncracked_app.split('@@')[1].strip()
                        print(uncracked_app_name)
                        print(app_name)
                        if uncracked_app_name == app_name:
                            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text=app_name+" found in uncracked list. Removing...")
                            f = open(uncracked_requests_file, "w")
                            for uncracked_app in uncracked_apps:
                                uncracked_app_name = uncracked_app.split("@@")[0].replace(u'\xa0', u' ').strip().strip('\u200e')
                                uncracked_app_link = uncracked_app.split('@@')[1].strip()
                                if uncracked_app_name != app_name:
                                    f.write(uncracked_app_name+"@@"+uncracked_app_link+"\n")
                            uncracked_flag = True
                            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text=app_name+" removed from uncracked list.")
                            break

                if queued_flag == False and cracked_flag == False and uncracked_flag == False:
                    context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text=app_name+" not found in any list. Nothing removed from anywhere. Please check again.")
                
            else:
                context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Invalid link")
        else:
            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Link not found.")      

def start(update, context):
    if not is_topic_allowed(update):
        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Topic not authorized")
        return
    context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Use /help for list of commands")
        

def help(update, context):
    if not is_topic_allowed(update):
        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Topic not authorized")
        return
    context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text='1. authorize: /authorize (reply to user message to authorize the user)\n2. unauthorize: /unauthorize (reply to user message to unauthorize the user)\n3. listauthusers: /listauthusers\n4. authorize_topic: /authorize_topic\n5. unauthorize_topic: /unauthorize_topic\n6. listauthtopics: /listauthtopics\n7. info: /info (reply to user message to get user info)\n8. request: /request <link of app from app store>\n9. get_queued: /get_queued\n10. get_cracked: /get_cracked\n11. get_uncracked: /get_uncracked\n12. cracked: /cracked <link of app from app store> <link where crack is uploaded>\n13. uncracked: /uncracked <link of app from app store>')
        

def send(update, context):
    if not is_allowed(update):
        sent_message = context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text='You are not authorized to use this command.')
        context.bot.deleteMessage(message_id=update.message.message_id, chat_id=update.message.chat_id)
        context.bot.deleteMessage(message_id=sent_message.message_id, chat_id=update.message.chat_id)
        

def not_a_command(update, context):
    if not is_owner(update) and is_topic_allowed(update):
        sent_message = context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text="Not a command")
        context.bot.deleteMessage(message_id=update.message.message_id, chat_id=update.message.chat_id)
        context.bot.deleteMessage(message_id=sent_message.message_id, chat_id=update.message.chat_id)
    

if __name__ == '__main__':
    for file in (queued_requests_file, cracked_requests_file, uncracked_requests_file,authorized_users_file, authorized_topics_file):
        open(file, "a").close()
    updater = Updater(telegram_bot_token)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('authorize', authorize))
    dp.add_handler(CommandHandler('authorize_topic', authorize_topic))
    dp.add_handler(CommandHandler('unauthorize', unauthorize))
    dp.add_handler(CommandHandler('unauthorize_topic', unauthorize_topic))
    dp.add_handler(CommandHandler('listauthusers', listauthusers))
    dp.add_handler(CommandHandler('listauthtopics', listauthtopics))
    dp.add_handler(CommandHandler('info', info))
    dp.add_handler(CommandHandler('request', request))
    dp.add_handler(CommandHandler('cracked', cracked))
    dp.add_handler(CommandHandler('uncracked', uncracked))
    dp.add_handler(CommandHandler('get_queued', get_queued))
    dp.add_handler(CommandHandler('get_cracked', get_cracked))
    dp.add_handler(CommandHandler('get_uncracked', get_uncracked))
    dp.add_handler(CommandHandler('remove', remove))
    dp.add_handler(CommandHandler('send', send))
    dp.add_handler(MessageHandler(Filters.all, not_a_command))

    updater.start_polling()
    updater.idle()
