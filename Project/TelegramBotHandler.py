
from time import sleep as sec_sleep
from utility import telegram_api_key, telegram_chat_id
from threading import Thread
from telegram import Bot as TelegramBot
from pandas import DataFrame
from dataframe_image import export as image_export

class TelegramBotHandler(Thread):
    def __init__(self, aggregation_handler, image_dir="tmp", intervall=10):
        Thread.__init__(self)

        self.dir = image_dir
        self.aggregation_handler = aggregation_handler
        self.intervall=intervall
        self.df = None
        # self.terminate = False
        self.daemon = True
        self.bot = TelegramBot(token=telegram_api_key)

        self.start()

    def run(self):
        
        while True:
            data = self.aggregation_handler.build_aggregate()
            columns = list(data.keys())

            if len(columns) > 0:

                indexes = data["max"].keys()
                self.df = DataFrame(index=indexes,columns=columns)

                for column in columns:
                    data_column = list(data[column].values())
                    self.df[column] = data_column

                image_export(self.df,self.dir+"/table.png")
                self.bot.sendPhoto(chat_id=telegram_chat_id, photo=open(self.dir+"/table.png",'rb'))
            
                sec_sleep(self.intervall)