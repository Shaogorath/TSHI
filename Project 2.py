import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, \
    CallbackQuery
from aiogram.filters import Command

API_TOKEN = '7781388277:AAEMz24tOuEi7-KV8HjyHrkAOh9B_F_ejlk'  # Вставте свій API-токен

# Ініціалізація бота та диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Адміністратори (ID)
admin_ids = [5161187677, 745741800]  # Замініть на ID ваших адміністраторів

# Каталог товарів
products = [
    {"name": "Хліб", "description": "Свіжий білий хліб, 500 г", "price": "25 грн"},
    {"name": "Молоко", "description": "Молоко 2,5% жирності, 1 л", "price": "30 грн"},
    {"name": "Яйця", "description": "Яйця курячі, 10 шт", "price": "45 грн"},
    {"name": "Цукор", "description": "Цукор білий, 1 кг", "price": "22 грн"},
    {"name": "Макарони", "description": "Макарони з твердих сортів пшениці, 400 г", "price": "35 грн"},
    {"name": "Кава", "description": "Кава мелена, 250 г", "price": "80 грн"},
    {"name": "Чай", "description": "Чай чорний, 100 г", "price": "60 грн"},
    {"name": "Олія соняшникова", "description": "Олія соняшникова, 1 л", "price": "50 грн"},
    {"name": "Сир твердий", "description": "Сир твердий, 250 г", "price": "85 грн"},
    {"name": "Сіль кухонна", "description": "Сіль кухонна, 1 кг", "price": "15 грн"},
    {"name": "М'ясо куряче", "description": "М'ясо куряче, 1 кг", "price": "150 грн"},
    {"name": "Гречка", "description": "Гречка, 1 кг", "price": "30 грн"},
    {"name": "Помідори", "description": "Свіжі помідори, 1 кг", "price": "45 грн"},
    {"name": "Огірки", "description": "Свіжі огірки, 1 кг", "price": "35 грн"},
    {"name": "Картофель", "description": "Картофель, 2 кг", "price": "40 грн"},
    {"name": "Яблука", "description": "Яблука, 1 кг", "price": "30 грн"},
    {"name": "Банани", "description": "Банани, 1 кг", "price": "50 грн"},
    {"name": "Апельсини", "description": "Апельсини, 1 кг", "price": "60 грн"},
    {"name": "Вода мінеральна", "description": "Вода мінеральна, 1,5 л", "price": "18 грн"},
    {"name": "Кока-Кола", "description": "Кока-Кола, 1 л", "price": "35 грн"},
    {"name": "Сік апельсиновий", "description": "Сік апельсиновий, 1 л", "price": "25 грн"},
    {"name": "Пиво", "description": "Пиво світле, 0,5 л", "price": "30 грн"}
    # Інші товари
]

# Зберігання замовлень та стану користувачів
orders = {}
user_feedback = {}
admin_add_item_state = {}


# Команда /start
@dp.message(Command("start"))
async def send_welcome(message: Message):
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='/catalog'), KeyboardButton(text='/info')],
            [KeyboardButton(text='/feedback'), KeyboardButton(text='/hello')],
            [KeyboardButton(text='Оформити замовлення')]
        ],
        resize_keyboard=True
    )

    # Додаємо кнопки для адміністраторів, якщо це адміністратор
    if message.from_user.id in admin_ids:
        markup.add(KeyboardButton(text='/add_item'), KeyboardButton(text='/remove_item'))

    await message.answer("Ласкаво просимо! Оберіть команду з меню:", reply_markup=markup)


# Команда /feedback для отримання відгуку
@dp.message(Command("feedback"))
async def request_feedback(message: Message):
    user_feedback[message.from_user.id] = 'waiting_feedback'
    await message.answer("Будь ласка, залиште ваш відгук:")


# Обробка введення користувачем відгуку
@dp.message(lambda message: user_feedback.get(message.from_user.id) == 'waiting_feedback')
async def handle_feedback(message: Message):
    feedback = message.text
    user_feedback[message.from_user.id] = None  # Очищаємо стан

    # Надсилання відгуку адміністраторам
    for admin_id in admin_ids:
        await bot.send_message(admin_id,
                               f"Новий відгук від {message.from_user.first_name} (ID: {message.from_user.id}):\n{feedback}")

    await message.answer("Дякуємо за ваш відгук! Ми його передали адміністраторам.")


# Команда /hello для привітання
@dp.message(Command("hello"))
async def say_hello(message: Message):
    await message.answer(f"Привіт, {message.from_user.first_name}! Раді вас бачити.")


