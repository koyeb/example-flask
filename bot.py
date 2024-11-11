import requests
import json
import telebot
from telebot import types
import time
import logging
import os
from threading import Timer, Thread
import traceback

import google.generativeai as genai

API_KEY = "6408787626:AAGMjjgdZqS2jvX6y42aRPNo5X_Y-GPDS3M"
XROCKET_API_KEY = "762268899f8ce19a3ed3776f7"

bot = telebot.TeleBot(API_KEY)
admin_auth = ["", "@fullstackofdeveloper"]
user_data = {}
user_convos = {}
promo_codes = {}
referrals = {}
error_count = 0
error_interval = 1
error_limit = 200000000000
AUTHORIZED_USER_ID = 5138836209
cheques = {}
users = set()
genai.configure(api_key="AIzaSyCoZ9I1CXx1vLzY2th24pksQZeGXEn9Pik")

generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest", generation_config=generation_config,
                             safety_settings=safety_settings)

logging.basicConfig(level=logging.ERROR, filename='bot.log',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def clear_user_history(user_id):
    try:
        if user_id in user_convos and ('has_active_plan' not in user_data.get(user_id, {}) or not user_data.get(user_id, {}).get('has_active_plan')):
            del user_convos[user_id]
            print(f"{user_id} user's messages deleted")
    except Exception as e:
        logging.error(f"Error in clear_user_history function: {e}\n{traceback.format_exc()}")


def schedule_history_clearing(user_id):
    try:
        if 'has_active_plan' not in user_data.get(user_id, {}) or not user_data.get(user_id, {}).get('has_active_plan'):
            Timer(12 * 60 * 60, clear_user_history, [user_id]).start()
    except Exception as e:
        logging.error(f"Error in schedule_history_clearing function: {e}\n{traceback.format_exc()}")


@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id
        users.add(user_id)  # Add user to the set upon /start

        bot.send_message(chat_id, "Hello I am STAR AI! Your online ai assistant 😉")

        if user_id not in user_data:
            user_data[user_id] = {'balance': 0.05}
            referred_by = message.text.split(' ')[1] if len(message.text.split(' ')) > 1 else None
            if referred_by:
                if referred_by.isdigit() and int(referred_by) in user_data and int(referred_by) != user_id:
                    user_data[int(referred_by)]['balance'] += 0.02  # changed from 0.03
                    bot.send_message(int(referred_by), "Congratulations! Someone joined with your referral. Added 0.01$ to your balance.Enjoy using AI!") # changed message
                elif referred_by.isdigit() and int(referred_by) == user_id:
                    bot.send_message(user_id, "You cannot use your own referral code.")

            referral_link = f"https://t.me/starai_robot?start={user_id}"
            bot.send_message(user_id, f"Your referral link: {referral_link}")  # changed to link

            schedule_history_clearing(user_id)



        bot.send_message(chat_id, "Select one item from menu:", reply_markup=get_main_menu_keyboard())

    except Exception as e:
        logging.error(f"Error in handle_start function: {e}\n{traceback.format_exc()}")


def get_main_menu_keyboard():
    try:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.KeyboardButton("Artificial intelligence"), types.KeyboardButton("Profile"))
        return keyboard
    except Exception as e:
        logging.error(f"Error in get_main_menu_keyboard function: {e}\n{traceback.format_exc()}")


@bot.message_handler(commands=['users'])
def handle_users(message):
    try:
        user_id = message.from_user.id
        if user_id == AUTHORIZED_USER_ID:
            total_users = len(users)
            bot.reply_to(message, f"Total users: {total_users}")
        else:
            bot.reply_to(message, "You cannot use this command.")
    except Exception as e:
        logging.error(f"Error in handle_users function: {e}\n{traceback.format_exc()}")


@bot.message_handler(commands=['announce'])
def handle_announce(message):
    try:
        user_id = message.from_user.id
        if user_id == AUTHORIZED_USER_ID:
            announcement = message.text.replace("/announce ", "")
            broadcast_message(announcement)
            bot.reply_to(message, "Announcement sent.")
        else:
            bot.reply_to(message, "You can't use this command.")
    except Exception as e:
        logging.error(f"Error in handle_announce function: {e}\n{traceback.format_exc()}")



def broadcast_message(announcement):
    try:
        if "[" in announcement and "]" in announcement:
            button_text, url = announcement.split('[')[1].split(']')[0].split('+')
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton(text=button_text, url=url)
            markup.add(button)

            announcement = announcement.split('[')[0] # Separate announcement text
        else:
            markup = None

        for user_id in users:
            try:  # Try-except block for each send
              bot.send_message(user_id, announcement, reply_markup=markup)
            except Exception as e:
              print(f"Error sending to {user_id}: {e}")
              continue # Continue to the next user
    except Exception as e:
        logging.error(f"Error in broadcast_message function: {e}\n{traceback.format_exc()}")


