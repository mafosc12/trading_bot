import pandas as pd

WIDTHS = {'L:L':20, 'B:F':9} #so the time width goes to 20 and columns B to F go to 9

def set_widths(pair,writer): #this function is just here to make the widths of the columns in excel big enough so you can see all of the data and not just get ###

    worksheet = writer.sheets[pair]
    for k,v in WIDTHS.items():
        worksheet.set_column(k, v)

def get_line_chart(book, start_row, end_row, labels_col, data_col, title, sheetname):

    chart = book.add_chart({'type' : 'line'})
    chart.add_series({'categories' : [sheetname, start_row, labels_col, end_row, labels_col], 'values' : [sheetname, start_row, data_col, end_row, data_col], 'line' : {'color' : 'blue'}})
    chart.set_title({'name' : title})
    chart.set_legend({'none' : True})
    return chart

def add_chart(pair, cross, df, writer):
    
    workbook = writer.book
    worksheet = writer.sheets[pair]

    chart = get_line_chart(workbook, 1, df.shape[0], 11, 12, f"GAIN_C for {pair} {cross}", pair)
    chart.set_size({'x-scale' : 2.5, 'y_scale' : 2.5})
    worksheet.insert_chart('O1', chart)

def add_pair_charts(df_ma_res, df_ma_trades, writer):
    cols = ['time', 'GAIN_C']
    df_temp = df_ma_res.drop_duplicates(subset='pair') #this gets rid off all of the combinations for each currency pair other than the top performing one (one with the most gain) as they have beem ordered top down, hence this df_temp is a data frame with all of the top performing crosses for each currency pair

    for _, row in df_temp.iterrows(): # the _ is python convention for when u arent intending on using the 'i' in the for loop       
        dft = df_ma_trades[(df_ma_trades.cross  == row.cross)&(df_ma_trades.pair == row.pair)]    #this selects the pair and then the correct cross combo (i.e. the highest performing one)    
        dft[cols].to_excel(writer,sheet_name=row.pair,index=False, startrow=0, startcol=11)
        set_widths(row.pair, writer)
        add_chart(row.pair, row.cross, dft, writer)

def add_pair_sheets(df_ma_res, writer):
    for p in df_ma_res.pair.unique():  #gives us all the unique pairnames
        tdf = df_ma_res[df_ma_res.pair == p]
        tdf.to_excel(writer, sheet_name=p, index=False) #this should add the pairs to the excel doc one at a time

def prepare_data(df_ma_res, df_ma_trades):
    df_ma_res.sort_values(by=['pair', 'total_gain'], ascending=[True, False], inplace=True)  #here we are sorting our data by alphabetical order for the pair name (here ascending is true), and we are also at the same time are ordering the total_gain in descending order (hence why the second value in the ascending array is False)
    df_ma_trades['time'] = [x.replace(tzinfo= None) for x in df_ma_trades['time']] #we are just removing the tzinfo (time-zone info) from the time collumn of our data as this if not removed will cause issues later on

def process_data(df_ma_res, df_ma_trades, writer):
    prepare_data(df_ma_res, df_ma_trades)
    add_pair_sheets(df_ma_res, writer)
    add_pair_charts(df_ma_res, df_ma_trades, writer)

def create_excel(df_ma_res, df_ma_trades, granularity):
    filename = f"ma_sim_{granularity}.xlsx"
    writer = pd.ExcelWriter(filename, engine="xlsxwriter")

    process_data(df_ma_res[df_ma_res.granularity == granularity].copy(),df_ma_trades[df_ma_trades.granularity == granularity].copy(),writer)
    writer._save()

def create_ma_res(granularity):
    df_ma_res = pd.read_pickle("./data/ma_res.pkl")
    df_ma_trades = pd.read_pickle("./data/ma_trades.pkl")
    create_excel(df_ma_res, df_ma_trades, granularity)
    

if __name__ == "__main__":

    df_ma_res = pd.read_pickle("../data/ma_res.pkl")
    df_ma_trades = pd.read_pickle("../data/ma_trades.pkl")
    create_excel(df_ma_res, df_ma_trades, "H1")
    create_excel(df_ma_res, df_ma_trades, "H4")



#in summary:
#have loaded up the dataframes using pd.read and set our granularities to H1 and H4
#then go to create_excel here we make the filename and create the writer to write to this file
#then go to process_data inputing the data but filtering for the correct granularity
#then go to prepare data and the data is sorted by name and total_gain, modifying the data using inplace (inplace basically replaces the orginal data with the new ordered data under the same name)
#then go to add_pair_sheets and a new sheet is formed for every unique pairname