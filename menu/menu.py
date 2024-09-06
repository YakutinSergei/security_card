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