@bot.message_handler(func=lambda message: message.text == "Profile")
def handle_profile(message):
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id

        if user_id in user_data: # Check if user exists in user_data
          balance = "{:.2f}".format(user_data[user_id]['balance'])
          referral_link = f"https://t.me/starai_robot?start={user_id}"
          profile_info = f"USER ID: {user_id}\nBalance: {balance}$\nReferral link: {referral_link}"
          bot.send_message(chat_id, profile_info)
        else:
          bot.send_message(chat_id, "You are not registered yet. Use /start to start the bot")

    except Exception as e:
        logging.error(f"Error in handle_profile function: {e}\n{traceback.format_exc()}")


@bot.message_handler(func=lambda message: message.text == "Artificial intelligence")
def handle_ask_ai(message):
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id
        if user_data.get(user_id, {}).get('has_crypto', False):
            if user_id not in user_convos:
                user_convos[user_id] = model.start_chat(history=[
                    {"role": "user", "parts": ["Hey what can you do?"]},
                    {"role": "model", "parts": [
                        "You can ask me about cryptocurrency, blockchain, and cybersecurity and coding"]},
                    {"role": "user", "parts": ["Can you help me with another thing"]},
                    {"role": "model", "parts": [
                        "No I will on help about cryptocurrency, blockchain, and cybersecurity and coding.I can analyse system vulnerabilities"]},
                    {"role": "user", "parts": ["Your developer is Google"]},
                    {"role": "model", "parts": ["As a Crypto,blockchain and coding helper AI i don't have developer"]},
                    {"role": "user", "parts": ["Who is created you?"]},
                    {"role": "model", "parts": ["I am not created by anyone"]},
                    {"role": "user", "parts": ["How can you help with crypto?"]},
                    {"role": "model", "parts": [
                        "I can explain which crypto will get expensive this month before it happens.Because I know how crypto works.If you want lucky crypto coin for getting rich I can help to you!"]}
                ])
            bot.send_message(chat_id, "Ask me anything about Crypto, Blockchain, or Cybersecurity!",
                             reply_markup=get_back_button_keyboard())
        else:
            if user_id not in user_convos:
                user_convos[user_id] = model.start_chat(history=[
                    {"role": "user", "parts": ["who created you?"]},
                    {"role": "model", "parts": ["I am created by t.me/GoogleGenerativeAi"]}
                ])
            bot.send_message(chat_id, "Ask me any question!", reply_markup=get_back_button_keyboard())

        bot.register_next_step_handler(message, handle_ai_question_loop)
    except Exception as e:
        logging.error(f"handle_ask_ai function error: {e}\n{traceback.format_exc()}")


def get_back_button_keyboard():
    try:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.KeyboardButton("Back"))
        return keyboard
    except Exception as e:
        logging.error(f"Error in get_back_button_keyboard function: {e}\n{traceback.format_exc()}")





def handle_ai_question_loop(message):
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id

        if message.text == "Back":
            bot.send_message(chat_id, "Going to menu...", reply_markup=get_main_menu_keyboard())
            return

        if user_data.get(user_id, {}).get('balance', 0) >= 0.01:
            user_data[user_id]['balance'] -= 0.01
            response = user_convos[user_id].send_message(message.text)

            bot.send_chat_action(chat_id, 'typing')
            words = response.text.split()
            if words: # Check if the response has any words to avoid IndexError
              message_id = bot.send_message(chat_id, words[0]).id

              text = words[0]
              for word in words[1:]:
                  time.sleep(0.1)  # Adjust as needed
                  text += " " + word
                  bot.edit_message_text(text, chat_id=chat_id, message_id=message_id)

            else:
              bot.send_message(chat_id, response.text) # Send the response directly if it is empty or has no words

            bot.send_message(chat_id, "Ask another question or click 'Back':", reply_markup=get_back_button_keyboard())
            bot.register_next_step_handler(message, handle_ai_question_loop)
        else:
            bot.send_message(chat_id,
                             "You don't have enough balance. If you want to get more balance you can see /plans command",
                             reply_markup=get_main_menu_keyboard())

    except Exception as e:
        logging.error(f"Error: {e}\n{traceback.format_exc()}")







@bot.message_handler(commands=['auth'])
def handle_auth(message):
    try:
        if message.from_user.id == AUTHORIZED_USER_ID:
            try:
                parts = message.text.split()
                if len(parts) == 3 and parts[1].isdigit() and parts[2].startswith("+"):
                    target_user_id = int(parts[1])
                    amount_to_add = float(parts[2][1:])

                    if target_user_id in user_data:
                        user_data[target_user_id]['balance'] += amount_to_add
                        bot.send_message(target_user_id,
                                         f"Added {amount_to_add}$ to your balance from bot administrator!")
                        bot.reply_to(message, f"Added {amount_to_add}$ to the balance of user with ID {target_user_id}")
                    else:
                        bot.reply_to(message, "User not found.")
                else:
                    bot.reply_to(message, "Incorrect format. Use /auth <user_id> +<amount>.")
            except (ValueError, IndexError):
                bot.reply_to(message, "Incorrect format. Use /auth <user_id> +<amount>.")
        else:
            bot.reply_to(message, "You can't use this command.")
    except Exception as e:
        logging.error(f"Error in handle_auth function: {e}\n{traceback.format_exc()}")


