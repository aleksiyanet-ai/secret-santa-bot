import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from config import TOKEN  # токен мы положим в отдельный файл config.py

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Простое хранилище участников (пока в памяти)
participants = {}


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    """
    Обработка команды /start.
    Регистрируем пользователя и просим написать пожелания к подарку.
    """
    user_id = message.from_user.id

    # создаём запись об участнике, если её ещё нет
    if user_id not in participants:
        participants[user_id] = {
            "name": message.from_user.full_name
        }

    text = (
        "Харе Кришна!\n"
        "Добро пожаловать в нашу тёплую игру Вайшнавского Санты.\n\n"
        "Пусть эта маленькая игра принесёт тебе радость и вдохновение "
        "дарить подарки и принимать подарки. :)\n\n"
        "Пожалуйста, напиши свои пожелания к подарку или напиши, если хочешь сюрприз.\n"
        "(Ты можешь перечислить несколько вариантов.)"
    )

    await message.answer(text)


@dp.message_handler(lambda m: m.from_user.id in participants and "wishlist" not in participants[m.from_user.id])
async def wishlist(message: types.Message):
    """
    Первый текст после /start — считаем его списком пожеланий.
    Затем просим адрес.
    """
    user_id = message.from_user.id
    participants[user_id]["wishlist"] = message.text

    text = (
        "Принято!\n"
        "Мы передадим эту информацию твоему Вайшнавскому Санте.\n\n"
        "Теперь напиши адрес, куда твой Вайшнавский Санта "
        "сможет отправить подарок.\n"
        "Это может быть пункт выдачи Wildberries, Ozon или почта России.\n"
        "Обязательно укажи, адрес какого именно пункта ты указал "
        "(Wildberries, Ozon или почта России), чтобы Вайшнавский Санта "
        "не запутался и заказал подарок там, где нужно.\n"
        "(Он увидит его только после распределения, так что всё остаётся анонимно.)"
    )

    await message.answer(text)


@dp.message_handler(
    lambda m: (
        m.from_user.id in participants
        and "wishlist" in participants[m.from_user.id]
        and "address" not in participants[m.from_user.id]
    )
)
async def address(message: types.Message):
    """
    Второй текст после пожеланий — адрес.
    Подтверждаем участие.
    """
    user_id = message.from_user.id
    participants[user_id]["address"] = message.text

    text = (
        "Харибол!\n"
        "Спасибо тебе за доверие и участие в этой маленькой игре.\n\n"
        "Ты успешно присоединилась к клубу Вайшнавских Сант.\n"
        "Скоро ты получишь имя того, кому сможешь подарить "
        "частичку тепла и внимания. :)"
    )

    await message.answer(text)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
