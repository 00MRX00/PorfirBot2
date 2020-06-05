import requests
import json
import misc


class Porfirievich:
    def __init__(self):
        self.__URL = 'https://api.telegram.org/bot' + misc.token + '/'
        self.__PROXYES = misc.proxies
        self.__hystory = {}

    def resultsToFile(self, fileName, text):
        with open(f"{fileName}.json", "w", encoding="utf-8") as file:
            json.dump(text, file, indent=4, ensure_ascii=False)

    def getMessage(self, responce):
        chatId = responce["message"]["chat"]["id"]
        if str(chatId) not in self.__hystory.keys():
            self.__hystory[str(chatId)] = list()
        self.__hystory[str(chatId)].append(responce)
        return {
            "chatId": chatId,
            "messageText": responce["message"]["text"]
        }

    def sendMessage(self, chatId, text="Wait a second? please...", replyMarkup=[]):
        url = self.__URL + 'sendMessage'
        if replyMarkup:
            data = {
                "chat_id": chatId,
                "text": text,
                "reply_markup": json.dumps(replyMarkup)
            }
        else:
            data = {
                "chat_id": chatId,
                "text": text
            }
        return requests.get(url, params=data, proxies=self.__PROXYES)

    def slashPorf(self, chatId):
        self.sendMessage(chatId, "Придумайте начало истории...")

    def beginStoryHandler(self, chatId, messageText):
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
                answer += f"[{abs(i-3)}] - {messageText + responce.json()['replies'][i]}\n\n"
        self.sendMessage(chatId, answer)

    def questionHandler(self, responce):
        question = self.getMessage(responce)
        chatId = question["chatId"]
        messageText = question["messageText"]
        if "/porf" in messageText:
            self.slashPorf(chatId)
        elif len(self.__hystory[str(chatId)]) >= 2 and "/porf" in self.__hystory[str(chatId)][-2]["message"]["text"]:
            self.beginStoryHandler(chatId, messageText)
        else:
            answer = "Пока что я не знаю такой команды("
            self.sendMessage(chatId, answer)
        self.resultsToFile("hystory", self.__hystory)