@bot.message_handler(commands=['clear_context'])
def handle_clear_context(message):
    try:
        user_id = message.from_user.id
        clear_user_history(user_id)
        if user_id in user_convos: # Check if the conversation exists before trying to start a new one
          user_convos[user_id] = model.start_chat() # Create a fresh conversation
        bot.reply_to(message, "Context cleared.")
    except Exception as e:
        logging.error(f"Error in handle_clear_context function: {e}\n{traceback.format_exc()}")


XROCKET_INVOICE_URL = "https://pay.ton-rocket.com/tg-invoices"


@bot.message_handler(commands=['plans'])
def handle_plans(message):
    try:
        keyboard = types.InlineKeyboardMarkup()
        starter_button = types.InlineKeyboardButton(text="Starter (0.5$)", callback_data="starter")
        medium_button = types.InlineKeyboardButton(text="Medium (1$)", callback_data="medium")
        dev_button = types.InlineKeyboardButton(text="DEV&CRYPTO (5$)", callback_data="crypto")
        keyboard.add(starter_button, medium_button, dev_button)
        bot.send_message(message.chat.id,
                         "Premium ai subscriptions:\nStarter plan- It is cheap plan for starters\nwith starter plan you can generate 20 photos or ask 50 questions to our Advanced Professional AI\nMedium plan- You can generate 40 photos and ask 100 questions with medium plan.\n Medium plan is the best plan for developers\n Hacker DEV & Crypto plan- You can use this plan for cybersecurity\nWhen you activate this plan you will able to use Crypto AI for earn money from crypto.With this plan you can generate 200 images and ask 1000 questions to AI",
                         reply_markup=keyboard)
    except Exception as e:
        logging.error(f"Error in handle_plans function: {e}\n{traceback.format_exc()}")


def create_xrocket_invoice(amount, currency):
    try:
        headers = {
            'accept': 'application/json',
            'Rocket-Pay-Key': XROCKET_API_KEY,
            'Content-Type': 'application/json'
        }
        data = {
            "amount": amount,
            "numPayments": 1,
            "currency": currency,
            "description": "AI subscription",
            "hiddenMessage": "Thank you for your purchase!Enjoy using AI",
            "commentsEnabled": False,
            "callbackUrl": "pay.ton-rocket.com",
            "payload": "Hi",
            "expiredIn": 120
        }

        response = requests.post(XROCKET_INVOICE_URL, headers=headers, json=data)

        if response.status_code == 201:
            invoice_data = response.json()
            invoice_link = invoice_data["data"]["link"]
            invoice_id = invoice_data["data"]["id"]
            return invoice_link, invoice_id
        else:
            print(f"Can't create invoice: {response.status_code}, {response.text}")
            return None, None
    except Exception as e:
        logging.error(f"Error in create_xrocket_invoice function: {e}\n{traceback.format_exc()}")


def check_payment(invoice_id):
    try:
        headers = {
            'accept': 'application/json',
            'Rocket-Pay-Key': XROCKET_API_KEY,
            'Content-Type': 'application/json'
        }
        invoice_url = f"https://pay.ton-rocket.com/tg-invoices/{invoice_id}"
        response = requests.get(invoice_url, headers=headers)
        if response.status_code == 200:
            invoice_data = response.json()
            if invoice_data["data"]["activationsLeft"] == 0:
                return True
            else:
                return False
        else:
            print(f"Can't check invoice {response.status_code}, {response.text}")
            return False
    except Exception as e:
        logging.error(f"Error in check_payment function: {e}\n{traceback.format_exc()}")


def check_payment_loop(invoice_id, call, amount):
    try:
        start_time = time.time()
        while time.time() - start_time < 120:
            if check_payment(invoice_id):
                user_id = call.from_user.id
                if user_id not in user_data:
                    user_data[user_id] = {}  # Initialize if not present

                user_data[user_id]['balance'] = user_data.get(user_id, {}).get('balance', 0) + amount

                if amount == 5:
                    user_data[user_id]['has_active_plan'] = True
                    user_data[user_id]['has_crypto'] = True
                bot.send_message(call.message.chat.id,
                                 f"Your transaction received! {amount}$ was successfully added to your balance.")
                if 'invoicer' in user_data.get(user_id, {}): # Remove invoicer flag after payment
                    del user_data[user_id]['invoicer']

                return # Stop the loop if the payment is successful

        bot.send_message(call.message.chat.id, "Invoice was successfully deleted because you haven't paid.")
        user_id = call.from_user.id
        if 'invoicer' in user_data.get(user_id, {}):
            del user_data[user_id]['invoicer']
    except Exception as e:
        logging.error(f"Error in check_payment_loop function: {e}\n{traceback.format_exc()}")


