import json
from models.instrument import Instrument

class InstrumentCollection:
    FILENAME = "instruments.json"
    API_KEYS = ['name', 'type', 'displayName', 'pipLocation',
         'displayPrecision', 'tradeUnitsPrecision', 'marginRate']

    def __init__(self):
        self.instruments_dict = {}
        
    def LoadInstruments(self, path):  #this converts the data we have loaded from the api about the instruments, into the class form we have defined in instruments.py hence each pair is now a class
        self.instruments_dict = {}
        fileName = f"{path}/{self.FILENAME}"
        with open(fileName, "r") as f:
            data = json.loads(f.read())
            for k, v in data.items():
                self.instruments_dict[k] = Instrument.FromApiObject(v)

    def CreateFile(self, data, path):
        if data is None:
            print("Instrument file creation failed")
            return
        
        instruments_dict = {}
        for i in data:
            key = i['name']    #so key would be the name of the pair
            instruments_dict[key] = { k: i[k] for k in self.API_KEYS }  #then we make an object with the names of the pair as a label and then stored underneath each of these the value for each of the things listed in api_keys for each of the pairs

        fileName = f"{path}/{self.FILENAME}"
        with open(fileName, "w") as f:
            f.write(json.dumps(instruments_dict, indent=2)) #apparently the indent = 2 lets us see it as a human


    def PrintInstruments(self): #this is just here so that we could run it as a sanity check tnat Loadinstruments actually works
        [print(k,v) for k,v in self.instruments_dict.items()]
        print(len(self.instruments_dict.keys()), "instruments")

instrumentCollection = InstrumentCollection()