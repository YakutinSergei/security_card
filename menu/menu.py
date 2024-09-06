from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from datetime import datetime


async def create_inline_kb() -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []

    buttons.append(InlineKeyboardButton(
        text='Отмена',
        callback_data='Cancel'))
    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*buttons, width=1)

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()


'''Клавиатура на отправку чека'''


async def price_kb() -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []

    buttons.append(InlineKeyboardButton(
        text='Купить',
        callback_data='price'))
    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*buttons, width=1)

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()


'''Выбор языка'''


async def language_selection_kb() -> InlineKeyboardMarkup:
    language_list = ['Русский', 'English', 'Uzbek', 'Kazakh', 'Sri Lankan', 'Vietnamese']
    # Инициализируем билдер
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    # Инициализируем список для кнопо
    buttons: list[InlineKeyboardButton] = []

    for i in language_list:
        buttons.append(InlineKeyboardButton(
            text=i,
            callback_data=f'ch_lang_{i}'),
        )

    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*buttons, width=2)

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()


'''Клавиатура с кнопкой отправить чек'''


async def kb_price(text_btn):
    # Инициализируем билдер
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    # Инициализируем список для кнопоr
    buttons: list[InlineKeyboardButton] = []

    buttons.append(InlineKeyboardButton(
        text=text_btn,
        callback_data=f'output_check'),
    )

    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*buttons, width=1)

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()


'''Клавиатура админу'''
async def output_admin(id_user):
    # Инициализируем билдер
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    # Инициализируем список для кнопоr
    buttons: list[InlineKeyboardButton] = []

    buttons.append(InlineKeyboardButton(
        text='Подтвердить',
        callback_data=f'chPhoto_{id_user}'),

    )
    buttons.append(InlineKeyboardButton(
        text='Отклонить',
        callback_data=f'chPhoto_{id_user}_no'),

    )

    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*buttons, width=2)

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()