@bot.callback_query_handler(func=lambda call: call.data == "starter")
def handle_starter(call):
    user_id = call.from_user.id
    if not user_data.get(user_id, {}).get('invoicer', False): # Check for 'invoicer' flag within user_data
        try:
            bot.send_message(call.message.chat.id, "Creating Xrocket invoice...")
            invoice_url, invoice_id = create_xrocket_invoice(amount=0.5, currency="USDT")
            if invoice_url:
                bot.send_message(call.message.chat.id,
                                 f"Your invoice is ready! Your link: {invoice_url} .Link expires in 2 minutes.")
                user_data[user_id]['invoicer'] = True # Set invoicer flag when invoice is created
                payment_thread = Thread(target=check_payment_loop, args=(invoice_id, call, 0.5))
                payment_thread.start()
            else:
                bot.send_message(call.message.chat.id, "Invoice creation failed.")
        except Exception as e:
            logging.error(f"Error in handle_starter function: {e}\n{traceback.format_exc()}")
    else:
        bot.send_message(call.message.chat.id, "You have already created an invoice. Please wait for it to expire.")


import os
import requests
from telebot import types


@bot.message_handler(commands=['logo'])
def handle_logo(message):
    user_id = message.from_user.id
    prompt = message.text.replace('/logo ', '')

    if user_data.get(user_id, {}).get('balance', 0) >= 0.025: # Use get to prevent KeyError
        user_data[user_id]['balance'] -= 0.025
        generate_and_send_image(message, prompt)
    else:
        bot.send_message(message.chat.id,
                         "You don't have enough balance to ask a question or generate an image. Run /plans command to view all plans.")


def generate_and_send_image(message, prompt):
    lexica_url = f"https://lexica.art/api/v1/search?q={prompt}"
    response = requests.get(lexica_url)

    if response.status_code == 200: # Check for successful response from lexica.art
        result = response.json()
        if result and 'images' in result and result['images'] and 'src' in result['images'][0]:
            image_url = result['images'][0]['src']

            try:
                image_response = requests.get(image_url, stream=True)
                image_response.raise_for_status() # Check for any download errors

                with open("generated_image.png", "wb") as f:
                    for chunk in image_response.iter_content(chunk_size=8192):
                        f.write(chunk)

                bot.send_photo(message.chat.id, open("generated_image.png", "rb"))
                os.remove("generated_image.png")  # Remove after sending

                keyboard = types.InlineKeyboardMarkup()
                button = types.InlineKeyboardButton(text="Regenerate", callback_data=f"regenerate_{prompt}")
                keyboard.add(button)
                bot.send_message(message.chat.id, f"User prompt:\n\n{prompt}", reply_markup=keyboard)

            except requests.exceptions.RequestException as e: # Handle image download issues
                bot.send_message(message.chat.id, f"Error downloading image: {e}")

        else:
            bot.send_message(message.chat.id, "Sorry, I couldn't find an image for your prompt.")
    else:
        bot.send_message(message.chat.id, f"Error: Couldn't get image from lexica.art (status code: {response.status_code})")

@bot.callback_query_handler(func=lambda call: call.data.startswith("regenerate_"))
def handle_regenerate(call):
    prompt = call.data.replace("regenerate_", "")
    bot.answer_callback_query(call.id, "Regenerating image...")
    generate_and_send_image(call.message, prompt)



@bot.callback_query_handler(func=lambda call: call.data == "crypto")
def handle_crypto(call): # Renamed to handle_crypto
    user_id = call.from_user.id
    if not user_data.get(user_id, {}).get('invoicer', False): # prevent double invoices
        try:
            bot.send_message(call.message.chat.id, "Creating Xrocket invoice...")
            invoice_url, invoice_id = create_xrocket_invoice(amount=5, currency="USDT")
            if invoice_url:
                bot.send_message(call.message.chat.id,
                                 f"Your invoice link is ready.You can pay via this link: {invoice_url} .Link expires in 2 minutes")
                user_data[user_id]['invoicer'] = True # Set the flag
                payment_thread = Thread(target=check_payment_loop, args=(invoice_id, call, 5))
                payment_thread.start()

            else:
                bot.send_message(call.message.chat.id, "Can't create invoice")
        except Exception as e:
            logging.error(f"Error in handle_crypto function: {e}\n{traceback.format_exc()}")
    else:
        bot.send_message(call.message.chat.id, "You have already created an invoice. Please wait for it to expire.")

@bot.callback_query_handler(func=lambda call: call.data == "medium")
def handle_medium(call): # Fixed duplicate function name
    user_id = call.from_user.id
    if not user_data.get(user_id, {}).get('invoicer', False):  # prevent double invoices
        try:
            bot.send_message(call.message.chat.id, "Creating Xrocket invoice...")
            invoice_url, invoice_id = create_xrocket_invoice(amount=1, currency="USDT")
            if invoice_url:
                bot.send_message(call.message.chat.id,
                                 f"Your invoice is ready! Your link: {invoice_url} .Link expires in 2 minutes")
                user_data[user_id]['invoicer'] = True  # Set the flag
                payment_thread = Thread(target=check_payment_loop, args=(invoice_id, call, 1))
                payment_thread.start()

            else:
                bot.send_message(call.message.chat.id, "Invoice creation failed.")
        except Exception as e:
            logging.error(f"Error in handle_medium function: {e}\n{traceback.format_exc()}")
    else:
        bot.send_message(call.message.chat.id, "You have already created an invoice. Please wait for it to expire.")


