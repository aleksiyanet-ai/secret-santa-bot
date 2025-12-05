import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from config import TOKEN  # токен лежит в config.py

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Хранилище участников в памяти
# user_id -> { "step": ..., "name": ..., "wishlist": ..., "delivery_type": ..., "address": ... }
participants = {}


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    """
    Команда /start.
    Приветствие и запрос духовного имени.
    """
    user_id = message.from_user.id

    # При каждом /start начинаем регистрацию заново
    participants[user_id] = {
        "step": "name"
    }

    text = (
        "Х а р и б о л!\n"
        "Мы рады приветствовать тебя в клубе анонимных Вайшнавских Сант.\n\n"
        "Здесь мы будем практиковать один из главных принципов Шри Упадешамриты: "
        "дарить подарки и принимать подарки.\n\n"
        "Для начала назови свое духовное имя, пожалуйста."
    )

    await message.answer(text)


@dp.message_handler(lambda m: m.from_user.id in participants)
async def registration_flow(message: types.Message):
    """
    Общий обработчик для всех шагов регистрации.
    Смотрим, на каком шаге сейчас участник, и ведём дальше.
    """
    user_id = message.from_user.id
    user = participants.get(user_id, {})
    step = user.get("step")

    # Если по какой-то причине шага нет — начнём сначала
    if step is None:
        participants[user_id] = {"step": "name"}
        step = "name"

    # ШАГ 1: ИМЯ
    if step == "name":
        name = message.text.strip()
        user["name"] = name
        user["step"] = "wishlist"

        text = (
            f"Приятно познакомиться, {name}.\n\n"
            "А теперь подскажи своему Вайшнавскому Санте, чем он может порадовать тебя.\n"
            "Или просто напиши, что хочешь получить сюрприз.\n\n"
            "Для того, чтобы игра была комфортной для всех, мы устанавливаем денежный лимит "
            "на подарок — он должен быть в пределах 1000 рублей."
        )
        await message.answer(text)
        return

    # ШАГ 2: ПОЖЕЛАНИЯ
    if step == "wishlist":
        user["wishlist"] = message.text.strip()
        user["step"] = "delivery_type"

        text = (
            "А теперь скажи, пожалуйста, где тебе удобно получить подарок.\n\n"
            "Возможные варианты:\n"
            "- пункт выдачи Wildberries\n"
            "- пункт выдачи Ozon\n"
            "- почтой России\n\n"
            "Напиши, пожалуйста, один из этих вариантов."
        )
        await message.answer(text)
        return

    # ШАГ 3: СПОСОБ ПОЛУЧЕНИЯ ПОДАРКА
    if step == "delivery_type":
        choice_raw = message.text.strip().lower()

        if "wildberries" in choice_raw:
            delivery_type = "wildberries"
        elif "ozon" in choice_raw:
            delivery_type = "ozon"
        elif "почта" in choice_raw or "почтой" in choice_raw:
            delivery_type = "post"
        else:
            # Не распознали ответ — просим повторить
            text = (
                "Пока я не могу понять твой вариант.\n\n"
                "Пожалуйста, выбери один из вариантов и напиши его текстом:\n"
                "- пункт выдачи Wildberries\n"
                "- пункт выдачи Ozon\n"
                "- почтой России"
            )
            await message.answer(text)
            return

        user["delivery_type"] = delivery_type
        user["step"] = "address"

        if delivery_type in ("wildberries", "ozon"):
            text = (
                "Твоему Вайшнавскому Санте понадобится адрес пункта выдачи.\n\n"
                "Пожалуйста, напиши:\n"
                "- город,\n"
                "- точный адрес пункта выдачи,\n"
                "- и укажи, это Wildberries или Ozon."
            )
        else:
            text = (
                "Твоему Вайшнавскому Санте понадобится твой точный почтовый адрес и твои ФИО.\n\n"
                "Пожалуйста, напиши:\n"
                "- индекс,\n"
                "- город,\n"
                "- улицу, дом, квартиру,\n"
                "- и свои фамилию, имя и отчество."
            )

        await message.answer(text)
        return

    # ШАГ 4: АДРЕС
    if step == "address":
        user["address"] = message.text.strip()
        user["step"] = "done"

        text = (
            "Джай, регистрация завершена.\n\n"
            "Сейчас мы ожидаем, пока все участники присоединятся к нам, "
            "после чего администратор нажмет волшебную кнопку, и тогда у каждого из нас "
            "появится свой Вайшнавский Санта.\n\n"
            "Хотим обратить внимание на то, что все подарочки должны отправиться к своим "
            "получателям до 20 декабря.\n"
            "Давайте будем внимательными и чуткими друг к другу, ведь игра создана именно "
            "для этого — получить возможность осчастливить своим вниманием и хорошим отношением "
            "хотя бы одного вайшнава."
        )

        await message.answer(text)
        return

    # ЕСЛИ ШАГ "done" И ЧЕЛОВЕК ПИШЕТ ДАЛЬШЕ
    if step == "done":
        text = (
            "Ты уже прошёл(ла) регистрацию в игре Вайшнавского Санты.\n"
            "Если хочешь всё начать сначала, просто отправь команду /start."
        )
        await message.answer(text)
        return


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
