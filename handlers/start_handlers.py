import os

from aiogram import  types, F, Router
from aiogram.filters import StateFilter, CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from rembg import remove
from PIL import Image, ImageDraw, ImageFont

from create_bot import bot
from database import add_user, user_exists, get_user, get_admins, up_lang, get_user_id
from lexicon_list import text
from menu.menu import create_inline_kb, language_selection_kb, kb_price, output_admin

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
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=text[f'{language}']['create_command'])
    await callback_query.answer()


'''Обработка команды создания карты'''


@router.message(F.text == '/create_card')
async def create_card(message: types.Message, state: FSMContext):
    user = get_user(message.from_user.id)
    await message.answer(text=text[f'{user[4]}']['name'], reply_markup=await create_inline_kb(text[f'{user[4]}']['cancel']))
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
    user = get_user(callback_query.message.from_user.id)

    await state.set_state(Form.price)
    await callback_query.message.answer(
        "Для покупки карты безопасности сделайте перевод в размере 5000 рублей на номер карты 0000 0000 0000 0000 0000 и отправьте чек.\n"
        "Или нажмите кнопку отмена",
        reply_markup=await create_inline_kb(text[f'{user[4]}']['cancel']))
    await callback_query.answer()





# Запрос имени на корейском
@router.message(StateFilter(Form.korean_name))
async def get_korean_name(message: types.Message, state: FSMContext):
    await state.update_data(korean_name=message.text)
    user = get_user(message.from_user.id)
    await message.answer(text=text[f'{user[4]}']['dateOfBirth'],
                         reply_markup=await create_inline_kb(text[f'{user[4]}']['cancel']))
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
                               reply_markup=await create_inline_kb(text[f'{user[4]}']['cancel']))
    await state.set_state(Form.photo)


# Запрос фотографии
@router.message(StateFilter(Form.photo))
async def get_photo(message: types.Message, state: FSMContext):
    if message.photo:
        user = get_user(message.from_user.id)

        # Скачивание фото
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        photo_path = f"img/photo_{user[1]}.jpg"
        # Скачивание файла
        await bot.download_file(file.file_path, photo_path)

        # Удаление фона
        input_image = Image.open(photo_path)
        output_image = remove(input_image)

        # Конвертируем изображение в RGB, если оно не в этом формате
        # if output_image.mode != 'RGB':
        #     output_image = output_image.convert('RGB')
        #
        output_image_path = f"img/removed_{user[1]}.png"
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
        result_path = f"img/{message.from_user.id}.jpg"
        template.save(result_path)

        # Вставка водяного знака образец
        user_photo = Image.open("img/sample.png")
        user_photo = user_photo.resize(sample_size)
        template.paste(user_photo, sample_position, user_photo)

        # Сохранение и отправка результата
        result_path_sample = f"img/sample_{message.from_user.id}.jpg"
        template.save(result_path_sample)
        await message.reply_photo(photo=FSInputFile(result_path_sample),
                                  caption=text[f'{user[4]}']['price'],
                                  reply_markup=await kb_price(text_btn=text[f'{user[4]}']['in_Cheque']))

    else:

        await message.answer("Отправьте фото для генерации картинки.")
        return

    # Завершение состояния
    await state.clear()


'''Прикрепление карты'''
@router.callback_query(F.data.startswith("output_check"))
async def output_check_callback(callback_query: types.CallbackQuery, state: FSMContext):
    user = get_user(callback_query.from_user.id)
    await callback_query.message.answer(text=text[f'{user[4]}']['out_Cheque'])
    await state.set_state(Form.price)
    await callback_query.answer()



'''Обработка отправки сообщения админу с чеком'''
@router.message(StateFilter(Form.price))
async def process_payment_proof(message: types.Message, state: FSMContext):
    tg_id = message.from_user.id

    # Получение идентификатора администратора (замените на реальный ID)

    admins = get_admins()
    user = get_user(tg_id)

    for admin in admins:
        await message.copy_to(chat_id=admin[0],
                              caption=f"Пользователь {user[0]} отправил чек для подтверждения оплаты.",
                              reply_markup= await output_admin(user[0]))

    await message.answer(text=text[f'{user[4]}']['send_message'])
    await state.clear()


'''Ответ админа'''
@router.callback_query(F.data.startswith("chPhoto_"))
async def output_check_callback(callback: types.CallbackQuery):
    user = get_user_id(callback.data.split('_')[1])
    if callback.data.split('_')[-1] == "no":
        await bot.send_message(chat_id=user[1],
                               text=text[f'{user[4]}']['error_check'])
        await bot.delete_message(chat_id=callback.message.chat.id,
                                 message_id=callback.message.message_id)
        await callback.answer()
    else:
        # Путь к результату
        result_path_sample = f"img/{user[1]}.jpg"

        try:
            # Отправка результата пользователю
            await bot.send_photo(chat_id=user[1], photo=FSInputFile(result_path_sample))

            # Удаление файла после отправки
            os.remove(result_path_sample)
            os.remove(f"img/sample_{user[1]}.jpg")
            os.remove(f"img/removed_{user[1]}.jpg")

        except FileNotFoundError:
            print(f"Файл {result_path_sample} не найден для удаления.")

        # Удаление сообщения у администратора
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)

    await callback.answer()