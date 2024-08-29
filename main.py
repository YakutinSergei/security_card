import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, StateFilter, Text
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InputFile
from rembg import remove
from PIL import Image, ImageDraw, ImageFont
from database import init_db, add_user, user_exists, get_user, update_tokens, add_tokens

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token="YOUR_BOT_TOKEN")
dp = Dispatcher(storage=MemoryStorage())

# Инициализация базы данных
init_db()

# Определение состояний
class Form(StatesGroup):
    korean_name = State()
    birth_date = State()
    photo = State()

# Кнопка отмены
cancel_button = KeyboardButton("Отмена")
cancel_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(cancel_button)

# Стартовая команда
@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    tg_id = message.from_user.id

    # Проверка пользователя в базе данных
    if not user_exists(tg_id):
        add_user(tg_id)
        await message.answer("Вы были добавлены в базу данных как пользователь.", reply_markup=cancel_keyboard)
    else:
        user = get_user(tg_id)
        tokens = user[3]
        if tokens <= 0:
            await message.answer("У вас не осталось жетонов для генерации картинки. Свяжитесь с администратором для пополнения жетонов.")
            return

    await message.answer("Введите ваше имя на корейском языке:", reply_markup=cancel_keyboard)
    await state.set_state(Form.korean_name)

# Обработка команды отмены
@dp.message(Text("Отмена"))
async def cancel_process(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Операция отменена. Вы можете начать заново, нажав /start.", reply_markup=ReplyKeyboardRemove())

# Запрос имени на корейском
@dp.message(StateFilter(Form.korean_name))
async def get_korean_name(message: types.Message, state: FSMContext):
    await state.update_data(korean_name=message.text)
    await message.answer("Теперь введите вашу дату рождения (например, 1990-01-01):", reply_markup=cancel_keyboard)
    await state.set_state(Form.birth_date)

# Запрос даты рождения
@dp.message(StateFilter(Form.birth_date))
async def get_birth_date(message: types.Message, state: FSMContext):
    await state.update_data(birth_date=message.text)
    await message.answer("Пожалуйста, отправьте ваше фото:", reply_markup=cancel_keyboard)
    await state.set_state(Form.photo)

# Запрос фотографии
@dp.message(StateFilter(Form.photo), content_types=types.ContentType.PHOTO)
async def get_photo(message: types.Message, state: FSMContext):
    tg_id = message.from_user.id

    # Скачивание фото
    photo = message.photo[-1]
    photo_path = f"{photo.file_id}.jpg"
    await photo.download(photo_path)

    # Удаление фона
    input_image = Image.open(photo_path)
    output_image = remove(input_image)
    output_image_path = f"removed_{photo.file_id}.png"
    output_image.save(output_image_path)

    # Получение данных
    user_data = await state.get_data()
    korean_name = user_data['korean_name']
    birth_date = user_data['birth_date']

    # Создание итогового изображения
    template = Image.open("template.png")  # Загрузите ваш шаблон
    draw = ImageDraw.Draw(template)

    # Позиции для текста и фото (настройте под ваш шаблон)
    name_position = (100, 100)
    date_position = (100, 150)
    photo_position = (300, 100)
    photo_size = (200, 200)

    # Вставка текста
    font = ImageFont.truetype("arial.ttf", 30)  # Замените шрифт при необходимости
    draw.text(name_position, korean_name, font=font, fill="black")
    draw.text(date_position, birth_date, font=font, fill="black")

    # Вставка фотографии
    user_photo = Image.open(output_image_path)
    user_photo = user_photo.resize(photo_size)
    template.paste(user_photo, photo_position, user_photo)

    # Сохранение и отправка результата
    result_path = f"result_{photo.file_id}.png"
    template.save(result_path)
    await message.answer_photo(photo=InputFile(result_path), reply_markup=ReplyKeyboardRemove())

    # Снижение количества жетонов на 1
    user = get_user(tg_id)
    update_tokens(tg_id, user[3] - 1)

    # Завершение состояния
    await state.clear()

# Команда добавления жетонов (доступна только администраторам)
@dp.message(Command("add_tokens"))
async def add_tokens_command(message: types.Message):
    tg_id = message.from_user.id
    user = get_user(tg_id)

    if user[2] != "admin":
        await message.answer("У вас нет прав для выполнения этой команды.")
        return

    args = message.text.split()
    if len(args) != 3:
        await message.answer("Неверный формат команды. Используйте: /add_tokens <tg_id> <количество_жетонов>")
        return

    target_tg_id = int(args[1])
    tokens_to_add = int(args[2])

    if not user_exists(target_tg_id):
        await message.answer("Пользователь с таким tg_id не найден.")
        return

    add_tokens(target_tg_id, tokens_to_add)
    await message.answer(f"Пользователю {target_tg_id} добавлено {tokens_to_add} жетонов.")

# Запуск бота
if __name__ == "__main__":
    dp.run_polling(bot)
