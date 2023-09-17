import requests
import pandas as pd
import constants.defs as defs
from dateutil import parser
from datetime import datetime as dt

class OandaApi:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {defs.API_KEY}",
            "Content-Type": "application/json"
        })

    def make_request(self, url, verb='get', code=200, params=None, data=None, headers=None): #this func literally just makes the request for data to oanda, with some error stuff. the try and exception bit is to save u from the whole bot crashing if the request goes wrong it some weird way, if this happens it will go to the exception part and then move on as relevant
        full_url = f"{defs.OANDA_URL}/{url}" #url represents the endpoint we want 
        try:
            response = None
            if verb == "get":
                response = self.session.get(full_url, params=params, data=data, headers=headers) #this is the bit which is actually making the request to oanda, saving the response under response
            
            if response == None:
                return False, {'error': 'verb not found'}

            if response.status_code == code:
                return True, response.json() #what we want, return the data (response.json()) and also True to tell us the request all went well
            else:
                return False, response.json() #request was actually made but something went wrong, still return response.json() so we can look at the error message later on
            
        except Exception as error:
            return False, {'Exception': error}

    def get_account_ep(self, ep, data_key): #ep stands for endpoint. this function makes the relevant url, plugs this into the make_requests function, checks the request went ok  and checks the data_key you want is actually present in the response from oanda as sometimes the request goes fine but its just empty and you dont have the data you want so you must screen for this (if not prints error)
        url = f"accounts/{defs.ACCOUNT_ID}/{ep}"
        ok, data = self.make_request(url);

        if ok == True and data_key in data:
            return data[data_key]
        else:
            print("ERROR get_account_ep()", data)
            return None

    def get_account_summary(self): #gets the account summary by calling the get account endpoint func and setting the end point as summary and the datakey you want as account
        return self.get_account_ep("summary", "account")

    def get_account_instruments(self): #gets the account instrument list by obvs if read above hash
        return self.get_account_ep("instruments", "instruments")
    
    def fetch_candles(self, pair_name, count=10, granularity='H1', price='MBA', date_f=None, date_t=None): #this function just makes the request to oanda for the candle data, returning this unproccessed data and the error-code, also does a bit of error checking
        url = f"instruments/{pair_name}/candles"
        params = dict(
            granularity = granularity,
            price = price
            )    #just setting up the relevant url and params (note for candles data unlike instruments the params are required)
        if date_f is not None and date_t is not None: #so if the end and start date from which you want the data to range over has been specified (note if it hasnt been specified this is fine as we just run over the length of time specified by the count)
            date_format = "%Y-%m-%dT%H:%M:%SZ"
            params['from'] = dt.strftime(date_f, date_format) #just converting the datetimes into the format that the oandaapi wants in the request
            params['to']=dt.strftime(date_t, date_format)
        else: #so no datetime range specified here so we just use the count
            params['count'] = count

        ok, data = self.make_request(url, params=params) #use the make_requests function which makes the request, and returns either true or false (depending on if it was successful or not) and the data
        if ok == True and 'candles' in data: #either return the candles subsection of the data if all went well or print an error message if the request was unsuccessful
            return data['candles']
        else:
            print("ERROR fetch_candles", params, data)
            return None

    
    def get_candles_df(self, pair_name, **kwargs): #what this does is take the response from our request to oanda, and create a dataframe (basically just a table), with the collumns volume and time (which have the volume and time underneath them respectively) and mid_o, mid_h . . . ask_o, . .  . bid_c with the corresponding prices underneath these respectively
        
        data = self.fetch_candles(pair_name, **kwargs) #note **kwargs is just to get around typing out all of the arguments as seen at the end of fetch_candles (it just copies all of the arguments from there down to here)
        if data is None: #error check
            return None
        if len(data) == 0:
            return pd.DataFrame() #error checker, if the list is empty this returns an empty dataframe
        prices = ['mid', 'bid', 'ask']
        ohlc = ['o', 'h', 'l', 'c']
        final_data = []
        for candle in data:
            if candle['complete'] == False: #ignore the incomplete candles
                continue
            new_dict = {}
            new_dict['time'] = parser.parse(candle['time']) #converts the time string into a nicer datetime
            new_dict['volume'] = candle['volume']
            for p in prices:
                if p in candle: #to make sure that we dont try and make a dataframe with ask for example if we didnt fetch the ask data when calling fetch_candles
                    for o in ohlc:
                        new_dict[f'{p}_{o}'] = float(candle[p][o]) 
            final_data.append(new_dict)
        df = pd.DataFrame.from_dict(final_data)
        return df #returns the nicely formatted data frame

    
    