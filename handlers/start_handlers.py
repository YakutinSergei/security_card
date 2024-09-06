import os
import re

from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import Command, StateFilter, CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InputFile, FSInputFile
from humanfriendly.terminal import message
from rembg import remove
from PIL import Image, ImageDraw, ImageFont

from create_bot import bot
from database import init_db, add_user, user_exists, get_user, update_tokens, add_tokens, get_admins, user_exists_2, \
    up_lang
from lexicon_list import text
from menu.menu import create_inline_kb, price_kb, language_selection_kb

router: Router = Router()


# Определение состояний
class Form(StatesGroup):
    korean_name = State()
    birth_date = State()
    photo = State()
    price = State()


# Стартовая команда
@router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    tg_id = message.from_user.id

    # Проверка пользователя в базе данных
    if not user_exists(tg_id):
        add_user(tg_id)

    await message.answer(text='Привет, это бот который делает карту техники безопасности (анджон када)',
                         reply_markup=await language_selection_kb())


'''Кнопка выбора языка'''


@router.callback_query(F.data.startswith('ch_lang_'))
async def choice_language(callback_query: types.CallbackQuery, state: FSMContext):
    language = callback_query.data.split('_')[-1]
    up_language_user = up_lang(language, callback_query.from_user.id)
    await bot.edit_message_text(
        chat_id=callback_query.message.from_user.id,

        text=text[f'{language}']['create_command'])
    await callback_query.answer()


'''Обработка команды создания карты'''


@router.message(F.text == '/create_card')
async def create_card(message: types.Message, state: FSMContext):
    user = get_user(message.from_user.id)
    await message.answer(text=text[f'{user[4]}']['name'], reply_markup=await create_inline_kb())
    await state.set_state(Form.korean_name)


