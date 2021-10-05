import pygsheets

class Storage:
    def __init__(self) -> None:
        #authorization
        gc = pygsheets.authorize()
        #open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
        sh = gc.open('Cross Persistent')
        #select the first sheet 
        self.__df = sh[0].get_as_df()

    def add(self, name: str, slots: int, hours:str) -> None:
        # Create empty dataframe
        df = pd.Dataframe()
        # Create a column
        df['name'] = [name]
        df['slots'] = [slots]
        df['hours'] = [hours]
        #update the first sheet with df, starting at cell B2. 
        self.__wks.set_dataframe(df,(1,1))
    