# Валідація введеної ціни
def is_valid_price(price):
    try:
        price_value = int(price)
        return price_value > 0  # Ціна повинна бути позитивним числом
    except ValueError:
        return False


# Команда для адміністраторів: додати товар
@dp.message(Command("add_item"))
async def add_item(message: Message):
    if message.from_user.id in admin_ids:
        admin_add_item_state[message.from_user.id] = {'step': 'name'}
        await message.answer("Введіть назву товару:")
    else:
        await message.answer("У вас немає прав для доступу до цієї функції.")


# Команда для адміністраторів: видалити товар
@dp.message(Command("remove_item"))
async def remove_item(message: Message):
    if message.from_user.id in admin_ids:
        admin_add_item_state[message.from_user.id] = {'step': 'remove'}
        await message.answer("Введіть назву товару, який хочете видалити:")
    else:
        await message.answer("У вас немає прав для доступу до цієї функції.")


# Обробка додавання товару адміністратором
@dp.message(lambda message: message.from_user.id in admin_add_item_state)
async def handle_add_item(message: Message):
    user_id = message.from_user.id
    state = admin_add_item_state.get(user_id)

    if state['step'] == 'name':
        state['name'] = message.text
        state['step'] = 'description'
        await message.answer("Введіть опис товару:")

    elif state['step'] == 'description':
        state['description'] = message.text
        state['step'] = 'price'
        await message.answer("Введіть ціну товару (в грн):")

    elif state['step'] == 'price':
        price = message.text
        if is_valid_price(price):
            products.append({
                'name': state['name'],
                'description': state['description'],
                'price': f"{price} грн"
            })
            await message.answer(f"Товар '{state['name']}' успішно додано до каталогу!")
            del admin_add_item_state[user_id]  # Очищаємо стан
        else:
            await message.answer("Невірний формат ціни. Будь ласка, введіть правильну ціну.")

    elif state['step'] == 'remove':
        product_name = message.text
        product_to_remove = next((p for p in products if p['name'] == product_name), None)
        if product_to_remove:
            products.remove(product_to_remove)
            await message.answer(f"Товар '{product_name}' успішно видалено з каталогу.")
        else:
            await message.answer(f"Товар '{product_name}' не знайдено.")
        del admin_add_item_state[user_id]


# Команда /catalog для перегляду товарів
@dp.message(Command("catalog"))
async def send_catalog(message: Message):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{product['name']} - {product['price']}", callback_data=f"view_{product['name']}")]
        for product in products
    ])
    await message.answer("Оберіть товар для перегляду:", reply_markup=markup)


# Обробка інлайн-кнопок для перегляду товару та замовлення
@dp.callback_query(lambda call: call.data.startswith('view_') or call.data.startswith('order_'))
async def callback_query(call: CallbackQuery):
    user_id = call.from_user.id

    # Перегляд товару
    if call.data.startswith('view_'):
        product_name = call.data.split('_')[1]
        selected_product = next((p for p in products if p['name'] == product_name), None)

        if selected_product:
            description = f"Назва: {selected_product['name']}\nОпис: {selected_product['description']}\nЦіна: {selected_product['price']}"
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Замовити", callback_data=f"order_{selected_product['name']}")]
            ])
            await call.message.answer(description, reply_markup=markup)

    # Замовлення товару
    elif call.data.startswith('order_'):
        product_name = call.data.split('_')[1]
        selected_product = next((p for p in products if p['name'] == product_name), None)
        if selected_product:
            if user_id not in orders:
                orders[user_id] = []
            orders[user_id].append(selected_product)
            await call.message.answer(f"Додано до замовлення: {selected_product['name']} ({selected_product['price']})")


# Оформлення замовлення
@dp.message(lambda message: message.text == 'Оформити замовлення')
async def order_button(message: Message):
    user_id = message.from_user.id

    if user_id in orders and orders[user_id]:
        total_price = 0
        order_details = "Ваше замовлення:\n"
        for product in orders[user_id]:
            order_details += f"- {product['name']} ({product['price']})\n"
            total_price += int(product['price'].split()[0])  # Витягаємо ціну
        order_details += f"Загальна сума: {total_price} грн"

        # Підтвердження замовлення
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Підтвердити", callback_data='confirm_order')]
        ])

        await message.answer(order_details, reply_markup=markup)
    else:
        await message.answer("Ваша корзина порожня. Будь ласка, додайте товари з каталогу.")


# Підтвердження замовлення
@dp.callback_query(lambda call: call.data == 'confirm_order')
async def confirm_order(call: CallbackQuery):
    await call.message.answer("Дякуємо за ваше замовлення! Ваше замовлення підтверджено.")


# Запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