# Обработка команды отмены
@router.callback_query(F.data == 'Cancel')
async def cancel_process(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await bot.delete_message(chat_id=callback_query.message.chat.id,
                             message_id=callback_query.message.message_id)


# Обработка команды покупки
@router.callback_query(F.data == 'price')
async def price_process(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.price)
    await callback_query.message.answer(
        "Для покупки карты безопасности сделайте перевод в размере 5000 рублей на номер карты 0000 0000 0000 0000 0000 и отправьте чек.\n"
        "Или нажмите кнопку отмена",
        reply_markup=await create_inline_kb())
    await callback_query.answer()


@router.message(StateFilter(Form.price))
async def process_payment_proof(message: types.Message, state: FSMContext):
    tg_id = message.from_user.id

    # Получение идентификатора администратора (замените на реальный ID)

    admins = get_admins()
    user = get_user(tg_id)

    if message.photo:
        # Если отправлено фото
        file = message.photo[-1]
        print(admins[0])

        await bot.send_photo(chat_id=admins[0][0],
                             photo=message.photo[0].file_id,
                             caption=f"Пользователь {user[0]} отправил чек для подтверждения оплаты.")
        await message.answer("Ваш чек отправлен администратору на проверку.", reply_markup=ReplyKeyboardRemove())
    elif message.document:
        # Если отправлен документ
        file = message.document
        file_path = f"img/{file.file_id}.{file.file_name.split('.')[-1]}"
        await bot.download_file_by_id(file.file_id, file_path)
        file_to_send = FSInputFile(file_path)
    else:
        await message.answer("Пожалуйста, отправьте чек в виде фотографии или документа.")
        return

    await state.clear()


# Запрос имени на корейском
@router.message(StateFilter(Form.korean_name))
async def get_korean_name(message: types.Message, state: FSMContext):
    await state.update_data(korean_name=message.text)
    user = get_user(message.from_user.id)
    await message.answer(text=text[f'{user[4]}']['dateOfBirth'],
                         reply_markup=await create_inline_kb())
    await state.set_state(Form.birth_date)


# Запрос даты рождения
@router.message(StateFilter(Form.birth_date))
async def get_birth_date(message: types.Message, state: FSMContext):
    # Проверка формата даты

    await state.update_data(birth_date=message.text)
    user = get_user(message.from_user.id)
    result_path = f"img/photo.jpg"
    await message.answer_photo(photo=FSInputFile(result_path),
                               caption=text[f'{user[4]}']['photo'],
                               reply_markup=await create_inline_kb())
    await state.set_state(Form.photo)


# Запрос фотографии
@router.message(StateFilter(Form.photo))
async def get_photo(message: types.Message, state: FSMContext):
    if message.photo:
        tg_id = message.from_user.id
        user = get_user(message.from_user.id)

        # Скачивание фото
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        photo_path = f"img/{photo.file_id}.jpg"
        # Скачивание файла
        await bot.download_file(file.file_path, photo_path)

        # Удаление фона
        input_image = Image.open(photo_path)
        output_image = remove(input_image)

        # Конвертируем изображение в RGB, если оно не в этом формате
        # if output_image.mode != 'RGB':
        #     output_image = output_image.convert('RGB')
        #
        output_image_path = f"img/removed_{photo.file_id}.png"
        output_image.save(output_image_path)

        # Получение данных
        user_data = await state.get_data()
        korean_name = user_data['korean_name']
        birth_date = user_data['birth_date']

        # Создание итогового изображения
        template = Image.open("img/1.jpg")  # Загрузите ваш шаблон
        draw = ImageDraw.Draw(template)

        # Позиции для текста и фото (настройте под ваш шаблон)
        name_position = (630, 192)
        date_position = (630, 240)
        photo_position = (150, 190)
        photo_size = (250, 255)
        sample_position = (100, 100)
        sample_size = (700, 500)
        watermark_position = (315, 200)
        watermark_size = (195, 195)

        # Вставка текста
        font_name = ImageFont.truetype("NotoSansCJK-Regular.ttc", 18)  # Замените шрифт при необходимости
        font = ImageFont.truetype("arial.ttf", 20)  # Замените шрифт при необходимости
        draw.text(name_position, korean_name, font=font_name, fill="black")
        draw.text(date_position, birth_date, font=font, fill="black")

        # Вставка фотографии
        user_photo = Image.open(output_image_path)
        user_photo = user_photo.resize(photo_size)
        # Если user_photo имеет альфа-канал, извлекаем его для использования в качестве маски
        if user_photo.mode == 'RGBA':
            r, g, b, mask = user_photo.split()
            template.paste(user_photo, photo_position, mask)
        else:
            template.paste(user_photo, photo_position)

        # Вставка водяного знака
        user_photo = Image.open("img/2.png")
        user_photo = user_photo.resize(watermark_size)
        template.paste(user_photo, watermark_position, user_photo)

        # Сохранение и отправка результата
        result_path = f"img/{user[0]}.jpg"
        template.save(result_path)

        # Вставка водяного знака образец
        user_photo = Image.open("img/sample.png")
        user_photo = user_photo.resize(sample_size)
        template.paste(user_photo, sample_position, user_photo)

        # Сохранение и отправка результата
        result_path_sample = f"img/sample_{user[0]}.jpg"
        template.save(result_path_sample)
        await message.reply_photo(photo=FSInputFile(result_path_sample),
                                  caption=text[f'{user[4]}']['price'],
                                  reply_markup=await kb_price())

    else:

        await message.answer("Отправьте фото для генерации картинки.")
        return

    # Завершение состояния
    await state.clear()


# Команда добавления жетонов (доступна только администраторам)
@router.message(F.text.startswith("add"))
async def add_tokens_command(message: types.Message):
    tg_id = message.from_user.id
    user = get_user(tg_id)

    if user[2] != "admin":
        await message.answer("У вас нет прав для выполнения этой команды.")
        return

    args = message.text.split()
    if len(args) != 3:
        await message.answer("Неверный формат команды. Используйте: add <id> <количество_жетонов>")
        return

    target_id = int(user[0])
    tokens_to_add = int(args[2])

    user_add = user_exists_2(args[1])

    if not user_exists_2(target_id):
        await message.answer("Пользователь с таким id не найден.")
        return

    add_tokens(args[1], tokens_to_add)
    await message.answer(f"Пользователю {args[1]} добавлено {tokens_to_add} жетонов.")
    await bot.send_message(chat_id=user_add[1], text=f'Добавлено {tokens_to_add} жетона(ов)')