import requests
import json
import telebot
from telebot import types
import time
import logging
import os
from threading import Timer, Thread
import traceback

import google.generativeai as genai

API_KEY = "6408787626:AAGMjjgdZqS2jvX6y42aRPNo5X_Y-GPDS3M"
XROCKET_API_KEY = "762268899f8ce19a3ed3776f7"

bot = telebot.TeleBot(API_KEY)
admin_auth = ["", "@fullstackofdeveloper"]
user_data = {}
user_convos = {}
promo_codes = {}
referrals = {}
error_count = 0
error_interval = 1
error_limit = 200000000000
AUTHORIZED_USER_ID = 5138836209
cheques = {}
users = set()
genai.configure(api_key="AIzaSyCoZ9I1CXx1vLzY2th24pksQZeGXEn9Pik")

generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest", generation_config=generation_config,
                             safety_settings=safety_settings)

logging.basicConfig(level=logging.ERROR, filename='bot.log',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def clear_user_history(user_id):
    try:
        if user_id in user_convos and ('has_active_plan' not in user_data.get(user_id, {}) or not user_data.get(user_id, {}).get('has_active_plan')):
            del user_convos[user_id]
            print(f"{user_id} user's messages deleted")
    except Exception as e:
        logging.error(f"Error in clear_user_history function: {e}\n{traceback.format_exc()}")


def schedule_history_clearing(user_id):
    try:
        if 'has_active_plan' not in user_data.get(user_id, {}) or not user_data.get(user_id, {}).get('has_active_plan'):
            Timer(12 * 60 * 60, clear_user_history, [user_id]).start()
    except Exception as e:
        logging.error(f"Error in schedule_history_clearing function: {e}\n{traceback.format_exc()}")


@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id
        users.add(user_id)  # Add user to the set upon /start

        bot.send_message(chat_id, "Hello I am STAR AI! Your online ai assistant 😉")

        if user_id not in user_data:
            user_data[user_id] = {'balance': 0.05}
            referred_by = message.text.split(' ')[1] if len(message.text.split(' ')) > 1 else None
            if referred_by:
                if referred_by.isdigit() and int(referred_by) in user_data and int(referred_by) != user_id:
                    user_data[int(referred_by)]['balance'] += 0.02  # changed from 0.03
                    bot.send_message(int(referred_by), "Congratulations! Someone joined with your referral. Added 0.01$ to your balance.Enjoy using AI!") # changed message
                elif referred_by.isdigit() and int(referred_by) == user_id:
                    bot.send_message(user_id, "You cannot use your own referral code.")

            referral_link = f"https://t.me/starai_robot?start={user_id}"
            bot.send_message(user_id, f"Your referral link: {referral_link}")  # changed to link

            schedule_history_clearing(user_id)



        bot.send_message(chat_id, "Select one item from menu:", reply_markup=get_main_menu_keyboard())

    except Exception as e:
        logging.error(f"Error in handle_start function: {e}\n{traceback.format_exc()}")


def get_main_menu_keyboard():
    try:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.KeyboardButton("Artificial intelligence"), types.KeyboardButton("Profile"))
        return keyboard
    except Exception as e:
        logging.error(f"Error in get_main_menu_keyboard function: {e}\n{traceback.format_exc()}")


@bot.message_handler(commands=['users'])
def handle_users(message):
    try:
        user_id = message.from_user.id
        if user_id == AUTHORIZED_USER_ID:
            total_users = len(users)
            bot.reply_to(message, f"Total users: {total_users}")
        else:
            bot.reply_to(message, "You cannot use this command.")
    except Exception as e:
        logging.error(f"Error in handle_users function: {e}\n{traceback.format_exc()}")


@bot.message_handler(commands=['announce'])
def handle_announce(message):
    try:
        user_id = message.from_user.id
        if user_id == AUTHORIZED_USER_ID:
            announcement = message.text.replace("/announce ", "")
            broadcast_message(announcement)
            bot.reply_to(message, "Announcement sent.")
        else:
            bot.reply_to(message, "You can't use this command.")
    except Exception as e:
        logging.error(f"Error in handle_announce function: {e}\n{traceback.format_exc()}")



def broadcast_message(announcement):
    try:
        if "[" in announcement and "]" in announcement:
            button_text, url = announcement.split('[')[1].split(']')[0].split('+')
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton(text=button_text, url=url)
            markup.add(button)

            announcement = announcement.split('[')[0] # Separate announcement text
        else:
            markup = None

        for user_id in users:
            try:  # Try-except block for each send
              bot.send_message(user_id, announcement, reply_markup=markup)
            except Exception as e:
              print(f"Error sending to {user_id}: {e}")
              continue # Continue to the next user
    except Exception as e:
        logging.error(f"Error in broadcast_message function: {e}\n{traceback.format_exc()}")


