# -*- coding: utf-8 -*-
"""

HiWi Buehl Data Processing TruTrack WT-HR

Tasks: 
    - Read out raw csv files from several folders 
    - split csv files for every sensor (in precipitation and temperature for instance)
    - combine csv files for every sensor over whole time 
    - manually replace measured values for certain time ranges with NaN if field log shows irregularities
    - manually add warnings in case the field log shows non severe irregularities
    - at the end create some plots and check for gaps/ extreme values 
Created on Tue Jun 29/06/21

@author: Alexander Magerl
"""

#%% load required packages
import pandas as pd
import matplotlib.pyplot as plt 
from re import search
import glob

# %% Set path -> add data folder wise, one folder usually contains the data from one field trip 
current_folder = "01-25-18" # Change to folder with data to add
file_type = ".xlsx" # the data has been exported as xlsx or csv, manually choose which one here
mypath = "D:/Dokumente/Studium/KIT2/HIWI/Data_Buehl/Daten-2018/" + current_folder # Adjust Folder with Year
targetpath = "D:/Dokumente/Studium/KIT2/HIWI/Data_Final/TruTrack_Water_Level"

# The files have to be named exactly like that and in .csv format
filenames = ["TruTrack_Schafhof", "TruTrack_Sprengquellen_OS", "TruTrack_Sprengquellen_ON"] 
measured = ["water_temp", "logger_temp", "water_height"] #  water temperature, logger temperature, water level
headers_xlsx = ["Water Temp", "Logger Temp", "Water Height"] # Original Headers from xlsx file
headers_csv = ["wtemp_p_1", "ltemp_p_2", "wtrhgt__3"] # Original Headers from csv file

# Logger IDs:   -Schafhof:          1207299
#               -Sprengquellen_ON:  1207285
#               -Sprenquellen_OS:   1207298

# %% Loop over files 
    
for current_file in filenames:
    try:
        
        #current_file = filenames[i] #debug
        
        # For Dataimport differentiate between csv and xlsx files (different header)
        if file_type == ".xlsx":
            file = []
            file = glob.glob(mypath +"/" +current_file + "*.xlsx")
            df = pd.read_excel(file[0], skiprows = [0,1,2,3,4,5,6,7,8,10,11])
            df["Date Time"] = pd.to_datetime(df["Date Time"],  format = "%d/%m/%Y %H:%M:%S") 
            df.set_index('Date Time', inplace = True)
            df.index.names = ["DateTimeUTC"]
            df = df.drop("Sample",1)
            
            
        elif file_type == ".csv":
            file = []
            file = glob.glob(mypath +"/" +current_file + "*.CSV")
            df = pd.read_csv(file[0])
            df["datetime"] = pd.to_datetime(df["datetime"],  format = "%d/%m/%Y %H:%M:%S") 
            df.set_index('datetime', inplace = True)
            df.index.names = ["DateTimeUTC"]
            df = df.drop("sample",1)    
    
        for parameter,i in zip(measured, range(len(measured))):
            # order in df should be Water Temp, Logger Temp, Water Height
            
            # new daataframe with only one parameter:
            df2 = df.iloc[:,[i]].copy()
            df2.columns = ["DataValue"]
            df2 = df2.apply(lambda x: pd.to_numeric(x, errors='coerce')).dropna() #drop rows containing strings
            
            #PLOT new data
            plt.plot(df2.index, df2.DataValue, ".", ms = 0.5)
            plt.title(current_file + measured[i] + " PART")
            plt.xticks(rotation = 45)
            plt.show()
            
            # Add Warning column and manually fill with warnings if necessary
            header_list = ["DataValue", "Warning"]
            df2 = df2.reindex(columns = header_list)
            df2.Warning = "NaN"    # NaN if there is no warning
            
            # Load old, already merged data
            data_old = pd.read_csv(targetpath + "/" + current_file + "_" + measured[i] + ".csv")
            data_old["DateTimeUTC"] = pd.to_datetime(data_old["DateTimeUTC"])
            data_old.set_index("DateTimeUTC", inplace = True)
        
            # concatenate (= append) current file to merged data
            data_new = pd.concat([data_old, df2]).sort_index()
            
            # PLOT merged data
            plt.plot(data_new.index, data_new.DataValue, ".", ms = 0.5)
            plt.title(current_file + measured[i] + " ALL")
            plt.xticks(rotation = 45)
            plt.show()
            
            #Check for index duplicates and remove them 
            dup = data_new.index.duplicated().sum() 
            if dup > 0:
                print(dup, " duplicates in index of " + measured[i] )
                data_new = data_new[~data_new.index.duplicated(keep = 'last')] # remove rows with duplicates in index
                #first -> keep first occurence, last -> keep last occurence, False -> keep none
                
            data_new = data_new.dropna(subset = ["DataValue"])  # drop row if NaN in DataValue column
            data_new.sort_index(inplace = True)                 # sort after datetimeindex
            
            # safe newly merged data (overwrite old csv file) -----------------------------------------------------
            data_new.to_csv(targetpath + "/" + current_file + "_" + measured[i] + ".csv", na_rep = "NaN")
        
        print( current_file + " looks good")
        
    except: 
        print("> Exception: Probably no " + current_file + file_type + " file in the folder -> check filenames (.xlsx or .csv?)<")


            
            
      
