from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import SimpleEventIsolation

from Config_Data.config import Config, load_config

# Загружаем конфиг в переменную config
config: Config = load_config()

# Инициализируем бот и диспетчер
bot: Bot = Bot(token=config.tg_bot.token,
               )
dp: Dispatcher = Dispatcher(events_isolation=SimpleEventIsolation())