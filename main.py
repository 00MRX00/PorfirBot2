import logging
import misc
import hashlib
import json
import requests
from aiohttp import BasicAuth

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineQuery, InputTextMessageContent, InlineQueryResultArticle

API_TOKEN = misc.token
PROXY_URL = misc.proxies

global hystory
hystory = {}

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher

bot = Bot(token=API_TOKEN, proxy=PROXY_URL)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    addToHystory(message)
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")

@dp.message_handler(commands=['porf'])
async def index(message: types.Message):
    addToHystory(message)
    await message.answer("Придумайте начало истории...")

@dp.message_handler(regexp='[^*]')
async def textMessage(message: types.Message):
    global hystory
    question = addToHystory(message)
    chatId = question["chat"]["id"]
    messageText = question["text"]
    if len(hystory[str(chatId)]) >= 2 and "/porf" in hystory[str(chatId)][-2]["text"]:
        answer = beginStoryHandler(chatId, messageText)
        await message.answer(answer, reply_markup=keyboard([1, 2, 3, 4]))
    else:
        await message.answer("Простите, но пока я не знаю такой команды(")

def keyboard(buttonsText):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    buttons = [{"text": el} for el in buttonsText]
    markup.row(*buttons)
    return markup

def beginStoryHandler(chatId, messageText):
    url = "https://models.dobro.ai/gpt2/medium/"
    text = {
        "prompt": messageText,
        "num_samples": 4,
        "length": 30
    }
    data = {
        "chat_id": chatId,
        "text": json.dumps(text)
    }
    headers = {
        "Content-Type": "application/json"
    }
    responce = requests.post(url, data=data["text"], headers=headers)
    answer = "Извините, что-то пошло не так :("
    if responce:
        answer = ""
        for i in range(3, -1, -1):
            answer += f"[{abs(i-4)}] - {messageText + responce.json()['replies'][i]}\n\n"
    return answer


def addToHystory(message):
    global hystory
    msg = json.loads(message.as_json())
    if str(msg["chat"]["id"]) not in hystory.keys():
            hystory[str(msg["chat"]["id"])] = list()
    hystory[str(msg["chat"]["id"])].append(msg)
    return msg


def resultsToFile(fileName, text):
    with open(f"{fileName}.json", "w", encoding="utf-8") as file:
        json.dump(text, file, indent=4, ensure_ascii=False)

# @dp.message_handler(commands=['r'])
# async def showButtonsT(message: types.Message):
#     await message.answer("Супер пупер кнопки!!!", reply_markup=types.ReplyKeyboardRemove())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)