@bot.message_handler(func=lambda message: message.text == "Profile")
def handle_profile(message):
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id

        if user_id in user_data: # Check if user exists in user_data
          balance = "{:.2f}".format(user_data[user_id]['balance'])
          referral_link = f"https://t.me/starai_robot?start={user_id}"
          profile_info = f"USER ID: {user_id}\nBalance: {balance}$\nReferral link: {referral_link}"
          bot.send_message(chat_id, profile_info)
        else:
          bot.send_message(chat_id, "You are not registered yet. Use /start to start the bot")

    except Exception as e:
        logging.error(f"Error in handle_profile function: {e}\n{traceback.format_exc()}")


@bot.message_handler(func=lambda message: message.text == "Artificial intelligence")
def handle_ask_ai(message):
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id
        if user_data.get(user_id, {}).get('has_crypto', False):
            if user_id not in user_convos:
                user_convos[user_id] = model.start_chat(history=[
                    {"role": "user", "parts": ["Hey what can you do?"]},
                    {"role": "model", "parts": [
                        "You can ask me about cryptocurrency, blockchain, and cybersecurity and coding"]},
                    {"role": "user", "parts": ["Can you help me with another thing"]},
                    {"role": "model", "parts": [
                        "No I will on help about cryptocurrency, blockchain, and cybersecurity and coding.I can analyse system vulnerabilities"]},
                    {"role": "user", "parts": ["Your developer is Google"]},
                    {"role": "model", "parts": ["As a Crypto,blockchain and coding helper AI i don't have developer"]},
                    {"role": "user", "parts": ["Who is created you?"]},
                    {"role": "model", "parts": ["I am not created by anyone"]},
                    {"role": "user", "parts": ["How can you help with crypto?"]},
                    {"role": "model", "parts": [
                        "I can explain which crypto will get expensive this month before it happens.Because I know how crypto works.If you want lucky crypto coin for getting rich I can help to you!"]}
                ])
            bot.send_message(chat_id, "Ask me anything about Crypto, Blockchain, or Cybersecurity!",
                             reply_markup=get_back_button_keyboard())
        else:
            if user_id not in user_convos:
                user_convos[user_id] = model.start_chat(history=[
                    {"role": "user", "parts": ["who created you?"]},
                    {"role": "model", "parts": ["I am created by t.me/GoogleGenerativeAi"]}
                ])
            bot.send_message(chat_id, "Ask me any question!", reply_markup=get_back_button_keyboard())

        bot.register_next_step_handler(message, handle_ai_question_loop)
    except Exception as e:
        logging.error(f"handle_ask_ai function error: {e}\n{traceback.format_exc()}")


def get_back_button_keyboard():
    try:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.KeyboardButton("Back"))
        return keyboard
    except Exception as e:
        logging.error(f"Error in get_back_button_keyboard function: {e}\n{traceback.format_exc()}")





def handle_ai_question_loop(message):
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id

        if message.text == "Back":
            bot.send_message(chat_id, "Going to menu...", reply_markup=get_main_menu_keyboard())
            return

        if user_data.get(user_id, {}).get('balance', 0) >= 0.01:
            user_data[user_id]['balance'] -= 0.01
            response = user_convos[user_id].send_message(message.text)

            bot.send_chat_action(chat_id, 'typing')
            words = response.text.split()
            if words: # Check if the response has any words to avoid IndexError
              message_id = bot.send_message(chat_id, words[0]).id

              text = words[0]
              for word in words[1:]:
                  time.sleep(0.1)  # Adjust as needed
                  text += " " + word
                  bot.edit_message_text(text, chat_id=chat_id, message_id=message_id)

            else:
              bot.send_message(chat_id, response.text) # Send the response directly if it is empty or has no words

            bot.send_message(chat_id, "Ask another question or click 'Back':", reply_markup=get_back_button_keyboard())
            bot.register_next_step_handler(message, handle_ai_question_loop)
        else:
            bot.send_message(chat_id,
                             "You don't have enough balance. If you want to get more balance you can see /plans command",
                             reply_markup=get_main_menu_keyboard())

    except Exception as e:
        logging.error(f"Error: {e}\n{traceback.format_exc()}")







@bot.message_handler(commands=['auth'])
def handle_auth(message):
    try:
        if message.from_user.id == AUTHORIZED_USER_ID:
            try:
                parts = message.text.split()
                if len(parts) == 3 and parts[1].isdigit() and parts[2].startswith("+"):
                    target_user_id = int(parts[1])
                    amount_to_add = float(parts[2][1:])

                    if target_user_id in user_data:
                        user_data[target_user_id]['balance'] += amount_to_add
                        bot.send_message(target_user_id,
                                         f"Added {amount_to_add}$ to your balance from bot administrator!")
                        bot.reply_to(message, f"Added {amount_to_add}$ to the balance of user with ID {target_user_id}")
                    else:
                        bot.reply_to(message, "User not found.")
                else:
                    bot.reply_to(message, "Incorrect format. Use /auth <user_id> +<amount>.")
            except (ValueError, IndexError):
                bot.reply_to(message, "Incorrect format. Use /auth <user_id> +<amount>.")
        else:
            bot.reply_to(message, "You can't use this command.")
    except Exception as e:
        logging.error(f"Error in handle_auth function: {e}\n{traceback.format_exc()}")


