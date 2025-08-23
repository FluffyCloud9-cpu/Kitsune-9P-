# telebot_key_inline_buttons_delay_banner.py
import os
import telebot
from telebot import types
import random
import threading
import time
import json
import shutil
from colorama import Fore, Style, init

init(autoreset=True)

# ---------- Cleanup ----------
if os.path.exists("tg_data") and os.path.isdir("tg_data"):
    try:
        shutil.rmtree("tg_data")
    except Exception:
        pass

KEY_FILE_TXT = "key.txt"
KEY_FILE_JSON = "key.json"
BOT_TOKEN = None
ADMIN_ID = None  # Telegram user ID of the admin

CHOICES = {
    1: "Garena",
    2: "Mobile legend",
    3: "SSO",
    4: "100082",
    5: "Roblox",
    6: "Steam",
    7: "Authgop",
    8: "Freefire",
    9: "Paypal",
    10: "Facebook",
    11: "Valorant",
    12: "Gaslight",
    13: "Discord",
    14: "Tiktok",
    15: "Spotify"
}

BANNER = f"""{Fore.CYAN}
██╗  ██╗███████╗███╗   ██╗███████╗██╗   ██╗
██║ ██╔╝██╔════╝████╗  ██║╚══███╔╝██║   ██║
█████╔╝ █████╗  ██╔██╗ ██║  ███╔╝ ██║   ██║
██╔═██╗ ██╔══╝  ██║╚██╗██║ ███╔╝  ██║   ██║
██║  ██╗███████╗██║ ╚████║███████╗╚██████╔╝
╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝╚══════╝ ╚═════╝ 
{Style.RESET_ALL}"""

# ---------- Helpers ----------
def load_keys_json():
    if not os.path.exists(KEY_FILE_JSON):
        return []
    with open(KEY_FILE_JSON, "r") as f:
        return json.load(f)

def save_keys_json(keys):
    with open(KEY_FILE_JSON, "w") as f:
        json.dump(keys, f, indent=2)

def load_bot_token():
    global BOT_TOKEN, ADMIN_ID
    if os.path.exists(KEY_FILE_TXT):
        with open(KEY_FILE_TXT, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
            if lines:
                BOT_TOKEN = lines[0]
                # Optional: store admin telegram ID on second line
                if len(lines) > 1:
                    try:
                        ADMIN_ID = int(lines[1])
                    except ValueError:
                        ADMIN_ID = None
                initial_keys = lines[2:]
                if initial_keys:
                    save_keys_json(initial_keys)

def print_center_banner():
    os.system("clear")
    try:
        width = os.get_terminal_size().columns
    except OSError:
        width = 80
    for line in BANNER.split("\n"):
        print(line.center(width))

# ---------- Bot ----------
def start_bot():
    load_bot_token()
    if not BOT_TOKEN:
        print(Fore.RED + "❌ Bot token not found in key.txt!" + Style.RESET_ALL)
        return
    if not ADMIN_ID:
        print(Fore.YELLOW + "⚠️ Admin ID not set in key.txt (optional, admin commands won't work)" + Style.RESET_ALL)

    bot = telebot.TeleBot(BOT_TOKEN)

    # ----- /start -----
    @bot.message_handler(commands=['start'])
    def start_cmd(message):
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(types.KeyboardButton("/key"))
        bot.send_message(message.chat.id, "👋 Welcome! Tap /key to enter your key.", reply_markup=kb)

    # ----- /key -----
    @bot.message_handler(commands=['key'])
    def ask_key(message):
        msg = bot.send_message(message.chat.id, "🔑 Please enter your key:")
        bot.register_next_step_handler(msg, check_key)

    def check_key(message):
        user_key = (message.text or "").strip()
        if not user_key:
            bot.reply_to(message, "❌ Key cannot be empty.")
            return
        allowed = set(load_keys_json())
        if user_key in allowed:
            markup = types.InlineKeyboardMarkup(row_width=3)
            buttons = [types.InlineKeyboardButton(label, callback_data=f"choice_{num}") for num, label in CHOICES.items()]
            markup.add(*buttons)
            bot.send_message(message.chat.id, "📋 Please choose an option:", reply_markup=markup)
        else:
            bot.reply_to(message, "❌ Invalid key.")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("choice_"))
    def handle_choice(call):
        choice_num = int(call.data.split("_")[1])
        choice_label = CHOICES.get(choice_num, "Unknown")
        bot.answer_callback_query(call.id, text=f"You chose {choice_label}")
        bot.send_message(call.message.chat.id, f"⏳ Processing {choice_label}... Please wait.")
        threading.Thread(target=delayed_busy_message, args=(bot, call.message.chat.id)).start()

    def delayed_busy_message(bot_instance, chat_id):
        delay = random.randint(30, 60)
        time.sleep(delay)
        bot_instance.send_message(chat_id, "⚠️ Please try again later, server is busy.")

    # ----- Admin-only: /addkey -----
    @bot.message_handler(commands=['addkey'])
    def add_key_cmd(message):
        if ADMIN_ID and message.from_user.id != ADMIN_ID:
            bot.reply_to(message, "❌ You are not authorized to add keys.")
            return
        msg = bot.send_message(message.chat.id, "🔑 Enter new key to add:")
        bot.register_next_step_handler(msg, add_key)

    def add_key(message):
        key = (message.text or "").strip()
        if not key:
            bot.reply_to(message, "❌ Key cannot be empty.")
            return
        keys = load_keys_json()
        if key in keys:
            bot.reply_to(message, "⚠️ Key already exists!")
        else:
            keys.append(key)
            save_keys_json(keys)
            bot.reply_to(message, f"✅ Key '{key}' added!")

    # ----- Admin-only: /delkey -----
    @bot.message_handler(commands=['delkey'])
    def del_key_cmd(message):
        if ADMIN_ID and message.from_user.id != ADMIN_ID:
            bot.reply_to(message, "❌ You are not authorized to delete keys.")
            return
        keys = load_keys_json()
        if not keys:
            bot.reply_to(message, "❌ No keys to delete!")
            return
        kb = types.InlineKeyboardMarkup(row_width=2)
        for i, k in enumerate(keys, 1):
            kb.add(types.InlineKeyboardButton(k, callback_data=f"del_{i-1}"))
        bot.send_message(message.chat.id, "🗑️ Select key to delete:", reply_markup=kb)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("del_"))
    def handle_del_key(call):
        index = int(call.data.split("_")[1])
        keys = load_keys_json()
        if 0 <= index < len(keys):
            removed = keys.pop(index)
            save_keys_json(keys)
            bot.edit_message_text(f"✅ Key '{removed}' deleted!", call.message.chat.id, call.message.message_id)
        else:
            bot.answer_callback_query(call.id, "❌ Invalid key index.")

    print(Fore.GREEN + "\n🤖 Bot is running... Press Ctrl+C to stop.")
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        print(Fore.CYAN + "\n⏹️ Bot stopped by user.")
    except Exception as e:
        print(Fore.RED + f"❌ Error while running bot: {e}")

# ---------- Main ----------
if __name__ == "__main__":
    print_center_banner()
    load_bot_token()
    start_bot()
