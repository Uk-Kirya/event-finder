import telebot
import logging
import sys
import time
from telebot.types import (
    BotCommand,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from peewee import IntegrityError
from models import User, Bio, create_models
from settings import (
    BOT_TOKEN,
    DEFAULT_COMMANDS,
    edit_profile_keyboard,
    categories_keyboard,
    button_back_to_categories,
    subcategories_category_1,
    subcategories_category_3,
    choice_category_keyboard,
)

logging.basicConfig(
    filename='bot_error.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

bot = telebot.TeleBot(BOT_TOKEN)


def get_user_profile_photo(user_id: int):
    try:
        photos = bot.get_user_profile_photos(user_id)
        if photos.photos:
            file_id = photos.photos[0][-1].file_id
            return file_id
        else:
            return None
    except:
        return None


@bot.message_handler(commands=['start'])
def start(message: Message) -> None:
    user_id: int = message.from_user.id
    username: str = message.from_user.username or f"user_{user_id}"

    try:
        User.create(
            user_id=user_id,
            username=username,
        )
        Bio.create(
            user=User.get_or_none(user_id=user_id)
        )
        bot.send_message(
            message.chat.id,
            f'Здравствуйте!\n\nЯ проводник в мире мероприятий ✨\n\nПомогу вам найти '
            'исполнителя или заказчика ✅\n\n‼️Первым делом, рекомендуем заполнить свой профиль /profile\n\nНу а если '
            'найти исполнителя нужно очень срочно, воспользуйтесь категориями ниже 👇🏻',
            reply_markup=categories_keyboard()
        )
    except IntegrityError:
        user = User.get(User.user_id == user_id)
        bio = Bio.get_or_none(Bio.user == user)
        name = bio.name if bio and bio.name else username
        bot.reply_to(message,
                     f"Здравствуй, {name}! Я снова готов помочь 🫡\n\nДля поиска исполнителя, нужно выбрать "
                     f"категорию ⬇️", reply_markup=categories_keyboard())


@bot.message_handler(commands=['profile'])
def profile(message: Message) -> None:
    user_id: int = message.from_user.id
    user: str = User.get_or_none(User.user_id == user_id)

    if user is None:
        bot.reply_to(message, "Вы еще не зарегистрированы. Пожалуйста, выполните команду /start.")
        return

    bio = Bio.get_or_none(Bio.user == user)

    name = bio.name if bio and bio.name else '—'
    category = bio.category if bio and bio.category else '—'
    phone = bio.phone if bio and bio.phone else '—'
    instagram = bio.instagram if bio and bio.instagram else '—'
    tiktok = bio.tiktok if bio and bio.tiktok else '—'
    about = bio.about if bio and bio.about else '—'

    photo_file_id = get_user_profile_photo(message.from_user.id)

    profile_text = (
        f'(фотография меняется в настройках профиля телеграмма)\n\n\n'
        f'Имя: {name}\n\n'
        f'Род деятельности: {category}\n\n'
        f'Телефон: {phone}\n\n'
        f'Instagram: {instagram}\n\n'
        f'TikTok: {tiktok}\n\n'
        f'О себе:\n\n{about}'
    )

    if photo_file_id:
        bot.send_photo(
            message.chat.id,
            photo=photo_file_id,
            caption=profile_text
        )
    else:
        try:
            with open("default_photo.jpg", 'rb') as photo:
                bot.send_photo(
                    message.chat.id,
                    photo=photo,
                    caption=profile_text
                )
        except FileNotFoundError:
            bot.send_message(message.chat.id, profile_text)

    if bio and bio.portfolio:
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(
            InlineKeyboardButton(
                '👀 Посмотреть портфолио',
                url=bio.portfolio
            )
        )
        bot.send_message(
            message.chat.id,
            'Ваше портфолио:',
            reply_markup=markup
        )

    bot.send_message(
        message.chat.id,
        'Вы можете отредактировать свой профиль 👇🏻',
        reply_markup=edit_profile_keyboard()
    )


@bot.message_handler(commands=['search'])
def search(message: Message):
    bot.send_message(
        message.chat.id,
        'Для поиска исполнителя, выберите соответствующую категорию 👇🏻',
        reply_markup=categories_keyboard()
    )


@bot.message_handler(commands=['about'])
def search(message: Message):
    bot.send_message(
        message.chat.id,
        'Короткое описание бота'
    )


@bot.message_handler(commands=['help'])
def search(message: Message):
    bot.send_message(
        message.chat.id,
        'Руководство по эксплуатации бота'
    )


@bot.callback_query_handler(func=lambda call: call.data == 'category_1')
def handle_subcategory(call: CallbackQuery):
    bot.send_message(
        call.message.chat.id,
        'Выберите категорию музыкантов 👇🏻',
        reply_markup=subcategories_category_1()
    )


@bot.callback_query_handler(func=lambda call: call.data == 'category_2')
def handle_subcategory(call: CallbackQuery):
    bot.send_message(
        call.message.chat.id,
        'Вы выбрали категорию «Ведущие»',
    )
    users_with_category = (
        Bio.select(Bio, User)
        .join(User)
        .where(Bio.category == 'Ведущие')
    )

    if users_with_category:
        for bio in users_with_category:
            message_text = (
                f"👤 {bio.name}\n"
                f"📞 {bio.phone}\n"
            )

            markup = InlineKeyboardMarkup()
            details_button = InlineKeyboardButton(
                text="Посмотреть профиль 🪪",
                callback_data=f"user_details_{bio.user.user_id}"
            )
            markup.add(details_button)

            bot.send_message(
                call.message.chat.id,
                message_text,
                reply_markup=markup
            )
    else:
        bot.send_message(
            call.message.chat.id,
            "В категории «Ведущие» пока нет пользователей."
        )

    bot.send_message(
        call.message.chat.id,
        'Показать все категории поиска',
        reply_markup=button_back_to_categories()
    )


@bot.callback_query_handler(func=lambda call: call.data == 'category_3')
def handle_subcategory(call: CallbackQuery):
    bot.send_message(
        call.message.chat.id,
        'Выберите категорию 👇🏻',
        reply_markup=subcategories_category_3()
    )


@bot.callback_query_handler(func=lambda call: call.data == 'category_4')
def handle_subcategory(call: CallbackQuery):
    bot.send_message(
        call.message.chat.id,
        'Вы выбрали категорию «Оформители»'
    )
    users_with_category = (
        Bio.select(Bio, User)
        .join(User)
        .where(Bio.category == 'Оформители')
    )

    if users_with_category:
        for bio in users_with_category:
            message_text = (
                f"👤 {bio.name}\n"
                f"📞 {bio.phone}\n"
            )

            markup = InlineKeyboardMarkup()
            details_button = InlineKeyboardButton(
                text="Посмотреть профиль 🪪",
                callback_data=f"user_details_{bio.user.user_id}"
            )
            markup.add(details_button)

            bot.send_message(
                call.message.chat.id,
                message_text,
                reply_markup=markup
            )
    else:
        bot.send_message(
            call.message.chat.id,
            "В категории «Оформители» пока нет пользователей."
        )

    bot.send_message(
        call.message.chat.id,
        'Показать все категории поиска',
        reply_markup=button_back_to_categories()
    )


@bot.callback_query_handler(func=lambda call: call.data == 'category_5')
def handle_subcategory(call: CallbackQuery):
    bot.send_message(
        call.message.chat.id,
        'Вы выбрали категорию «Танцоры и шоу балет»'
    )
    users_with_category = (
        Bio.select(Bio, User)
        .join(User)
        .where(Bio.category == 'Танцоры и шоу балет')
    )

    if users_with_category:
        for bio in users_with_category:
            message_text = (
                f"👤 {bio.name}\n"
                f"📞 {bio.phone}\n"
            )

            markup = InlineKeyboardMarkup()
            details_button = InlineKeyboardButton(
                text="Посмотреть профиль 🪪",
                callback_data=f"user_details_{bio.user.user_id}"
            )
            markup.add(details_button)

            bot.send_message(
                call.message.chat.id,
                message_text,
                reply_markup=markup
            )
    else:
        bot.send_message(
            call.message.chat.id,
            "В категории «Танцоры и шоу балет» пока нет пользователей."
        )

    bot.send_message(
        call.message.chat.id,
        'Показать все категории поиска',
        reply_markup=button_back_to_categories()
    )


@bot.callback_query_handler(func=lambda call: call.data == 'category_6')
def handle_subcategory(call: CallbackQuery):
    bot.send_message(
        call.message.chat.id,
        'Вы выбрали категорию «Ди-джеи и таперы»'
    )
    users_with_category = (
        Bio.select(Bio, User)
        .join(User)
        .where(Bio.category == 'Ди-джеи и таперы')
    )

    if users_with_category:
        for bio in users_with_category:
            message_text = (
                f"👤 {bio.name}\n"
                f"📞 {bio.phone}\n"
            )

            markup = InlineKeyboardMarkup()
            details_button = InlineKeyboardButton(
                text="Посмотреть профиль 🪪",
                callback_data=f"user_details_{bio.user.user_id}"
            )
            markup.add(details_button)

            bot.send_message(
                call.message.chat.id,
                message_text,
                reply_markup=markup
            )
    else:
        bot.send_message(
            call.message.chat.id,
            "В категории «Ди-джеи и таперы» пока нет пользователей."
        )

    bot.send_message(
        call.message.chat.id,
        'Показать все категории поиска',
        reply_markup=button_back_to_categories()
    )


@bot.callback_query_handler(func=lambda call: call.data == 'category_7')
def handle_subcategory(call: CallbackQuery):
    bot.send_message(
        call.message.chat.id,
        'Вы выбрали категорию «Аниматоры»'
    )
    users_with_category = (
        Bio.select(Bio, User)
        .join(User)
        .where(Bio.category == 'Аниматоры')
    )

    if users_with_category:
        for bio in users_with_category:
            message_text = (
                f"👤 {bio.name}\n"
                f"📞 {bio.phone}\n"
            )

            markup = InlineKeyboardMarkup()
            details_button = InlineKeyboardButton(
                text="Посмотреть профиль 🪪",
                callback_data=f"user_details_{bio.user.user_id}"
            )
            markup.add(details_button)

            bot.send_message(
                call.message.chat.id,
                message_text,
                reply_markup=markup
            )
    else:
        bot.send_message(
            call.message.chat.id,
            "В категории «Аниматоры» пока нет пользователей."
        )

    bot.send_message(
        call.message.chat.id,
        'Показать все категории поиска',
        reply_markup=button_back_to_categories()
    )


@bot.callback_query_handler(func=lambda call: call.data == 'category_8')
def handle_subcategory(call: CallbackQuery):
    bot.send_message(
        call.message.chat.id,
        'Вы выбрали категорию «Шоу-программа»'
    )
    users_with_category = (
        Bio.select(Bio, User)
        .join(User)
        .where(Bio.category == 'Шоу-программа')
    )

    if users_with_category:
        for bio in users_with_category:
            message_text = (
                f"👤 {bio.name}\n"
                f"📞 {bio.phone}\n"
            )

            markup = InlineKeyboardMarkup()
            details_button = InlineKeyboardButton(
                text="Посмотреть профиль 🪪",
                callback_data=f"user_details_{bio.user.user_id}"
            )
            markup.add(details_button)

            bot.send_message(
                call.message.chat.id,
                message_text,
                reply_markup=markup
            )
    else:
        bot.send_message(
            call.message.chat.id,
            "В категории «Шоу-программа» пока нет пользователей."
        )

    bot.send_message(
        call.message.chat.id,
        'Показать все категории поиска',
        reply_markup=button_back_to_categories()
    )


@bot.callback_query_handler(func=lambda call: call.data == 'category_9')
def handle_subcategory(call: CallbackQuery):
    bot.send_message(
        call.message.chat.id,
        'Вы выбрали категорию «Прокат, аренда»'
    )
    users_with_category = (
        Bio.select(Bio, User)
        .join(User)
        .where(Bio.category == 'Прокат, аренда')
    )

    if users_with_category:
        for bio in users_with_category:
            message_text = (
                f"👤 {bio.name}\n"
                f"📞 {bio.phone}\n"
            )

            markup = InlineKeyboardMarkup()
            details_button = InlineKeyboardButton(
                text="Посмотреть профиль 🪪",
                callback_data=f"user_details_{bio.user.user_id}"
            )
            markup.add(details_button)

            bot.send_message(
                call.message.chat.id,
                message_text,
                reply_markup=markup
            )
    else:
        bot.send_message(
            call.message.chat.id,
            "В категории «Прокат, аренда» пока нет пользователей."
        )

    bot.send_message(
        call.message.chat.id,
        'Показать все категории поиска',
        reply_markup=button_back_to_categories()
    )


@bot.callback_query_handler(func=lambda call: call.data == 'category_10')
def handle_subcategory(call: CallbackQuery):
    bot.send_message(
        call.message.chat.id,
        'Вы выбрали категорию «Банкетные залы, рестораны»'
    )
    users_with_category = (
        Bio.select(Bio, User)
        .join(User)
        .where(Bio.category == 'Банкетные залы, рестораны')
    )

    if users_with_category:
        for bio in users_with_category:
            message_text = (
                f"👤 {bio.name}\n"
                f"📞 {bio.phone}\n"
            )

            markup = InlineKeyboardMarkup()
            details_button = InlineKeyboardButton(
                text="Посмотреть профиль 🪪",
                callback_data=f"user_details_{bio.user.user_id}"
            )
            markup.add(details_button)

            bot.send_message(
                call.message.chat.id,
                message_text,
                reply_markup=markup
            )
    else:
        bot.send_message(
            call.message.chat.id,
            "В категории «Банкетные залы, рестораны» пока нет пользователей."
        )

    bot.send_message(
        call.message.chat.id,
        'Показать все категории поиска',
        reply_markup=button_back_to_categories()
    )


@bot.callback_query_handler(func=lambda call: call.data == 'musicians_1')
def handle_subcategory(call: CallbackQuery):
    bot.send_message(
        call.message.chat.id,
        'Вы выбрали категорию «Вокалисты»'
    )
    users_with_category = (
        Bio.select(Bio, User)
        .join(User)
        .where(Bio.category == 'Вокалисты')
    )

    if users_with_category:
        for bio in users_with_category:
            message_text = (
                f"👤 {bio.name}\n"
                f"📞 {bio.phone}\n"
            )

            markup = InlineKeyboardMarkup()
            details_button = InlineKeyboardButton(
                text="Посмотреть профиль 🪪",
                callback_data=f"user_details_{bio.user.user_id}"
            )
            markup.add(details_button)

            bot.send_message(
                call.message.chat.id,
                message_text,
                reply_markup=markup
            )
    else:
        bot.send_message(
            call.message.chat.id,
            "В категории «Вокалисты» пока нет пользователей."
        )

    bot.send_message(
        call.message.chat.id,
        'Показать все категории поиска',
        reply_markup=button_back_to_categories()
    )


@bot.callback_query_handler(func=lambda call: call.data == 'musicians_2')
def handle_subcategory(call: CallbackQuery):
    bot.send_message(
        call.message.chat.id,
        'Вы выбрали категорию «Вокалистки»'
    )
    users_with_category = (
        Bio.select(Bio, User)
        .join(User)
        .where(Bio.category == 'Вокалистки')
    )

    if users_with_category:
        for bio in users_with_category:
            message_text = (
                f"👤 {bio.name}\n"
                f"📞 {bio.phone}\n"
            )

            markup = InlineKeyboardMarkup()
            details_button = InlineKeyboardButton(
                text="Посмотреть профиль 🪪",
                callback_data=f"user_details_{bio.user.user_id}"
            )
            markup.add(details_button)

            bot.send_message(
                call.message.chat.id,
                message_text,
                reply_markup=markup
            )
    else:
        bot.send_message(
            call.message.chat.id,
            "В категории «Вокалистки» пока нет пользователей."
        )

    bot.send_message(
        call.message.chat.id,
        'Показать все категории поиска',
        reply_markup=button_back_to_categories()
    )


@bot.callback_query_handler(func=lambda call: call.data == 'musicians_3')
def handle_subcategory(call: CallbackQuery):
    bot.send_message(
        call.message.chat.id,
        'Вы выбрали категорию «Дуэт»'
    )
    users_with_category = (
        Bio.select(Bio, User)
        .join(User)
        .where(Bio.category == 'Дуэт')
    )

    if users_with_category:
        for bio in users_with_category:
            message_text = (
                f"👤 {bio.name}\n"
                f"📞 {bio.phone}\n"
            )

            markup = InlineKeyboardMarkup()
            details_button = InlineKeyboardButton(
                text="Посмотреть профиль 🪪",
                callback_data=f"user_details_{bio.user.user_id}"
            )
            markup.add(details_button)

            bot.send_message(
                call.message.chat.id,
                message_text,
                reply_markup=markup
            )
    else:
        bot.send_message(
            call.message.chat.id,
            "В категории «Дуэт» пока нет пользователей."
        )

    bot.send_message(
        call.message.chat.id,
        'Показать все категории поиска',
        reply_markup=button_back_to_categories()
    )


@bot.callback_query_handler(func=lambda call: call.data == 'musicians_4')
def handle_subcategory(call: CallbackQuery):
    bot.send_message(
        call.message.chat.id,
        'Вы выбрали категорию «Лайв-бэнд»'
    )

    users_with_category = (
        Bio.select(Bio, User)
        .join(User)
        .where(Bio.category == 'Лайв-бэнд')
    )

    if users_with_category:
        for bio in users_with_category:
            message_text = (
                f"👤 {bio.name}\n"
                f"📞 {bio.phone}\n"
            )

            markup = InlineKeyboardMarkup()
            details_button = InlineKeyboardButton(
                text="Посмотреть профиль 🪪",
                callback_data=f"user_details_{bio.user.user_id}"
            )
            markup.add(details_button)

            bot.send_message(
                call.message.chat.id,
                message_text,
                reply_markup=markup
            )
    else:
        bot.send_message(
            call.message.chat.id,
            "В категории «Лайв-бэнд» пока нет пользователей."
        )

    bot.send_message(
        call.message.chat.id,
        'Показать все категории поиска',
        reply_markup=button_back_to_categories()
    )


@bot.callback_query_handler(func=lambda call: call.data == 'musicians_5')
def handle_subcategory(call: CallbackQuery):
    bot.send_message(
        call.message.chat.id,
        'Вы выбрали категорию «Инструментальные ансамбли»'
    )
    users_with_category = (
        Bio.select(Bio, User)
        .join(User)
        .where(Bio.category == 'Инструментальные ансамбли')
    )

    if users_with_category:
        for bio in users_with_category:
            message_text = (
                f"👤 {bio.name}\n"
                f"📞 {bio.phone}\n"
            )

            markup = InlineKeyboardMarkup()
            details_button = InlineKeyboardButton(
                text="Посмотреть профиль 🪪",
                callback_data=f"user_details_{bio.user.user_id}"
            )
            markup.add(details_button)

            bot.send_message(
                call.message.chat.id,
                message_text,
                reply_markup=markup
            )
    else:
        bot.send_message(
            call.message.chat.id,
            "В категории «Инструментальные ансамбли» пока нет пользователей."
        )

    bot.send_message(
        call.message.chat.id,
        'Показать все категории поиска',
        reply_markup=button_back_to_categories()
    )


@bot.callback_query_handler(func=lambda call: call.data == 'media_1')
def handle_subcategory(call: CallbackQuery):
    bot.send_message(
        call.message.chat.id,
        'Вы выбрали категорию «Видеография»'
    )
    users_with_category = (
        Bio.select(Bio, User)
        .join(User)
        .where(Bio.category == 'Видеография')
    )

    if users_with_category:
        for bio in users_with_category:
            message_text = (
                f"👤 {bio.name}\n"
                f"📞 {bio.phone}\n"
            )

            markup = InlineKeyboardMarkup()
            details_button = InlineKeyboardButton(
                text="Посмотреть профиль 🪪",
                callback_data=f"user_details_{bio.user.user_id}"
            )
            markup.add(details_button)

            bot.send_message(
                call.message.chat.id,
                message_text,
                reply_markup=markup
            )
    else:
        bot.send_message(
            call.message.chat.id,
            "В категории «Видеография» пока нет пользователей."
        )

    bot.send_message(
        call.message.chat.id,
        'Показать все категории поиска',
        reply_markup=button_back_to_categories()
    )


@bot.callback_query_handler(func=lambda call: call.data == 'media_2')
def handle_subcategory(call: CallbackQuery):
    bot.send_message(
        call.message.chat.id,
        'Вы выбрали категорию «Фотография»'
    )
    users_with_category = (
        Bio.select(Bio, User)
        .join(User)
        .where(Bio.category == 'Фотография')
    )

    if users_with_category:
        for bio in users_with_category:
            message_text = (
                f"👤 {bio.name}\n"
                f"📞 {bio.phone}\n"
            )

            markup = InlineKeyboardMarkup()
            details_button = InlineKeyboardButton(
                text="Посмотреть профиль 🪪",
                callback_data=f"user_details_{bio.user.user_id}"
            )
            markup.add(details_button)

            bot.send_message(
                call.message.chat.id,
                message_text,
                reply_markup=markup
            )
    else:
        bot.send_message(
            call.message.chat.id,
            "В категории «Фотография» пока нет пользователей."
        )

    bot.send_message(
        call.message.chat.id,
        'Показать все категории поиска',
        reply_markup=button_back_to_categories()
    )


@bot.callback_query_handler(func=lambda call: call.data == 'media_3')
def handle_subcategory(call: CallbackQuery):
    bot.send_message(
        call.message.chat.id,
        'Вы выбрали категорию «Мобилография»'
    )
    users_with_category = (
        Bio.select(Bio, User)
        .join(User)
        .where(Bio.category == 'Мобилография')
    )

    if users_with_category:
        for bio in users_with_category:
            message_text = (
                f"👤 {bio.name}\n"
                f"📞 {bio.phone}\n"
            )

            markup = InlineKeyboardMarkup()
            details_button = InlineKeyboardButton(
                text="Посмотреть профиль 🪪",
                callback_data=f"user_details_{bio.user.user_id}"
            )
            markup.add(details_button)

            bot.send_message(
                call.message.chat.id,
                message_text,
                reply_markup=markup
            )
    else:
        bot.send_message(
            call.message.chat.id,
            "В категории «Мобилография» пока нет пользователей."
        )

    bot.send_message(
        call.message.chat.id,
        'Показать все категории поиска',
        reply_markup=button_back_to_categories()
    )


@bot.callback_query_handler(func=lambda call: call.data == 'back_to_categories')
def handle_subcategory(call: CallbackQuery):
    bot.send_message(
        call.message.chat.id,
        'Выберите категорию 👇🏻',
        reply_markup=categories_keyboard()
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_'))
def edit_profile_handler(call: CallbackQuery):
    if call.data == 'edit_name':
        bot.send_message(
            call.message.chat.id,
            'Введите имя 👇🏻',
        )
        bot.register_next_step_handler(call.message, input_name)
    elif call.data == 'edit_phone':
        bot.send_message(
            call.message.chat.id,
            'Введите телефон 👇🏻',
        )
        bot.register_next_step_handler(call.message, input_phone)
    elif call.data == 'edit_about':
        bot.send_message(
            call.message.chat.id,
            'Введите информацию о себе 👇🏻',
        )
        bot.register_next_step_handler(call.message, input_about)
    elif call.data == 'edit_instagram':
        bot.send_message(
            call.message.chat.id,
            'Введите свой Instagram 👇🏻',
        )
        bot.register_next_step_handler(call.message, input_instagram)
    elif call.data == 'edit_tiktok':
        bot.send_message(
            call.message.chat.id,
            'Введите свой TikTok 👇🏻',
        )
        bot.register_next_step_handler(call.message, input_tiktok)
    elif call.data == 'edit_portfolio':
        bot.send_message(
            call.message.chat.id,
            'Укажите ссылку на свое портфолио 👇🏻',
        )
        bot.register_next_step_handler(call.message, input_portfolio)
    elif call.data == 'edit_category':
        bot.send_message(
            call.message.chat.id,
            'Выберите подходящую категорию 👇🏻',
            reply_markup=choice_category_keyboard()
        )


def input_name(message):
    name = message.text
    user_id: int = message.from_user.id
    user: str = User.get_or_none(User.user_id == user_id)
    bio = Bio.get_or_none(Bio.user == user)
    try:
        bio.name = name
        bio.save()
        bot.send_message(message.chat.id, f'Ваше имя было обновлено на: {name} ✅')
        bot.send_message(
            message.chat.id,
            'Вы можете продолжить редактировать свой профиль 👇🏻',
            reply_markup=edit_profile_keyboard()
        )
        bot.send_message(
            message.chat.id,
            'Для поиска исполнителя, нажмите на /search 🔍'
        )
    except:
        bot.send_message(message.chat.id, 'Упс ... Что-то пошло не так. Попробуйте еще раз')
        return


def input_phone(message):
    phone = message.text
    user_id: int = message.from_user.id
    user: str = User.get_or_none(User.user_id == user_id)
    bio = Bio.get_or_none(Bio.user == user)
    try:
        bio.phone = phone
        bio.save()
        bot.send_message(message.chat.id, f'Ваш телефон был обновлен на: {phone} ✅')
        bot.send_message(
            message.chat.id,
            'Вы можете продолжить редактировать свой профиль 👇🏻',
            reply_markup=edit_profile_keyboard()
        )
        bot.send_message(
            message.chat.id,
            'Для поиска исполнителя, нажмите на /search 🔍'
        )
    except:
        bot.send_message(message.chat.id, 'Упс ... Что-то пошло не так. Попробуйте еще раз')
        return


def input_instagram(message):
    instagram = message.text
    user_id: int = message.from_user.id
    user: str = User.get_or_none(User.user_id == user_id)
    bio = Bio.get_or_none(Bio.user == user)
    try:
        bio.instagram = instagram
        bio.save()
        bot.send_message(message.chat.id, f'Ваш Instagram был обновлен на: {instagram} ✅')
        bot.send_message(
            message.chat.id,
            'Вы можете продолжить редактировать свой профиль 👇🏻',
            reply_markup=edit_profile_keyboard()
        )
        bot.send_message(
            message.chat.id,
            'Для поиска исполнителя, нажмите на /search 🔍'
        )
    except:
        bot.send_message(message.chat.id, 'Упс ... Что-то пошло не так. Попробуйте еще раз')
        return


def input_tiktok(message):
    tiktok = message.text
    user_id: int = message.from_user.id
    user: str = User.get_or_none(User.user_id == user_id)
    bio = Bio.get_or_none(Bio.user == user)
    try:
        bio.tiktok = tiktok
        bio.save()
        bot.send_message(message.chat.id, f'Ваш TikTok был обновлен на: {tiktok} ✅')
        bot.send_message(
            message.chat.id,
            'Вы можете продолжить редактировать свой профиль 👇🏻',
            reply_markup=edit_profile_keyboard()
        )
        bot.send_message(
            message.chat.id,
            'Для поиска исполнителя, нажмите на /search 🔍'
        )
    except:
        bot.send_message(message.chat.id, 'Упс ... Что-то пошло не так. Попробуйте еще раз')
        return


def input_about(message):
    about = message.text
    user_id: int = message.from_user.id
    user: str = User.get_or_none(User.user_id == user_id)
    bio = Bio.get_or_none(Bio.user == user)
    try:
        bio.about = about
        bio.save()
        bot.send_message(message.chat.id, f'Информация о вас обновлена на:\n\n{about}\n\n✅')
        bot.send_message(
            message.chat.id,
            'Вы можете продолжить редактировать свой профиль 👇🏻',
            reply_markup=edit_profile_keyboard()
        )
        bot.send_message(
            message.chat.id,
            'Для поиска исполнителя, нажмите на /search 🔍'
        )
    except:
        bot.send_message(message.chat.id, 'Упс ... Что-то пошло не так. Попробуйте еще раз')
        return


def input_portfolio(message):
    portfolio = message.text
    user_id: int = message.from_user.id
    user: str = User.get_or_none(User.user_id == user_id)
    bio = Bio.get_or_none(Bio.user == user)
    try:
        bio.portfolio = portfolio
        bio.save()
        bot.send_message(message.chat.id, f'Ссылка на портфолио обновлена на: {portfolio} ✅')
        bot.send_message(
            message.chat.id,
            'Вы можете продолжить редактировать свой профиль 👇🏻',
            reply_markup=edit_profile_keyboard()
        )
        bot.send_message(
            message.chat.id,
            'Для поиска исполнителя, нажмите на /search 🔍'
        )
    except:
        bot.send_message(message.chat.id, 'Упс ... Что-то пошло не так. Попробуйте еще раз')
        return


@bot.callback_query_handler(func=lambda call: call.data.startswith('choice_category_'))
def edit_profile_category_handler(call: CallbackQuery):
    user_id: int = call.from_user.id
    user: str = User.get_or_none(User.user_id == user_id)
    bio = Bio.get_or_none(Bio.user == user)
    if call.data == 'choice_category_1':
        bio.category = 'Вокалисты'
        bio.save()
        bot.send_message(
            call.message.chat.id,
            'Вы выбрали категорию: «Вокалисты» ✅',
        )
    elif call.data == 'choice_category_2':
        bio.category = 'Вокалистки'
        bio.save()
        bot.send_message(
            call.message.chat.id,
            'Вы выбрали категорию: «Вокалистки» ✅',
        )
    elif call.data == 'choice_category_3':
        bio.category = 'Дуэт'
        bio.save()
        bot.send_message(
            call.message.chat.id,
            'Вы выбрали категорию: «Дуэт» ✅',
        )
    elif call.data == 'choice_category_4':
        bio.category = 'Лайв-бэнд'
        bio.save()
        bot.send_message(
            call.message.chat.id,
            'Вы выбрали категорию: «Лайв-бэнд» ✅',
        )
    elif call.data == 'choice_category_5':
        bio.category = 'Инструментальные ансамбли'
        bio.save()
        bot.send_message(
            call.message.chat.id,
            'Вы выбрали категорию: «Инструментальные ансамбли» ✅',
        )
    elif call.data == 'choice_category_6':
        bio.category = 'Ведущие'
        bio.save()
        bot.send_message(
            call.message.chat.id,
            'Вы выбрали категорию: «Ведущие» ✅',
        )
    elif call.data == 'choice_category_7':
        bio.category = 'Видеография'
        bio.save()
        bot.send_message(
            call.message.chat.id,
            'Вы выбрали категорию: «Видеография» ✅',
        )
    elif call.data == 'choice_category_8':
        bio.category = 'Фотография'
        bio.save()
        bot.send_message(
            call.message.chat.id,
            'Вы выбрали категорию: «Фотография» ✅',
        )
    elif call.data == 'choice_category_9':
        bio.category = 'Мобилография'
        bio.save()
        bot.send_message(
            call.message.chat.id,
            'Вы выбрали категорию: «Мобилография» ✅',
        )
    elif call.data == 'choice_category_10':
        bio.category = 'Оформители'
        bio.save()
        bot.send_message(
            call.message.chat.id,
            'Вы выбрали категорию: «Оформители» ✅',
        )
    elif call.data == 'choice_category_11':
        bio.category = 'Танцоры и шоу балет'
        bio.save()
        bot.send_message(
            call.message.chat.id,
            'Вы выбрали категорию: «Танцоры и шоу балет» ✅',
        )
    elif call.data == 'choice_category_12':
        bio.category = 'Ди-джеи и таперы'
        bio.save()
        bot.send_message(
            call.message.chat.id,
            'Вы выбрали категорию: «Ди-джеи и таперы» ✅',
        )
    elif call.data == 'choice_category_13':
        bio.category = 'Аниматоры'
        bio.save()
        bot.send_message(
            call.message.chat.id,
            'Вы выбрали категорию: «Аниматоры» ✅',
        )
    elif call.data == 'choice_category_14':
        bio.category = 'Шоу-программа'
        bio.save()
        bot.send_message(
            call.message.chat.id,
            'Вы выбрали категорию: «Шоу-программа» ✅',
        )
    elif call.data == 'choice_category_15':
        bio.category = 'Прокат, аренда'
        bio.save()
        bot.send_message(
            call.message.chat.id,
            'Вы выбрали категорию: «Прокат, аренда» ✅',
        )
    elif call.data == 'choice_category_16':
        bio.category = 'Банкетные залы, рестораны'
        bio.save()
        bot.send_message(
            call.message.chat.id,
            'Вы выбрали категорию: «Банкетные залы, рестораны» ✅',
        )

    bot.send_message(
        call.message.chat.id,
        'Вы можете продолжить редактировать свой профиль 👇🏻',
        reply_markup=edit_profile_keyboard()
    )
    bot.send_message(
        call.message.chat.id,
        'Для поиска исполнителя, нажмите на /search 🔍'
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('user_details_'))
def handle_user_details(call: CallbackQuery):
    user_id = int(call.data.split('_')[2])

    bio = Bio.get_or_none(Bio.user == user_id)

    name = bio.name if bio and bio.name else '—'
    category = bio.category if bio and bio.category else '—'
    phone = bio.phone if bio and bio.phone else '—'
    instagram = bio.instagram if bio and bio.instagram else '—'
    tiktok = bio.tiktok if bio and bio.tiktok else '—'
    about = bio.about if bio and bio.about else '—'

    if bio:
        full_description = (
            f"Имя: {name}\n"
            f"Род деятельности: {category}\n"
            f"Телефон: {phone}\n"
            f"Instagram: {instagram}\n"
            f"TikTok: {tiktok}\n"
            f"О себе: {about}\n"
        )

        user_profile_photos = bot.get_user_profile_photos(user_id)
        if user_profile_photos.photos:
            photo_file_id = user_profile_photos.photos[0][0].file_id
            bot.send_photo(
                call.message.chat.id,
                photo=photo_file_id,
                caption=full_description
            )
            if bio.portfolio:
                markup = InlineKeyboardMarkup()
                markup.row_width = 1
                markup.add(
                    InlineKeyboardButton(
                        '👀 Посмотреть портфолио',
                        url=bio.portfolio
                    )
                )
                bot.send_message(
                    call.message.chat.id,
                    'Ссылка на портфолио:',
                    reply_markup=markup
                )
        else:
            bot.send_message(
                call.message.chat.id,
                full_description
            )

        markup = InlineKeyboardMarkup()

        links_back = {
            'Вокалисты': 'musicians_1',
            'Вокалистки': 'musicians_2',
            'Дуэт': 'musicians_3',
            'Лайв-бэнд': 'musicians_4',
            'Инструментальные ансамбли': 'musicians_5',
            'Ведущие': 'category_2',
            'Видеография': 'media_1',
            'Фотография': 'media_2',
            'Мобилография': 'media_3',
            'Оформители': 'category_4',
            'Танцоры и шоу балет': 'category_5',
            'Ди-джеи и таперы': 'category_6',
            'Аниматоры': 'category_7',
            'Шоу-программа': 'category_8',
            'Прокат, аренда': 'category_9',
            'Банкетные залы, рестораны': 'category_10',
        }

        back_button = InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=links_back[category]
        )
        markup.add(back_button)

        bot.send_message(
            call.message.chat.id,
            "Вернуться к списку пользователей:",
            reply_markup=markup
        )
    else:
        bot.send_message(
            call.message.chat.id,
            "Пользователь не найден."
        )


@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    bot.send_message(message.chat.id, 'Я не понимаю вашу команду. Пожалуйста, используйте доступные команды, '
                                      'например: /start или /help.')


def run_bot():
    try:
        create_models()
        bot.set_my_commands([BotCommand(*cmd) for cmd in DEFAULT_COMMANDS])
        bot.infinity_polling()
    except Exception as e:
        logging.error(f"Bot crashed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    while True:
        try:
            run_bot()
        except Exception as e:
            logging.error(f"Bot crashed and will restart: {str(e)}")
            time.sleep(5)
