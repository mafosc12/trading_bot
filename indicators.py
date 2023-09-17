import pandas as pd

def BollingerBands(df: pd.DataFrame, n=20,s=2):
    typical_p = (df.mid_c + df.mid_h + df.mid_l)/3 #calculates the typical price
    stddev = typical_p.rolling(window=n).std()  #finds the n period standard deviation using the typical price note the rolling is needed as the typical_price is a list and therefore so is this
    df["BB_MA"] = typical_p.rolling(window=n).mean() #finds the n period roling average mean for the typical price, as this is something we want we add it to a new collumn in our dataframe
    df["BB_UP"] = df["BB_MA"] + stddev*s #the higher bollinger band
    df["BB_LW"] = df["BB_MA"] - stddev*s #the lower bollinger band
    return df

def ATR(df: pd.DataFrame, n=14): #function to calc the average true range

    prev_c = df.mid_c.shift(1) # the previous closing price
    tr1 = df.mid_h - df.mid_l #the first true range and so on
    tr2 = abs(df.mid_h - prev_c)
    tr3 = abs(prev_c - df.mid_l)

    tr = pd.DataFrame({'tr1': tr1,'tr2': tr2, 'tr3': tr3}).max(axis=1) #creates a data frame with 3 collumns one for each of the true ranges and then from that data frame we take the max value for each row, returning that as a series called tr
    df[f"ATR_{n}"] = tr.rolling(window=n).mean() #then calc our ATR by finding the rolling average and then we add it as an extra collumn on our dataframe
    return df

def KeltnerChannels(df: pd.DataFrame, n_ema=20, n_atr=10):
    df['EMA'] = df.mid_c.ewm(span=n_ema, min_periods=n_ema).mean() #finds our exponential moving average
    df = ATR(df, n=n_atr) #call atr func to calc the atr
    c_atr = f"ATR_{n_atr}"
    df['KeUp'] = df[c_atr]*2 + df.EMA #finds the upper Keltner channel
    df['KeLo'] = df.EMA - df[c_atr]*2
    df.drop('ATR', axis=1, inplace=True) # gets rid of the atr collumn from our dataframe as we no longer need it
    return df

def RSI(df: pd.DataFrame, n=14):
    alpha = 1.0/n
    gains = df.mid_c.diff()

    wins = pd.Series([x if x>= 0 else 0.0 for x in gains], name='wins')
    losses = pd.Series([x * -1 if x<0 else 0.0 for x in gains], name='losses')

    wins_rma = wins.ewm(min_periods=n, alpha=alpha).mean()
    losses_rma = losses.ewm(min_periods=n, alpha=alpha).mean()

    rs = wins_rma/losses_rma #relative strength

    df[f"RSI_{n}"] = 100.0 - (100.0/(1.0+rs)) #our RSI
    return df

def MACD(df: pd.DataFrame, n_slow=26, n_fast=12, n_signal=9):

    ema_long = df.mid_c.ewm(min_periods=n_slow, span=n_slow).mean()
    ema_short = df.mid_c.ewm(min_periods=n_fast, span=n_fast).mean()

    df['MACD'] = ema_short - ema_long
    df['SIGNAL'] = df.MACD.ewm(min_periods=n_signal, span=n_signal).mean()
    df['HIST'] = df.MACD - df.SIGNAL

    return df
