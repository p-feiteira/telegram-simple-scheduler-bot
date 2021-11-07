import logging
import threading
import time
import json
from datetime import date, timedelta
from enum import Enum
from typing import Any, Dict, Final, List, Tuple

import pandas as pd
import gspread
from pandas.core.frame import DataFrame
import schedule
from beartype import beartype
from environs import Env

logging.basicConfig(level=logging.INFO)

env = Env()
env.read_env()

SHEETS_TOKEN: dict = json.loads(env.str("SHEETS_TOKEN"))

today = date.today()
tomorrow = today + timedelta(days=1)

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

    __sheetname = "Cross Persistent"

    @beartype
    def __init__(self) -> None:
        #authorization
        gc = gspread.service_account_from_dict(SHEETS_TOKEN)
        #open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
        self.__sh = gc.open(self.__sheetname)

        if self.__sh is None:
            raise SystemError(f"Erro de sistema: folha de cálculo '{self.__sheetname}' não encontrada. Por favor contacte o administrador.")

        self.__setup()
        self.__job()


    @beartype
    def __setup(self):
        try:
            self.__today_wks = self.__sh.worksheet(today.strftime("%d/%m/%Y"))
        except:
            self.__today_wks = self.__sh.add_worksheet(title=today.strftime("%d/%m/%Y"), rows="100", cols="2")
            
        try:
            self.__today_available_slots_sheet = self.__sh.worksheet(today.strftime("%d/%m/%Y") + " slots")
        except:
            self.__today_available_slots_sheet = self.__sh.add_worksheet(title=(today.strftime("%d/%m/%Y") + " slots"), rows="100", cols="2")
            
        try:
            self.__tomorrow_wks = self.__sh.worksheet(tomorrow.strftime("%d/%m/%Y"))
        except:
            self.__tomorrow_wks = self.__sh.add_worksheet(title=tomorrow.strftime("%d/%m/%Y"), rows="100", cols="2")
            
        try:
            self.__tomorrow_available_slots_sheet = self.__sh.worksheet(tomorrow.strftime("%d/%m/%Y") + " slots")
        except:
            self.__tomorrow_available_slots_sheet = self.__sh.add_worksheet(title=(tomorrow.strftime("%d/%m/%Y") + " slots"), rows="100", cols="2")

    @beartype
    def add(self,*, name: str, today: bool = False, hour:str) -> str:
        # Get Sheet current state as pandas Dataframe

        if today:
            wks: Any = self.__today_wks
            available_slots_sheets: Any = self.__today_available_slots_sheet
        # Create empty dataframe
        else:
            wks: Any = self.__tomorrow_wks
            available_slots_sheets: Any = self.__tomorrow_available_slots_sheet

        cells: Any = wks.get_values()
        available_slots: Any = available_slots_sheets.get_values()

        if len(cells) <= 1 or len(available_slots) <= 1:
            wks.append_row(["name", "hour"])

            data_frame: List[Tuple[str, int]] = []

            for h in HoursEnum:
                item: Tuple[str, int] = h.value, self.__MAX_SLOTS_PER_DAY
                data_frame.append(item)

            df = pd.DataFrame(data_frame, columns=["hour", "slots"])
            available_slots_sheets.update([df.columns.values.tolist()] + df.values.tolist())
    
        cell = wks.find(name)

        if cell is not None:
            value =  wks.cell(cell.row, cell.col + 1).value
            return f"{name}, já está registado para {wks.title}, às {value} horas."

        if HoursEnum.has_value(hour):
            cell = available_slots_sheets.find(hour)

            if cell is None:
                raise SystemError(f"Erro no sistema: não há entrada nos slots para as {hour} horas. Contactar administrador, por favor!")

            slot_value = available_slots_sheets.cell(cell.row, cell.col + 1).value
            if int(slot_value) > 0:
                available_slots_sheets.update(f"B{(cell.row)}", str(int(slot_value)-1))
            else:
                return f"{name}, não há vagas disponíveis para as {hour} horas!"
        else:
            cell = available_slots_sheets.find(hour)
            if cell is None:
                available_slots_sheets.append_row([hour, (self.__MAX_SLOTS_PER_DAY - 1)])
            else:
                slot_value = available_slots_sheets.cell(cell.row, cell.col + 1).value
                if int(slot_value) > 0:
                    available_slots_sheets.update(f"B{(cell.row)}", str(int(slot_value)-1))
                else:
                    return f"{name}, não há vagas disponíveis para as {hour} horas!"

        wks.append_row([name, hour])       
        return f"{name} reserva às {hour} horas dia {wks.title} registada com sucesso."         

    @beartype    
    def remove(self, name: str, today: bool = False) -> str:

        if today:
            wks: Any = self.__today_wks
            available_slots_sheets: Any = self.__today_available_slots_sheet
        else:
            wks: Any = self.__tomorrow_wks
            available_slots_sheets: Any = self.__tomorrow_available_slots_sheet

        cell = wks.find(name)

        if cell is None:
            return f"{name}, não tem aulas marcadas para dia {wks.title}."

        hour: str = wks.cell(cell.row, cell.col + 1).value

        slot_cell = available_slots_sheets.find(hour)

        if slot_cell is None:
            raise SystemError("Erro no sistema. Contacte o administrador.")

        wks.delete_row(cell.row)

        slot_value: str = available_slots_sheets.cell(slot_cell.row, slot_cell.col + 1).value

        available_slots_sheets.update(f"B{(slot_cell.row)}", str(int(slot_value)+1))

        return f"{name}, a aula das {hour} horas de dia {wks.title} foi desmarcada com sucesso!"

    @beartype
    def list(self) -> str:
        
        toSend: str = ""
        all_outputs: Dict = {}

        cells: List[List[Any]] = self.__today_wks.get_values()

        if cells is not None and len(cells)>1:
            result: Dict = {}
            for index in range(1,len(cells)):
                if cells[index][1] not in result.keys():
                    result[cells[index][1]] = [cells[index][0]]
                else:
                    result[cells[index][1]].append(cells[index][0])

            all_outputs[self.__today_wks.title] = result

        
        cells: List[List[Any]] = self.__tomorrow_wks.get_values()

        if cells is not None and len(cells)>1:
            result: Dict = {}
            for index in range(1,len(cells)):
                if cells[index][1] not in result.keys():
                    result[cells[index][1]] = [cells[index][0]]
                else:
                    result[cells[index][1]].append(cells[index][0])

            all_outputs[self.__tomorrow_wks.title] = result
        
        for day in all_outputs:
            toSend +=f"\nPara dia {day}:\n\n"
            for key in all_outputs[day]:
                toSend +=f"Às {key} horas:\n"
                for element in all_outputs[day][key]:
                    toSend += f"{element}\n"
                toSend += "\n"

        return toSend        

    def __job(self):
        schedule.every().day.at("01:30").do(self.__setup)
        
        def __loop(self):
            while True:
                schedule.run_pending()
                time.sleep(1)

        thread = threading.Thread(target=__loop, args=(1,))
        thread.start()