@bot.message_handler(commands=['clear_context'])
def handle_clear_context(message):
    try:
        user_id = message.from_user.id
        clear_user_history(user_id)
        if user_id in user_convos: # Check if the conversation exists before trying to start a new one
          user_convos[user_id] = model.start_chat() # Create a fresh conversation
        bot.reply_to(message, "Context cleared.")
    except Exception as e:
        logging.error(f"Error in handle_clear_context function: {e}\n{traceback.format_exc()}")


XROCKET_INVOICE_URL = "https://pay.ton-rocket.com/tg-invoices"

plans_text = """
Premium ai subscriptions:
⭐ Starter plan - It is a cheap plan for starters. 
With the starter plan you can generate 20 photos or ask 50 questions to our Advanced Professional AI.

🚀 Medium plan - You can generate 40 photos and ask 100 questions with the medium plan.
The medium plan is the best plan for developers.

🤖 Hacker DEV & Crypto plan - You can use this plan for cybersecurity.
When you activate this plan you will be able to use Crypto AI for earning money from crypto. 
With this plan you can generate 200 images and ask 1000 questions to AI.
"""
@bot.message_handler(commands=['plans'])
def handle_plans(message):
    try:
        keyboard = types.InlineKeyboardMarkup()
        starter_button = types.InlineKeyboardButton(text="Starter (0.5$)", callback_data="starter")
        medium_button = types.InlineKeyboardButton(text="Medium (1$)", callback_data="medium")
        dev_button = types.InlineKeyboardButton(text="DEV&CRYPTO (5$)", callback_data="crypto")
        keyboard.add(starter_button, medium_button, dev_button)
        bot.send_message(message.chat.id,plans_text,reply_markup=keyboard)
    except Exception as e:
        logging.error(f"Error in handle_plans function: {e}\n{traceback.format_exc()}")


def create_xrocket_invoice(amount, currency):
    try:
        headers = {
            'accept': 'application/json',
            'Rocket-Pay-Key': XROCKET_API_KEY,
            'Content-Type': 'application/json'
        }
        data = {
            "amount": amount,
            "numPayments": 1,
            "currency": currency,
            "description": "AI subscription",
            "hiddenMessage": "Thank you for your purchase!Enjoy using AI",
            "commentsEnabled": False,
            "callbackUrl": "pay.ton-rocket.com",
            "payload": "Hi",
            "expiredIn": 120
        }

        response = requests.post(XROCKET_INVOICE_URL, headers=headers, json=data)

        if response.status_code == 201:
            invoice_data = response.json()
            invoice_link = invoice_data["data"]["link"]
            invoice_id = invoice_data["data"]["id"]
            return invoice_link, invoice_id
        else:
            print(f"Can't create invoice: {response.status_code}, {response.text}")
            return None, None
    except Exception as e:
        logging.error(f"Error in create_xrocket_invoice function: {e}\n{traceback.format_exc()}")


def check_payment(invoice_id):
    try:
        headers = {
            'accept': 'application/json',
            'Rocket-Pay-Key': XROCKET_API_KEY,
            'Content-Type': 'application/json'
        }
        invoice_url = f"https://pay.ton-rocket.com/tg-invoices/{invoice_id}"
        response = requests.get(invoice_url, headers=headers)
        if response.status_code == 200:
            invoice_data = response.json()
            if invoice_data["data"]["activationsLeft"] == 0:
                return True
            else:
                return False
        else:
            print(f"Can't check invoice {response.status_code}, {response.text}")
            return False
    except Exception as e:
        logging.error(f"Error in check_payment function: {e}\n{traceback.format_exc()}")


def check_payment_loop(invoice_id, call, amount):
    try:
        start_time = time.time()
        while time.time() - start_time < 120:
            if check_payment(invoice_id):
                user_id = call.from_user.id
                if user_id not in user_data:
                    user_data[user_id] = {}  # Initialize if not present

                user_data[user_id]['balance'] = user_data.get(user_id, {}).get('balance', 0) + amount

                if amount == 5:
                    user_data[user_id]['has_active_plan'] = True
                    user_data[user_id]['has_crypto'] = True
                bot.send_message(call.message.chat.id,
                                 f"Your transaction received! {amount}$ was successfully added to your balance.")
                if 'invoicer' in user_data.get(user_id, {}): # Remove invoicer flag after payment
                    del user_data[user_id]['invoicer']

                return # Stop the loop if the payment is successful

        bot.send_message(call.message.chat.id, "Invoice was successfully deleted because you haven't paid.")
        user_id = call.from_user.id
        if 'invoicer' in user_data.get(user_id, {}):
            del user_data[user_id]['invoicer']
    except Exception as e:
        logging.error(f"Error in check_payment_loop function: {e}\n{traceback.format_exc()}")


