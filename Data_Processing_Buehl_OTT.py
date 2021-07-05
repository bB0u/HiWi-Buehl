# -*- coding: utf-8 -*-
"""

HiWi Buehl Data Processing OTT pressure transducer

Tasks: 
    - Read out raw csv files from several folders 
    - split csv files for every sensor (in precipitation and temperature for instance)
    - combine csv files for every sensor over whole time 
    - manually replace measured values for certain time ranges with NaN if field log shows irregularities  
    - at the end create some plots and check for gaps/ extreme values 
Created on Tue Jun 29/06/21

@author: Alexander Magerl
"""

#%% load required packages
import pandas as pd
import matplotlib.pyplot as plt 
from re import search
import re
import os
import glob

# %% Set path -> add data folder wise, one folder usually contains the data from one field trip 
current_folder = "05_08_21" # watch out for - or _ !!!
mypath = 'D:/Dokumente/Studium/KIT2/HIWI/Data_Buehl/Daten-2021/' + current_folder # Adjust Folder with Year
targetpath = "D:/Dokumente/Studium/KIT2/HIWI/Data_Final/Ott_Water_Level"

#a Search for filename, the first 16 symbols stay the same, the last 8 change and indicate the date

mypath_search = os.path.join(mypath, '*')

file = []
file = glob.glob(mypath + "/0000303452 0001*") # water level
file.append(glob.glob(mypath + "/0000303452 0002*")) # temperature
file.append(glob.glob(mypath + "/0000303452 0004*"))  # electric conductivity

measured = ["wl", "temp", "ec"]


# %% Loop over files 

for current_file,i in zip(file, range(len(file))):
    try:
        # i = 0 #debug
        # current_file = file[i] #debug
        current_file = ''.join(current_file) # convert from list to string
        df = pd.read_csv(current_file, sep = ';', header = None, names = ['Date', 'Time', 'DataValue'])
        df['DateTimeUTC'] = pd.to_datetime(df['Date'] + " " + df['Time'], format = "%d.%m.%Y %H:%M") # join Date and Time column to one datetimecolumn
        df = df.drop(['Date', 'Time'],1)
        df.set_index('DateTimeUTC', inplace = True)
        
        #remove rows with "---" entries
        df = df[df.DataValue != "---"]
        
        # convert df DataValue column from object to numeric, otherwise problems with plotting
        df = df.apply(pd.to_numeric, errors='coerce')
        
        # Add Warning column and manually fill with warnings if necessary
        header_list = ["DataValue", "Warning"]
        df = df.reindex(columns = header_list)
        df.Warning = "NaN"    # NaN if there is no warning


        
        # Plot New Data
        plt.plot(df.index, df.DataValue, ".", ms = 0.5)
        plt.title(measured[i] + " PART")
        plt.xticks(rotation = 45)
        plt.show()
        
        # load file with merged data 
        data_old = pd.read_csv(targetpath + "/Schwabenquelle_Ott_" + measured[i] + ".csv")
        data_old["DateTimeUTC"] = pd.to_datetime(data_old["DateTimeUTC"])
        data_old.set_index("DateTimeUTC", inplace = True)
        
        # concatenate (= append) current file to merged data
        data_new = pd.concat([data_old, df]).sort_index()
        
        
        # # Plot complete Datasets
        plt.plot(data_new.index, data_new.DataValue, ".", ms = 0.5)
        plt.title(measured[i] + " ALL")
        plt.xticks(rotation = 45)
        plt.show()
        
        #Check for index duplicates and remove them 
        dup = data_new.index.duplicated().sum() 
        if dup > 0:
            print(dup, " duplicates in index of " + measured[i] )
            data_new = data_new[~data_new.index.duplicated(keep = 'last')] # remove rows with duplicates in index
            #first -> keep first occurence, last -> keep last occurence, False -> keep none
            
        # safe newly merged data (overwrite old csv file) -----------------------------------------------------
        data_new.to_csv(targetpath + "/Schwabenquelle_Ott_" + measured[i] +".csv", na_rep = "NaN")
        
        print( measured[i] + " looks good")
        
    except:
        print("> Exception: Probably no "+ measured[i] + " file in the folder -> check filenames")
    
