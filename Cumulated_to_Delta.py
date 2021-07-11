# -*- coding: utf-8 -*-
"""
Data processing Buehl, Deal with cumulated precipitaion time series

Created on Thu May 27 14:45:58 2021

@author: alexa

WATCH OUT not to overwrite wrong csv file at the end

AND add a row on top manuallyy like in the original files
"""



#%% load required packages
import pandas as pd
import matplotlib.pyplot as plt 
from re import search

# %% Set path
current_file = "Schönbrunn_Cumulated.csv"
target_file = "Schönbrunn.csv"
current_folder = "Daten-2020/10_22_20/"
mypath = "D:/Dokumente/Studium/KIT2/HIWI/Data_Buehl/" + current_folder + current_file

df = pd.read_csv(mypath ,skiprows=1)
time_col = ''.join([col for col in df.columns if "Date" in col])           # search for rows that contain data of interest
time_col_nr = df.columns.get_loc('Date Time, GMT+00:00')
temp_col =[col for col in df.columns if "Temp" in col]
prec_col =[col for col in df.columns if "Niederschlag" in col]

# there are two diffent time formats in the HOBO files: "%d/%m/%y %h:%M" and "%m/%d/%y %I:%M:%S %p"
# -> if infirst DateTime entry  AM or PM is included, use the second format, else use the first
date1 = pd.to_datetime(df[time_col], format="%m/%d/%y %I:%M:%S %p", errors='coerce')
date2 = pd.to_datetime(df[time_col], format="%m/%d/%Y %H:%M", errors='coerce')
df[time_col] = date1.combine_first(date2)
df.set_index(time_col, inplace = True)
df.index.names = ["Date Time, GMT+00:00"]
df.fillna(method='ffill', inplace = True) # fill all nan in cumulated precipitation time series with last recorded value

plt.plot(df.index, df.loc[:,prec_col], 'b.')
plt.xticks(rotation = 45)
plt.title("cumulated")
plt.show()


# to deltas instead of cumulative:
df_non_cumulated = df.loc[:,prec_col].diff()
# they always logged at the moment of the gauge tipping and not every 5 minutes -> always get value to the next 5 min 
df_new = df_non_cumulated.resample('5Min').sum()

#add the temperature info to new dataframe
df_new = df_new.join(df.loc[:,temp_col])

# plot for testing

plt.plot(df_new.index, df_new.loc[:,prec_col], 'b.')
plt.xticks(rotation = 45)
plt.title("Processed")
plt.show()
plt.plot(df_new.index, df_new.loc[:,temp_col], 'r.')
plt.xticks(rotation = 45)
plt.show()

# %% store new file
df_new.to_csv("D:/Dokumente/Studium/KIT2/HIWI/Data_Buehl/" + current_folder + target_file, na_rep = "", date_format="%m/%d/%Y %H:%M")

# to use file in the main script, insert a row on top and make custom date format = "%d/%m/%Y %H:%M" 
