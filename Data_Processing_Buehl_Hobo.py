# -*- coding: utf-8 -*-
"""

HiWi Buehl Data Processing Try Number 2 

Tasks: 
    - Read out raw csv files from several folders 
    - split csv files for every sensor (in precipitation and temperature for instance)
    - combine csv files for every sensor over whole time 
    - create evenly spaced time series with NaN if no values are available (NO interpolation, Gap filling what so ever)
    - manually replace measured values for certain time ranges with NaN if field log shows irregularities  
    - at the end create some plots and check for gaps/ extreme values 
Created on Mon Apr  5 15:26:51 2021

@author: Alexander Magerl
"""

#%% load required packages
import pandas as pd
import matplotlib.pyplot as plt 
from re import search

# %% Set path
current_folder = "05_21_20"
mypath = "D:/Dokumente/Studium/KIT2/HIWI/Data_Buehl/Daten-2020/" + current_folder
targetpath = "D:/Dokumente/Studium/KIT2/HIWI/Data_Final"

filenames = ["Sternenberg", "Winterberg", "Sportplatz", "Schönbrunn", "Schwabenquelle", 
                         "Hundseck", "Grundigklinik", "Schafhof", "Butschenberg"]  # Schwabenquelle sometimes called Schwabenbrunnen


# %% Loop over files 
    
for current_file in filenames:
    try: 
        # current_file =  filenames[5] # for debugging
        df = pd.read_csv(mypath +"/" +current_file + ".csv", skiprows = 1)  # read csv file (second row with headers)
        time_col = [col for col in df.columns if "Date" in col]             # search for rows that contain data of interest
        time_col_nr = df.columns.get_loc('Date Time, GMT+00:00')
        temp_col =[col for col in df.columns if "Temp" in col]
        prec_col =[col for col in df.columns if "Niederschlag" in col]
        
        # there are two diffent time formats in the HOBO files: "%d/%m/%y %h:%M" and "%m/%d/%y %I:%M:%S %p"
        # -> if infirst DateTime entry  AM or PM is included, use the second format, else use the first
        first_datetime = df[time_col[0]].iloc[0]
        
        if search("AM|PM", first_datetime):
            df[time_col[0]] = pd.to_datetime(df[time_col[0]],  format = "%m/%d/%y %I:%M:%S %p")
        else:
            df[time_col[0]] = pd.to_datetime(df[time_col[0]],  format = "%d/%m/%y %H:%M:%S") 

            
        #in case two different datetime formats are in the same .csv file, comment the previous if statement and uncomennent the following 
        #(would be to slow to run for every file):
        # for index, row in df.iterrows():
        #     if search("AM|PM", df.iloc[index, time_col_nr]):
        #         df.iloc[index, time_col_nr] = pd.to_datetime(df.iloc[index, time_col_nr],  format = "%m/%d/%y %I:%M:%S %p")
        #     else:
        #         df.iloc[index, time_col_nr] = pd.to_datetime(df.iloc[index, time_col_nr],  format = "%m/%d/%Y %H:%M") 
        
        
        df.set_index(time_col, inplace = True)
        df.index.names = ["DateTimeUTC"]
        
        # build new dataframe with only columns of interest and Date Time as index 
        df_temp = df[temp_col]
        df_prec = df[prec_col]
        
        #rename columns
        df_temp.columns = ["Temperature"]
        df_prec.columns = ["Precipitation"]
        
        # regularize -> not a good idea 
        #df_temp = df_temp.asfreq('30Min') # Old 
        df_temp_old = df_temp
        df_temp = df_temp_old.dropna()
        #df_temp = df_temp.resample('30Min').fillna('nearest') # temp often logged e.g. 22sec -> resample on full min, take nearest value
        #df_prec = df_prec.asfreq('5Min')
    
        
        # handle problem of 1mm per count instead of 0.2mm per count
        most_frequent = df_prec["Precipitation"].value_counts().index.tolist()
        if len(most_frequent) >1 and most_frequent[1] != 0.2:
            df_prec = df_prec * 0.2
            print("Precipitation data multiplied by 0.2 in case of " + current_file)
        
        # plot files that are added
        plt.plot(df_temp.index, df_temp.Temperature)
        plt.title(current_file + " Temp PART")
        plt.xticks(rotation = 45)
        plt.show()
        
        plt.plot(df_prec.index, df_prec.Precipitation)
        plt.title(current_file + " Prec PART")
        plt.xticks(rotation = 45)
        plt.show()
        
        # load file with merged data
        data_temp_old = pd.read_csv(targetpath + "/" + current_file + "_Temperature.csv")
        data_prec_old = pd.read_csv(targetpath + "/" + current_file + "_Precipitation.csv")
        
        # set index col as datetime 
        data_temp_old["DateTimeUTC"] = pd.to_datetime(data_temp_old["DateTimeUTC"])
        data_temp_old.set_index("DateTimeUTC", inplace = True)
        data_prec_old["DateTimeUTC"] = pd.to_datetime(data_prec_old["DateTimeUTC"])
        data_prec_old.set_index("DateTimeUTC", inplace = True)
        
        # concatenate (= append) current file to merged data
        data_temp_new = pd.concat([data_temp_old, df_temp]).sort_index()
        data_prec_new = pd.concat([data_prec_old, df_prec]).sort_index()
        
        #Check for index duplicates and remove them 
        dup_temp = data_temp_new.index.duplicated(keep = 'last').sum() # keep second in case something was improved 
        if dup_temp > 0:
            print(dup_temp, " duplicates in index of " + current_file + "Temperature Timeseries" )
            data_temp_new = data_temp_new[~data_temp_new.index.duplicated(keep ='first')] # remove rows with duplicates in index
            
        dup_prec = data_prec_new.index.duplicated(keep = 'first').sum()
        if dup_prec > 0:
            print(dup_prec, " duplicates in index of " + current_file + "Precipitation Timeseries" )
            data_prec_new = data_prec_new[~data_prec_new.index.duplicated(keep ='first')] # remove rows with duplicates in index
        
        # Plot merged datasets
        plt.plot(data_temp_new.index, data_temp_new.Temperature, ".")
        plt.title(current_file + " Temp ALL")
        plt.xticks(rotation = 45)
        plt.show()
        
        plt.plot(data_prec_new.index, data_prec_new.Precipitation)
        plt.title(current_file + " Prec ALL")
        plt.xticks(rotation = 45)
        plt.show()
        
        
        # safe newly merged data (overwrite old csv file)
        data_prec_new.to_csv(targetpath + "/" + current_file +"_Precipitation.csv", na_rep = "NaN")
        data_temp_new.to_csv(targetpath + "/" + current_file +"_Temperature.csv", na_rep = "NaN")
        
        print(current_file+" looks good")
    
    except:
        print("> Exception: Probably no "+ current_file + " file in the folder or some issues with header")




# %% Manually overwrite/change stuff in merged files:

# # Replace precipitation data from certain file with nan in the data_final file
# site_to_replace = filenames[3]
# print(site_to_replace)
# df_faulty_file = 


    
