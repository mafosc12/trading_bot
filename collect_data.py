import pandas as pd
import datetime as dt
from dateutil import parser

from infrastructure.instrument_collection import InstrumentCollection
from api.oanda_api import OandaApi

#so basically the api limits each request to 5000 candles
#so if we want loads of data we need to make multiple requests
#this code basically just does the requests 
#making sure that the date of the end of the last request is the start of the next one

CANDLE_COUNT = 4000 #how many candles we are going to ask for per request

INCREMENTS = {
    'M5' : 5*CANDLE_COUNT,
    'H1' : 60*CANDLE_COUNT,
    'H4' : 240*CANDLE_COUNT
} #number of minutes the request would last over for the different granularities

def save_file(final_df: pd.DataFrame, file_prefix, granularity, pair):
    filename = f"{file_prefix}{pair}_{granularity}.pkl"

    final_df.drop_duplicates(subset=['time'], inplace=True) #probably dont need this but its here in case the candles df has repeated candles due to overlapping of the dates of our requests, so we drop the duplicates checking via time
    final_df.sort_values(by='time', inplace=True) #again probs not needed just sorts the candles df into time order in case something got jumbled up somehow
    final_df.reset_index(drop=True, inplace=True)
    final_df.to_pickle(filename)    
    print(f"{pair}{granularity}{final_df.time.min()}{final_df.time.max()}{final_df.shape[0]}")

def fetch_candles(pair, granularity, date_f:dt.datetime, date_t: dt.datetime, api: OandaApi):
    attempts = 0 #attempts at getting the data we will try 3 times until we give up, as if it was unsuccessful its most likely due to connection issue or smth so should work upon retrying

    while attempts<3:
        candles_df = api.get_candles_df(pair, granularity=granularity, date_f=date_f, date_t=date_t) #code we wrote earlier in oanda_api.py to get the candles
        if candles_df is not None:
            break #leave this loop
        attempts+=1
    if candles_df is not None and candles_df.empty == False:
        return candles_df
    else:
        return None

def collect_data(pair, granularity, date_f, date_t, file_prefix, api: OandaApi):
    time_step = INCREMENTS[granularity]
    end_date = parser.parse(date_t)
    from_date = parser.parse(date_f)

    candle_dfs = []

    to_date = from_date

    while to_date<end_date:
        to_date = from_date +dt.timedelta(minutes=time_step) # so basically we add on the amount of time corresponding to each request due to the granularity and count we have used
        if to_date > end_date: #this bit is to error check for the last request so you dont go over the end_date i.e. make too many requests
            to_date = end_date
        candles = fetch_candles(pair, granularity, from_date, to_date, api)
        if candles is not None:
            candle_dfs.append(candles) 
            print(f"{pair}{granularity}{from_date}{to_date}{candles.shape[0]} candles loaded")
        else:
            print(f"{pair}{granularity}{from_date}{to_date} --> no candles")

        from_date = to_date   #does this at the end of every loop as the next request should start from the date the one before ended 

    if len(candle_dfs)>0: 
        final_df = pd.concat(candle_dfs) #merges all of the dfs from each request into a single data frame
        save_file(final_df, file_prefix, granularity, pair) #saves the data
    else:
        print(f"{pair}{granularity}--> no data saved!")      

def run_collection(ic: InstrumentCollection, api: OandaApi):
    our_curr = ['EUR','GBP','AUD',"CAD","NZD","JPY","USD"]
    for p1 in our_curr:
        for p2 in our_curr:
            pair = f"{p1}_{p2}"
            if pair in ic.instruments_dict.keys():
                for granularity in ["M5","H1", "H4"]:
                    print(pair, granularity)
                    collect_data(pair, granularity, "2016-01-01T00:00:00Z", "2023-06-01T00:00:00Z","./data/",api)