import redis
import re

from environs import Env
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Filters, Updater, CallbackQueryHandler, CommandHandler, MessageHandler
from functools import partial

from elasticpath import get_access_token, get_products, get_product, get_file,\
      add_product_to_cart, get_items_in_cart, get_total_amount_for_cart,\
      delete_cart_item, create_customer


_database = None


def show_main_menu(db, client_id, client_secret):
    access_token = get_access_token(db, client_id, client_secret)
    products = get_products(access_token)
    keyboard = [[InlineKeyboardButton(product["name"], callback_data=product["id"])] for product in products]
    keyboard.append([InlineKeyboardButton("Cart", callback_data="cart")])
    return InlineKeyboardMarkup(keyboard)


def show_cart(access_token, chat_id):
    products_in_cart = get_items_in_cart(access_token, chat_id)
    total_value = get_total_amount_for_cart(access_token, chat_id)
    products_in_cart_texts = ["\n".join([
            product["name"],
            product["description"],
            f"{product['price_per_kg']} per kg",
            f"{product['quantity']}kg for {product['value']}"]) for product in products_in_cart]
    products_in_cart_texts.append(f"Total: {total_value}")
    cart_text = "\n\n".join(products_in_cart_texts)
    buttons = [[InlineKeyboardButton(f"Remove {product['name']}", callback_data=f"{product['id']}")] for product in products_in_cart]
    buttons.append([InlineKeyboardButton("Pay", callback_data="pay")])
    buttons.append([InlineKeyboardButton("Back to menu", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(buttons)
    return cart_text, reply_markup
    

def start(update, context, db, client_id, client_secret):    
    reply_markup = show_main_menu(db, client_id, client_secret)
    update.message.reply_text("Please choose:", reply_markup=reply_markup)
    
    return "HANDLE_MENU"


def handle_menu(update, context, db, client_id, client_secret):
    query = update.callback_query
    access_token = get_access_token(db, client_id, client_secret)
    chat_id = query.message.chat_id
    menu_msg_id = query.message.message_id
    if query.data == "cart":
        cart_text, reply_markup = show_cart(access_token, chat_id)
        context.bot.send_message(text=cart_text, chat_id=chat_id, reply_markup=reply_markup)
        context.bot.delete_message(message_id=menu_msg_id, chat_id=chat_id)
        return "HANDLE_CART"
    else:
        product = get_product(access_token, query.data.strip())
        image_url = get_file(access_token, product["image"])
        query.answer()
        
        buttons = [[InlineKeyboardButton("1 kg", callback_data=f"1 {product['id']}"), InlineKeyboardButton("5 kg", callback_data=f"5 {product['id']}")],
                [InlineKeyboardButton("Back", callback_data="back")]]
        keyboard_markup = InlineKeyboardMarkup(buttons)
        context.bot.send_photo(chat_id=chat_id,
                                photo=image_url,
                                caption=f"{product['name']}\n{product['description']}",
                                reply_markup=keyboard_markup)
        context.bot.delete_message(message_id = menu_msg_id, chat_id = chat_id)
        return "HANDLE_DESCRIPTION"


def handle_description(update, context, db, client_id, client_secret):
    query = update.callback_query
    chat_id = query.message.chat_id
    if query.data == "back":
        menu_msg_id = query.message.message_id
        reply_markup = show_main_menu(db, client_id, client_secret)
        context.bot.send_message(text="Please choose", chat_id=query.message.chat_id, reply_markup=reply_markup)
        context.bot.delete_message(message_id = menu_msg_id, chat_id = chat_id)
        return "HANDLE_MENU"
    else:
        quantity, product_id = query.data.split()
        access_token = get_access_token(db, client_id, client_secret)
        add_product_to_cart(access_token, chat_id, product_id, int(quantity))
        return "HANDLE_DESCRIPTION"


def handle_cart(update, context, db, client_id, client_secret):
    query = update.callback_query
    chat_id = query.message.chat_id
    old_msg_id = query.message.message_id
    
    if query.data == "back":
        reply_markup = show_main_menu(db, client_id, client_secret)
        context.bot.send_message(text="Please choose", chat_id=chat_id, reply_markup=reply_markup)
        context.bot.delete_message(message_id = old_msg_id, chat_id = chat_id)
        return "HANDLE_MENU"
    if query.data == "pay":
        context.bot.send_message(text="Please, send us email to contact you", chat_id=chat_id)
        context.bot.delete_message(message_id = old_msg_id, chat_id = chat_id)
        return "WAITING_EMAIL"
    else:
        item_in_cart_id = query.data
        access_token = get_access_token(db, client_id, client_secret)
        delete_cart_item(access_token, chat_id, item_in_cart_id)
        cart_text, reply_markup = show_cart(access_token, chat_id)
        context.bot.send_message(chat_id=chat_id, text=cart_text, reply_markup=reply_markup)
        context.bot.delete_message(message_id = old_msg_id, chat_id = chat_id)
        return "HANDLE_CART"


def waiting_email(update, context, db, client_id, client_secret):
    users_message = update.message.text
    chat_id = update.message.chat_id

    #regex was taken from https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/
    regex_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.fullmatch(regex_email, users_message):
        context.bot.send_message(chat_id=chat_id, text=f"Your email is {users_message}")
        access_token = get_access_token(db, client_id, client_secret)
        create_customer(access_token, chat_id, users_message)
        reply_markup = show_main_menu(db, client_id, client_secret)
        context.bot.send_message(text="Please choose", chat_id=chat_id, reply_markup=reply_markup)
        return "HANDLE_MENU"
    
    context.bot.send_message(chat_id=chat_id, text="Invalid email, try again")
    return "WAITING_EMAIL"


def handle_users_reply(update, context, db, client_id, client_secret):
    
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id).decode("utf-8")
    
    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu,
        'HANDLE_DESCRIPTION': handle_description,
        'HANDLE_CART': handle_cart,
        'WAITING_EMAIL': waiting_email
    }
    state_handler = states_functions[user_state]

    try:
        next_state = state_handler(update, context, db, client_id, client_secret)
        db.set(chat_id, next_state)
    except Exception as err:
        print(err)

def get_database_connection():
    global _database
    if _database is None:
        database_password = env("DATABASE_PASSWORD")
        database_host = env("DATABASE_HOST")
        database_port = env("DATABASE_PORT")
        _database = redis.Redis(host=database_host, port=database_port, password=database_password)
    return _database


if __name__ == '__main__':

    env = Env()
    env.read_env()
    
    token = env("TELEGRAM_TOKEN")
    client_id = env("CLIENT_ID")
    client_secret = env("CLIENT_SECRET")
    updater = Updater(token, use_context=True)
    db = get_database_connection()
    handle_users_reply_with_extra_arguments = partial(handle_users_reply, db=db, client_id=client_id, client_secret=client_secret)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply_with_extra_arguments))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply_with_extra_arguments))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply_with_extra_arguments))
    updater.start_polling()