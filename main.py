import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


API_TOKEN = '7319633029:AAE0FoLkdaPk-B3wH60zKxtQW4w9x0Xx6n8'  # Вставте ваш API токен
bot = telebot.TeleBot(API_TOKEN)

# Адміністратори (ID)
admin_ids = [745741800]  # Замініть на ID ваших адміністраторів

# Каталог товарів
products = [
    {"name": "Хліб", "description": "Свіжий білий хліб, 500 г", "price": "25 грн"},
    {"name": "Молоко", "description": "Молоко 2,5% жирності, 1 л", "price": "30 грн"},
    {"name": "Яйця", "description": "Яйця курячі, 10 шт", "price": "45 грн"},
    {"name": "Цукор", "description": "Цукор білий, 1 кг", "price": "22 грн"},
    {"name": "Макарони", "description": "Макарони з твердих сортів пшениці, 400 г", "price": "35 грн"},
    {"name": "Кава", "description": "Кава мелена, 250 г", "price": "80 грн"},
    {"name": "Чай", "description": "Чай чорний, 100 г", "price": "60 грн"},
    {"name": "Олія", "description": "Олія соняшникова, 1 л", "price": "50 грн"},
    {"name": "Сир", "description": "Сир твердий, 250 г", "price": "85 грн"},
    {"name": "Сіль", "description": "Сіль кухонна, 1 кг", "price": "15 грн"}
]

# Зберігання замовлень та стану користувачів
orders = {}
user_feedback = {}
admin_add_item_state = {}


# Команда /start з усіма кнопками на панелі
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('/catalog', '/info', '/feedback', '/hello')
    markup.add('Оформити замовлення')

    # Додаємо кнопки для адміністраторів, якщо це адміністратор
    if message.from_user.id in admin_ids:
        markup.add('/add_item', '/remove_item')

    bot.send_message(message.chat.id, "Ласкаво просимо! Оберіть команду з меню:", reply_markup=markup)


# Обробка введення користувачем відгуку
@bot.message_handler(func=lambda message: user_feedback.get(message.from_user.id) == 'waiting_feedback')
def handle_feedback(message):
    feedback = message.text
    user_feedback[message.from_user.id] = None  # Очищаємо стан очікування відгуку

    # Надсилання відгуку адміністраторам
    for admin_id in admin_ids:
        bot.send_message(admin_id,
                         f"Новий відгук від {message.from_user.first_name} (ID: {message.from_user.id}):\n{feedback}")

    bot.reply_to(message, "Дякуємо за ваш відгук! Ми його передали адміністраторам.")


# Валідація введеної ціни
def is_valid_price(price):
    try:
        price_value = int(price)
        return price_value > 0  # Ціна повинна бути позитивним числом
    except ValueError:
        return False


# Обробка додавання товару адміністратором
@bot.message_handler(func=lambda message: message.from_user.id in admin_add_item_state)
def handle_add_item(message):
    user_id = message.from_user.id
    state = admin_add_item_state.get(user_id)

    if state['step'] == 'name':
        state['name'] = message.text
        bot.send_message(message.chat.id, "Введіть опис товару:")
        state['step'] = 'description'

    elif state['step'] == 'description':
        state['description'] = message.text
        bot.send_message(message.chat.id, "Введіть ціну товару (в грн):")
        state['step'] = 'price'

    elif state['step'] == 'price':
        price = message.text
        if is_valid_price(price):
            products.append({
                'name': state['name'],
                'description': state['description'],
                'price': f"{price} грн"
            })
            bot.send_message(message.chat.id, f"Товар '{state['name']}' успішно додано до каталогу!")
            del admin_add_item_state[user_id]  # Очищаємо стан
        else:
            bot.send_message(message.chat.id, "Невірний формат ціни. Будь ласка, введіть правильну ціну.")

    elif state['step'] == 'remove':
        product_name = message.text
        product_to_remove = next((p for p in products if p['name'] == product_name), None)
        if product_to_remove:
            products.remove(product_to_remove)
            bot.send_message(message.chat.id, f"Товар '{product_name}' успішно видалено з каталогу.")
        else:
            bot.send_message(message.chat.id, f"Товар '{product_name}' не знайдено.")
        del admin_add_item_state[user_id]


# Команда /catalog для перегляду товарів
@bot.message_handler(commands=['catalog'])
def send_catalog(message):
    markup = InlineKeyboardMarkup()
    for product in products:
        markup.add(
            InlineKeyboardButton(f"{product['name']} - {product['price']}", callback_data=f"view_{product['name']}"))
    bot.send_message(message.chat.id, "Оберіть товар для перегляду:", reply_markup=markup)


# Обробка інлайн-кнопок для перегляду товару та замовлення
@bot.callback_query_handler(func=lambda call: call.data.startswith('view_') or call.data.startswith('order_'))
def callback_query(call):
    user_id = call.from_user.id

    # Перегляд товару
    if call.data.startswith('view_'):
        product_name = call.data.split('_')[1]
        selected_product = next((p for p in products if p['name'] == product_name), None)

        if selected_product:
            description = f"Назва: {selected_product['name']}\nОпис: {selected_product['description']}\nЦіна: {selected_product['price']}"
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("Замовити", callback_data=f"order_{selected_product['name']}"))
            bot.send_message(call.message.chat.id, description, reply_markup=markup)


# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)
