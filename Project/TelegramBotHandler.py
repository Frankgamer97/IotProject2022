from pandas import DataFrame
from telegram import Bot as TelegramBot

from utility import telegram_bot_update_frequency
from DataStorage import StorageHandler

class TelegramBotHandler():

    telegram_api_key = "5509057193:AAHxI7t17bDev0WfgA_V_jC9I_ZcgjGxRvw" 
    telegram_chat_id = "-1001781808448"
    
    def __init__(self, aggregation_handler, maxupdate=telegram_bot_update_frequency, image_dir="tmp"):

        self.dir = image_dir
        self.aggregation_handler = aggregation_handler
        self.df = None
        self.bot = TelegramBot(token=TelegramBotHandler.telegram_api_key)
        self.countupdate=0
        self.maxupdate=maxupdate

        print("[TELEGRAM_BOT] Initialized")

    def __send_updates(self):
        data = self.aggregation_handler.build_aggregate()
        columns = list(data.keys())
        if len(columns) > 0:

            indexes = data["max"].keys()
            self.df = DataFrame(index=indexes,columns=columns)

            for column in columns:
                data_column = list(data[column].values())
                self.df[column] = data_column

            self.df["max"] = self.df["max"].apply(lambda x: round(x,1))
            self.df["min"] = self.df["min"].apply(lambda x: round(x,1))
            self.df["mean"] = self.df["mean"].apply(lambda x: round(x,2))
            self.df["std"] = self.df["std"].apply(lambda x: round(x,2))

            StorageHandler.save_telegrame_bot_image(self.df)
            self.bot.sendPhoto(chat_id=TelegramBotHandler.telegram_chat_id, photo=StorageHandler.load_telegrame_bot_image()) ###########IMPORTANTE
            print("[TELEGRAM_BOT] POST")

    def telegram_updates(self):
        if self.countupdate == self.maxupdate - 1:
            self.countupdate=0
            self.__send_updates()
        else:
            self.countupdate+=1
