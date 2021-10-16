import pygsheets
import pandas as pd
import logging
from typing import Dict, Final
from datetime import date
import os
from enum import Enum
from typing import List
from typing import Any

logging.basicConfig(level=logging.INFO)

today = date.today()

class HoursEnum(Enum):
    SEVEN_AM: str = "7"
    TEN_AM: str = "10"
    FOUR_PM: str = "16"
    SEVEN_PM: str = "19"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_
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
    __ROOT_DIR: str = os.path.dirname(os.path.abspath(__file__))

    def __init__(self) -> None:
        #authorization
        gc = pygsheets.authorize(client_secret=self.__ROOT_DIR+"/client_secret.json")
        #open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
        self.__sh = gc.open('Cross Persistent')
        #select the first sheet 

    def add(self, name: str, hour:str) -> str:
        # Get Sheet current state as pandas Dataframe
        wks = self.__sh.sheet1
        available_slots_sheet = self.__sh[1]
        #retrieve all rows of the worksheet
        cells = wks.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')
        available_slots = available_slots_sheet.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')
        # Create empty dataframe
        if len(cells) <= 1 or len(available_slots) <= 1 or wks.title != today.strftime("%d/%m/%Y"):
            wks.clear()
            available_slots_sheet.clear()
            wks.title = (today.strftime("%d/%m/%Y"))
            available_slots_sheet.title = (today.strftime("%d/%m/%Y") + " slots")
            df = pd.DataFrame([[name, hour]], columns=["name", "hour"])
            wks.set_dataframe(df,(1,1))

            data_frame: List[List[str]] = []

            for h in HoursEnum:
                if h.value == hour:
                    data_frame.append([h.value, (self.__MAX_SLOTS_PER_DAY - 1)])
                else:
                    data_frame.append([h.value, self.__MAX_SLOTS_PER_DAY])

            if not HoursEnum.has_value(hour):
                data_frame.append([hour, (self.__MAX_SLOTS_PER_DAY - 1)])

            df = pd.DataFrame(data_frame, columns=["hour", "slots"])
            available_slots_sheet.set_dataframe(df, (1,1))
            return f"{name} reserva às {hour} horas dia {wks.title} registada com sucesso."
    
        for cell in cells:
            if name in cell:
                return f"{name}, já está registado para hoje, às {cell[1]} horas."
        
        if HoursEnum.has_value(hour) or (not HoursEnum.has_value(hour) and self.__checkHour(hour=hour,available_slots=available_slots,)):
            first_index: int = -1
            for index, cell in enumerate(available_slots):
                if cell[0] == "hour" and cell[1] == "slots":
                    pass
                else:
                    if first_index == -1:
                        first_index = index
                    if cell[0] == hour:
                        if int(cell[1]) > 0:
                            available_slots[index][1] = str(int(available_slots[index][1]) - 1)
                            df = pd.DataFrame(available_slots[first_index::], columns=["hour", "slots"])
                            available_slots_sheet.clear()
                            available_slots_sheet.set_dataframe(df, (1,1))
                        else:
                            return f"{name}, não há vagas disponíveis para as {hour} horas!"
        else:
            logging.info("Here")
            available_slots_sheet.append_table(values=[hour, (self.__MAX_SLOTS_PER_DAY - 1)])
        wks.append_table(values=[name, hour])       
        return f"{name} reserva às {hour} horas dia {wks.title} registada com sucesso."         
                
    def remove(self, name: str) -> None:
        wks = self.__sh[0]
        available_slots_sheet = self.__sh[1]
        # Get Sheet current state as pandas Dataframe
        cells = wks.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')
        available_slots = available_slots_sheet.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')

        for i, value in enumerate(cells):
            if(value[0] == name):
                wks.delete_rows(int(i) + 1)
                first_index: int = -1
                for index, cell in enumerate(available_slots):
                    if cell[0] == "hour" and cell[1] == "slots":
                        pass
                    else:
                        if first_index == -1:
                            first_index = index
                        if cell[0] == value[1]:
                            available_slots[index][1] = str(int(available_slots[index][1]) + 1)
                            df = pd.DataFrame(available_slots[first_index::], columns=["hour", "slots"])
                            available_slots_sheet.clear()
                            available_slots_sheet.set_dataframe(df, (1,1))
                            return f"{name}, a aula das {value[1]} horas foi desmarcada com sucesso!"
        return f"{name}, não tem aulas marcadas."

    def list(self) -> str:
        wks = self.__sh[0]
        cells = wks.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')
        result = ""

        result: Dict = {}

        for cell in cells:
            logging.info(cell)
            logging.info(not cell[1].isdigit())
            if (not cell[1].isdigit()):
                continue 
            if cell[1] not in result.keys():
                result[cell[1]] = [cell[0]]
            else:
                result[cell[1]].append(cell[0])

        toSend: str = ""

        for key in result:
            toSend +=f"Às {key} horas:\n"
            for element in result[key]:
                toSend += f"{element}\n"
            toSend += "\n"

        return toSend

    def __checkHour(self, *, hour: str, available_slots:List[List[str]]) -> bool:
        for row in available_slots:
            if hour == row[0]:
                return True
        return False

