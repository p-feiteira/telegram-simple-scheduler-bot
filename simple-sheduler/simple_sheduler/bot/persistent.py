import pygsheets
import pandas as pd
import logging
from typing import Final
from datetime import date

logging.basicConfig(level=logging.INFO)

today = date.today()
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

    __MAX_SLOTS_PER_DAY: Final[int] = 6

    def __init__(self) -> None:
        #authorization
        gc = pygsheets.authorize(client_secret="/home/pedro/Github/telegram-simple-scheduler-bot/client_secret.json")
        #open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
        self.__sh = gc.open('Cross Persistent')
        #select the first sheet 

    def add(self, name: str, hours:str) -> str:
        # Get Sheet current state as pandas Dataframe
        wks = self.__sh.sheet1
        #retrieve all rows of the worksheet
        cells = wks.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')

        for cell in cells:
            if name in cell:
                return f"{name}, já está registado para hoje, às {cell[1]} horas."

        if((len(cells) - 1) < self.__MAX_SLOTS_PER_DAY):
            # Create empty dataframe
            if len(cells) == 1 or wks.title != today.strftime("%d/%m/%Y"):
                wks.title = (today.strftime("%d/%m/%Y"))
                df = pd.DataFrame([[name, hours]], columns=["name", "hours"])
                wks.set_dataframe(df,(1,1))
            else:
                wks.append_table(values=[name, hours])
            return f"{name} reserva às {hours} horas dia {wks.title} registada com sucesso."
        else:
            return f"{name}, não há vagas disponíveis para as {hours} horas!"

    def remove(self, name: str) -> None:
        wks = self.__sh[0]
        # Get Sheet current state as pandas Dataframe
        cells = wks.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')
        for i, value in enumerate(cells):
            if(value[0] == name):
                wks.delete_rows(int(i) + 1)
                break

    def list(self) -> str:
        wks = self.__sh[0]
        cells = wks.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')
        result = ""
        for cell in cells:
            result += f"{cell}\n"
        return result
