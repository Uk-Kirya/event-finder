import os
from dotenv import load_dotenv, find_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

if not find_dotenv():
    exit("Переменные окружения не загружены, так как отсутствует файл .env")
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = os.getenv("DB_PATH")

DEFAULT_COMMANDS = (
    ("profile", "👤 Мой профиль"),
    ("search", "🔍 Найти исполнителя"),
    ("about", "🤖 О боте"),
    ("help", "ℹ️ Помощь")
)


def edit_profile_keyboard() -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для выбора раздела редактирования.
    """
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 2  # Количество кнопок в строке
    keyboard.add(
        InlineKeyboardButton("Имя", callback_data="edit_name"),
        InlineKeyboardButton("Род деятельности", callback_data="edit_category"),
        InlineKeyboardButton("Телефон", callback_data="edit_phone"),
        InlineKeyboardButton("О себе", callback_data="edit_about"),
        InlineKeyboardButton("Instagram", callback_data="edit_instagram"),
        InlineKeyboardButton("TikTok", callback_data="edit_tiktok"),
        InlineKeyboardButton("Портфолио", callback_data="edit_portfolio"),
    )
    return keyboard


def categories_keyboard() -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для выбора раздела редактирования.
    """
    categories = InlineKeyboardMarkup()
    categories.row_width = 2
    categories.add(
        InlineKeyboardButton("Музыканты", callback_data="category_1"),
        InlineKeyboardButton("Ведущие", callback_data="category_2"),
        InlineKeyboardButton("Фото-видео съемка", callback_data="category_3"),
        InlineKeyboardButton("Оформители", callback_data="category_4"),
        InlineKeyboardButton("Танцоры и шоу балет", callback_data="category_5"),
        InlineKeyboardButton("Ди-джеи и таперы", callback_data="category_6"),
        InlineKeyboardButton("Аниматоры", callback_data="category_7"),
        InlineKeyboardButton("Шоу-программа", callback_data="category_8"),
        InlineKeyboardButton("Прокат, аренда", callback_data="category_9"),
        InlineKeyboardButton("Банкетные залы, рестораны", callback_data="category_10"),
    )
    return categories


def subcategories_category_1() -> InlineKeyboardMarkup:
    musicians = InlineKeyboardMarkup()
    musicians.row_width = 2
    musicians.add(
        InlineKeyboardButton('Вокалисты', callback_data='musicians_1'),
        InlineKeyboardButton('Вокалистки', callback_data='musicians_2'),
        InlineKeyboardButton('Дуэт', callback_data='musicians_3'),
        InlineKeyboardButton('Лайв-бэнд', callback_data='musicians_4'),
        InlineKeyboardButton('Инструментальные ансамбли', callback_data='musicians_5'),
    )
    return musicians


def subcategories_category_3() -> InlineKeyboardMarkup:
    media = InlineKeyboardMarkup()
    media.row_width = 2
    media.add(
        InlineKeyboardButton('Видеография', callback_data='media_1'),
        InlineKeyboardButton('Фотография', callback_data='media_2'),
        InlineKeyboardButton('Мобилография', callback_data='media_3'),
    )
    return media


def choice_category_keyboard() -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для выбора раздела редактирования.
    """
    choice_category = InlineKeyboardMarkup()
    choice_category.row_width = 2
    choice_category.add(
        InlineKeyboardButton('Вокалисты', callback_data='choice_category_1'),
        InlineKeyboardButton('Вокалистки', callback_data='choice_category_2'),
        InlineKeyboardButton('Дуэт', callback_data='choice_category_3'),
        InlineKeyboardButton('Лайв-бэнд', callback_data='choice_category_4'),
        InlineKeyboardButton('Инструментальные ансамбли', callback_data='choice_category_5'),
        InlineKeyboardButton("Ведущие", callback_data="choice_category_6"),
        InlineKeyboardButton('Видеография', callback_data='choice_category_7'),
        InlineKeyboardButton('Фотография', callback_data='choice_category_8'),
        InlineKeyboardButton('Мобилография', callback_data='choice_category_9'),
        InlineKeyboardButton("Оформители", callback_data="choice_category_10"),
        InlineKeyboardButton("Танцоры и шоу балет", callback_data="choice_category_11"),
        InlineKeyboardButton("Ди-джеи и таперы", callback_data="choice_category_12"),
        InlineKeyboardButton("Аниматоры", callback_data="choice_category_13"),
        InlineKeyboardButton("Шоу-программа", callback_data="choice_category_14"),
        InlineKeyboardButton("Прокат, аренда", callback_data="choice_category_15"),
        InlineKeyboardButton("Банкетные залы, рестораны", callback_data="choice_category_16"),
    )
    return choice_category


def button_back_to_categories() -> InlineKeyboardMarkup:
    back_to_categories = InlineKeyboardMarkup()
    back_to_categories.add(
        InlineKeyboardButton('⬅️ Назад к категориям', callback_data="back_to_categories")
    )
    return back_to_categories
