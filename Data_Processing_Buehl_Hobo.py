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
current_folder = "07_09_21"
mypath = "D:/Dokumente/Studium/KIT2/HIWI/Data_Buehl/Daten-2021/" + current_folder
targetpath = "D:/Dokumente/Studium/KIT2/HIWI/Data_Final/HoBo_Rain_Gauges"

filenames = ["Sternenberg", "Winterberg", "Sportplatz", "Schönbrunn", "Schwabenquelle", 
                         "Hundseck", "Grundigklinik", "Schafhof", "Butschenberg"]  # Schwabenquelle sometimes called Schwabenbrunnen
measured = ["Temperature", "Precipitation"] # Temperature [°C] and Precipitation [0.2mm increments per 5 min] 
headers = ["Temp", "Niederschlag"]

# Dicts with warnings -> add a waring like clogged, broken, snow, etc. for the imported file instead of NaN in case there was sth. conspicious
warnings_prec = {"Sternenberg":"NaN", "Winterberg":"NaN", "Sportplatz":"NaN", "Schönbrunn":"NaN", "Schwabenquelle":"NaN", 
                         "Hundseck":"NaN", "Grundigklinik":"NaN", "Schafhof":"NaN", "Butschenberg":"NaN"}
warnings_temp = {"Sternenberg":"NaN", "Winterberg":"NaN", "Sportplatz":"NaN", "Schönbrunn":"NaN", "Schwabenquelle":"NaN", 
                         "Hundseck":"NaN", "Grundigklinik":"NaN", "Schafhof":"NaN", "Butschenberg":"NaN"}

# %% Loop over files  
for current_file in filenames: # loop through files in folder
    try:
        # current_file =  filenames[2] # for debugging
        df = pd.read_csv(mypath +"/" +current_file + ".csv", skiprows = 1)  # read csv file (second row with headers)
        
        #Deal with different datetimeformats in the hobo files:
        time_col = ''.join([col for col in df.columns if "Date" in col])      # search for rows that contain data of interest -> ''.join() to store as string instead of list
        
        #There are two different datetime formats -> use to_datetime with both to create two Series and if it does not apply fill with NaN (erros = coerce)
        #Then merge the two dfs   
        date1 = pd.to_datetime(df[time_col], format="%m/%d/%y %I:%M:%S %p", errors='coerce')
        date2 = pd.to_datetime(df[time_col], format="%m/%d/%Y %H:%M", errors='coerce')
        date3 = pd.to_datetime(df[time_col], format="%d/%m/%y %H:%M:%S", errors='coerce')
        date12 = date1.combine_first(date2)
        df[time_col] = date12.combine_first(date3)
        df.set_index(time_col, inplace = True)
        df.index.names = ["DateTimeUTC"]
        
        for parameter,i in zip(measured, range(len(measured))): # loop through parameters in file 
        
            dat_col = [col for col in df.columns if headers[i] in col]
            df2 = df[dat_col]
            df2.columns = ["DataValue"]
            
            if parameter == "Precipitation":   # mulitply prec data with 0.2 in case one gauge tip was set to be 1mm 
                most_frequent = df2["DataValue"].value_counts().index.tolist()
                if len(most_frequent) >1 and most_frequent[1] != 0.2:
                    df2 = df2 * 0.2
                    print(">Precipitation data multiplied by 0.2 in case of " + current_file)
            
            #PLOT new Data
            if parameter == "Precipitation":
                col = "b"
            else:
                col = "r"
                
            plt.plot(df2.index, df2.DataValue, ".", c = col, ms = 0.5)
            plt.title(current_file + parameter + " PART")
            plt.xticks(rotation = 45)
            plt.show()
            
            # Add Warning column and manually fill with warnings if necessary
            header_list = ["DataValue", "Warning"]
            df2 = df2.reindex(columns = header_list)
            if parameter == "Precipitation":
                df2.Warning = warnings_prec[current_file]    # NaN if there is no warning
            else:
                df2.Warning = warnings_temp[current_file]
            
            
            
            # Load old, already merged data
            data_old = pd.read_csv(targetpath + "/" + current_file + "_" + parameter + ".csv")
            data_old["DateTimeUTC"] = pd.to_datetime(data_old["DateTimeUTC"])
            data_old.set_index("DateTimeUTC", inplace = True)
        
            # concatenate (= append) current file to merged data
            data_new = pd.concat([data_old, df2])   # do not sort after index just yet, but after kicking out duplicates,
                                                    # this way, keeping the last occurence will only keep the new data    


            
            #Check for index duplicates and remove them 
            dup = data_new.index.duplicated().sum() 
            if dup > 0:
                print(">",dup, " duplicates in index of " + current_file + parameter )
                data_new = data_new[~data_new.index.duplicated(keep = 'last')] # remove rows with duplicates in index
                #first -> keep first occurence, last -> keep last occurence, False -> keep none
            
            data_new = data_new.dropna(subset = ["DataValue"])  # drop row if NaN in DataValue column
            data_new.sort_index(inplace = True)                 # sort after datetimeindex
             
            
            # PLOT merged data
            plt.plot(data_new.index, data_new.DataValue, ".",  c = col, ms = 0.5)
            plt.title(current_file + measured[i] + " ALL")
            plt.xticks(rotation = 45)
            plt.show()
            
            # safe newly merged data (overwrite old csv file) -----------------------------------------------------
            data_new.to_csv(targetpath + "/" + current_file + "_" + parameter + ".csv", na_rep = "NaN")
        
        print( current_file + " looks good")
            
    except:
        print(">>> Exception: Probably no "+ current_file + " file in the folder or some issues with header <<<")
        
