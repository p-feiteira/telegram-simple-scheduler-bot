import pygsheets
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
class Singleton(type):
    """
    Define an Instance operation that lets clients access its unique
    instance.
    """

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance
class Storage(metaclass=Singleton):
    def __init__(self) -> None:
        #authorization
        gc = pygsheets.authorize(client_secret="/home/pedro/Github/telegram-simple-scheduler-bot/client_secret.json")
        #open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
        self.__sh = gc.open('Cross Persistent')
        #select the first sheet 

    def add(self, name: str, slots: int, hours:str) -> None:
        # Get Sheet current state as pandas Dataframe
        wks = self.__sh[0]
        #retrieve all rows of the worksheet
        cells = wks.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')
        logging.info(len(cells))
        # Create empty dataframe
        if len(cells) == 1:
            df = pd.DataFrame([[name, slots, hours]], columns=["name","slots", "hours"])
            wks.set_dataframe(df,(1,1))
        else:
            wks.append_table(values=[name, slots, hours])

        logging.info(wks.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix'))
        #self.__sh[0].set_dataframe(current_df,(1,1))

    def remove(self, name: str) -> None:
        wks = self.__sh[0]
        # Get Sheet current state as pandas Dataframe
        cells = wks.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')
        logging.info(cells)
        for i in range(1, len(cells)):
            if(cells[i][0] == name):
                logging.info(cells[i][0])
                logging.info(i)
                wks.delete_rows(i+1)
    