@bot.callback_query_handler(func=lambda call: call.data == "starter")
def handle_starter(call):
    user_id = call.from_user.id
    if not user_data.get(user_id, {}).get('invoicer', False): # Check for 'invoicer' flag within user_data
        try:
            bot.send_message(call.message.chat.id, "Creating Xrocket invoice...")
            invoice_url, invoice_id = create_xrocket_invoice(amount=0.5, currency="USDT")
            if invoice_url:
                bot.send_message(call.message.chat.id,
                                 f"Your invoice is ready! Your link: {invoice_url} .Link expires in 2 minutes.")
                user_data[user_id]['invoicer'] = True # Set invoicer flag when invoice is created
                payment_thread = Thread(target=check_payment_loop, args=(invoice_id, call, 0.5))
                payment_thread.start()
            else:
                bot.send_message(call.message.chat.id, "Invoice creation failed.")
        except Exception as e:
            logging.error(f"Error in handle_starter function: {e}\n{traceback.format_exc()}")
    else:
        bot.send_message(call.message.chat.id, "You have already created an invoice. Please wait for it to expire.")


import os
import requests
from telebot import types


@bot.message_handler(commands=['logo'])
def handle_logo(message):
    user_id = message.from_user.id
    prompt = message.text.replace('/logo ', '')

    if user_data.get(user_id, {}).get('balance', 0) >= 0.025: # Use get to prevent KeyError
        user_data[user_id]['balance'] -= 0.025
        generate_and_send_image(message, prompt)
    else:
        bot.send_message(message.chat.id,
                         "You don't have enough balance to ask a question or generate an image. Run /plans command to view all plans.")


def generate_and_send_image(message, prompt):
    lexica_url = f"https://lexica.art/api/v1/search?q={prompt}"
    response = requests.get(lexica_url)

    if response.status_code == 200: # Check for successful response from lexica.art
        result = response.json()
        if result and 'images' in result and result['images'] and 'src' in result['images'][0]:
            image_url = result['images'][0]['src']

            try:
                image_response = requests.get(image_url, stream=True)
                image_response.raise_for_status() # Check for any download errors

                with open("generated_image.png", "wb") as f:
                    for chunk in image_response.iter_content(chunk_size=8192):
                        f.write(chunk)

                bot.send_photo(message.chat.id, open("generated_image.png", "rb"))
                os.remove("generated_image.png")  # Remove after sending

                keyboard = types.InlineKeyboardMarkup()
                button = types.InlineKeyboardButton(text="Regenerate", callback_data=f"regenerate_{prompt}")
                keyboard.add(button)
                bot.send_message(message.chat.id, f"User prompt:\n\n{prompt}", reply_markup=keyboard)

            except requests.exceptions.RequestException as e: # Handle image download issues
                bot.send_message(message.chat.id, f"Error downloading image: {e}")

        else:
            bot.send_message(message.chat.id, "Sorry, I couldn't find an image for your prompt.")
    else:
        bot.send_message(message.chat.id, f"Error: Couldn't get image from lexica.art (status code: {response.status_code})")

@bot.callback_query_handler(func=lambda call: call.data.startswith("regenerate_"))
def handle_regenerate(call):
    prompt = call.data.replace("regenerate_", "")
    bot.answer_callback_query(call.id, "Regenerating image...")
    generate_and_send_image(call.message, prompt)



@bot.callback_query_handler(func=lambda call: call.data == "crypto")
def handle_crypto(call): # Renamed to handle_crypto
    user_id = call.from_user.id
    if not user_data.get(user_id, {}).get('invoicer', False): # prevent double invoices
        try:
            bot.send_message(call.message.chat.id, "Creating Xrocket invoice...")
            invoice_url, invoice_id = create_xrocket_invoice(amount=5, currency="USDT")
            if invoice_url:
                bot.send_message(call.message.chat.id,
                                 f"Your invoice link is ready.You can pay via this link: {invoice_url} .Link expires in 2 minutes")
                user_data[user_id]['invoicer'] = True # Set the flag
                payment_thread = Thread(target=check_payment_loop, args=(invoice_id, call, 5))
                payment_thread.start()

            else:
                bot.send_message(call.message.chat.id, "Can't create invoice")
        except Exception as e:
            logging.error(f"Error in handle_crypto function: {e}\n{traceback.format_exc()}")
    else:
        bot.send_message(call.message.chat.id, "You have already created an invoice. Please wait for it to expire.")

@bot.callback_query_handler(func=lambda call: call.data == "medium")
def handle_medium(call): # Fixed duplicate function name
    user_id = call.from_user.id
    if not user_data.get(user_id, {}).get('invoicer', False):  # prevent double invoices
        try:
            bot.send_message(call.message.chat.id, "Creating Xrocket invoice...")
            invoice_url, invoice_id = create_xrocket_invoice(amount=1, currency="USDT")
            if invoice_url:
                bot.send_message(call.message.chat.id,
                                 f"Your invoice is ready! Your link: {invoice_url} .Link expires in 2 minutes")
                user_data[user_id]['invoicer'] = True  # Set the flag
                payment_thread = Thread(target=check_payment_loop, args=(invoice_id, call, 1))
                payment_thread.start()

            else:
                bot.send_message(call.message.chat.id, "Invoice creation failed.")
        except Exception as e:
            logging.error(f"Error in handle_medium function: {e}\n{traceback.format_exc()}")
    else:
        bot.send_message(call.message.chat.id, "You have already created an invoice. Please wait for it to expire.")



bot.polling(none_stop=True)
