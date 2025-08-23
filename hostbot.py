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
    except:
        pass
        
KEY_FILE_TXT = "key.txt"
KEY_FILE_JSON = "key.json"
BOT_TOKEN = None

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

def pause_and_clear():
    input(Fore.YELLOW + "\nPress Enter to return to main menu..." + Style.RESET_ALL)
    os.system("clear")
    print_center_banner()

def print_center_banner():
    os.system("clear")
    try:
        width = os.get_terminal_size().columns
    except OSError:
        width = 80
    for line in BANNER.split("\n"):
        print(line.center(width))

# ---------- Menu ----------
def menu():
    global BOT_TOKEN
    print_center_banner()

    # Load bot token and keys from key.txt
    if os.path.exists(KEY_FILE_TXT):
        with open(KEY_FILE_TXT, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
            if lines:
                BOT_TOKEN = lines[0]
                initial_keys = lines[1:]
                if initial_keys:
                    save_keys_json(initial_keys)

    while True:
        print(Fore.MAGENTA + "\n===== BOT MENU =====" + Style.RESET_ALL)
        print(Fore.CYAN + "[1]" + Fore.WHITE + " > Create/Add KEY")
        print(Fore.CYAN + "[2]" + Fore.WHITE + " > Delete KEY")
        print(Fore.CYAN + "[3]" + Fore.WHITE + " > Start bot")
        print(Fore.CYAN + "[4]" + Fore.WHITE + " > Exit")
        print(Fore.MAGENTA + "====================" + Style.RESET_ALL)
        choice = input(Fore.GREEN + "Choose a menu: " + Style.RESET_ALL).strip()

        if choice == "1":
            key = input(Fore.GREEN + "Enter new key: " + Style.RESET_ALL).strip()
            if not key:
                print(Fore.RED + "❌ Key cannot be empty!")
            else:
                keys = load_keys_json()
                if key in keys:
                    print(Fore.YELLOW + "⚠️ Key already exists!")
                else:
                    keys.append(key)
                    save_keys_json(keys)
                    print(Fore.GREEN + "✅ Key added!")
            pause_and_clear()

        elif choice == "2":
            keys = load_keys_json()
            if not keys:
                print(Fore.RED + "❌ No keys to delete!")
                pause_and_clear()
                continue

            print(Fore.CYAN + "Current keys:" + Style.RESET_ALL)
            for i, k in enumerate(keys, 1):
                print(f"[{i}] {k}")
            num = input(Fore.GREEN + "Enter the number of the key to delete: " + Style.RESET_ALL).strip()
            if not num.isdigit() or int(num) < 1 or int(num) > len(keys):
                print(Fore.RED + "❌ Invalid number!")
            else:
                removed = keys.pop(int(num)-1)
                save_keys_json(keys)
                print(Fore.GREEN + f"✅ Key '{removed}' deleted!")
            pause_and_clear()

        elif choice == "3":
            if not BOT_TOKEN:
                print(Fore.RED + "❌ Bot token not found in key.txt!")
                pause_and_clear()
            else:
                keys = load_keys_json()
                if not keys:
                    print(Fore.RED + "❌ No keys found! Add at least one key.")
                    pause_and_clear()
                else:
                    start_bot()
                    pause_and_clear()

        elif choice == "4":
            print(Fore.CYAN + "👋 Exiting program...")
            exit()

        else:
            print(Fore.RED + "❌ Invalid choice! Please enter 1–4.")
            pause_and_clear()

# ---------- Bot ----------
def start_bot():
    bot = telebot.TeleBot(BOT_TOKEN)

    @bot.message_handler(commands=['start'])
    def start_cmd(message):
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(types.KeyboardButton("/key"))
        bot.send_message(message.chat.id, "👋 Welcome! Tap /key to enter your key.", reply_markup=kb)

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
    try:
        # Try interactive menu
        menu()
    except EOFError:
        # If stdin is missing (non-interactive, e.g. auto-launch from script.py)
        print(Fore.YELLOW + "⚠️ No interactive input available. Auto-starting bot..." + Style.RESET_ALL)
        if BOT_TOKEN:
            start_bot()
        else:
            print(Fore.RED + "❌ Bot token not found in key.txt!" + Style.RESET_ALL)
