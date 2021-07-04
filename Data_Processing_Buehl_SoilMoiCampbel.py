# -*- coding: utf-8 -*-
"""

HiWi Buehl Data Processing Campbell Scientific Soil Moisture

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

# %% Set path -> add data folder wise, one folder usually contains the data from one field trip 
current_folder = "01-25-18"
mypath = "D:/Dokumente/Studium/KIT2/HIWI/Data_Buehl/Daten-2018/" + current_folder # Adjust Folder with Year
targetpath = "D:/Dokumente/Studium/KIT2/HIWI/Data_Final/Campbell_Soil_Moisture"

# The files have to be named exactly like that and in .csv format (simply copy .dat and change the file extension to .csv)
# EDIT: .dat file can be read directly just like .csv file, no need to copy/rename
# There are two locations (Schafhof1 and 2) with two Sensor heights eache (Table1 and 2)
filenames = ["Schafhof1_Table1", "Schafhof1_Table2", "Schafhof5_Table1", "Schafhof5_Table2"] 
measured = ["vwc", "ec", "temp"]


# %% Loop over files 
    
for current_file in filenames:
    try: 
        #current_file =  filenames[2] # for debugging
        df = pd.read_csv(mypath +"/" +current_file + ".dat", skiprows = [0,2,3])    # read csv file (second row with headers)
        time_col = [col for col in df.columns if "TIMESTAMP" in col]                # search for rows that contain data of interest
        vwc_col =[col for col in df.columns if "VWC_" in col]                    # VWC = Volumetric Water Content [m^3/m^3]
        ec_col =[col for col in df.columns if "EC_" in col]                      # EC = Electric Conducivity [dS/m]
        temp_col =[col for col in df.columns if "T_" in col]                     # T = Temperature in DegC
        
        # convert to datetime and set as datetimeindex

        df[time_col[0]] = pd.to_datetime(df[time_col[0]],  format = "%Y-%m-%d %H:%M:%S")  
        df.set_index(time_col, inplace = True)
        df.index.names = ["DateTimeUTC"] # rename datetimeindex (toughbook should always be set to UTC+0)
        
        # build new dataframe with only columns of interest and Date Time as index 
        df_temp = df[temp_col]
        df_vwc = df[vwc_col]
        df_ec = df[ec_col]
        
        #rename columns to DataValue
        df_temp.columns = ["DataValue"]
        df_vwc.columns = ["DataValue"]
        df_ec.columns = ["DataValue"]
        
        
        
        # plot files that are added -------------------------------------------------------------
        plt.plot(df_temp, "r.", ms = 0.5)
        plt.title(current_file + " Temp PART")
        plt.xticks(rotation = 45)
        plt.show()
        
        plt.plot(df_vwc, "b.", ms = 0.5)
        plt.title(current_file + " VWC PART")
        plt.xticks(rotation = 45)
        plt.show()
        
        plt.plot(df_ec, "g.", ms = 0.5)
        plt.title(current_file + " EC PART")
        plt.xticks(rotation = 45)
        plt.show()
        
        # Add Warning column and in case the field book contains a warning, add it 
        header_list = ["DataValue", "Warning"]
        df_temp = df_temp.reindex(columns = header_list)
        df_vwc = df_vwc.reindex(columns = header_list)
        df_ec = df_ec.reindex(columns = header_list)
        
        # df_temp.loc["Warning"] = "" #  put warning between parenthesis if it applies to whole dataset
        # df_vwc[:,"Warning"] = "" 
        # df_ec[:,"Warning"] = ""
        
        
        
        # load file with merged data -----------------------------------------------------------
        data_temp_old = pd.read_csv(targetpath + "/" + current_file + "_Temp.csv")
        data_vwc_old = pd.read_csv(targetpath + "/" + current_file + "_VWC.csv")
        data_ec_old = pd.read_csv(targetpath + "/" + current_file + "_EC.csv")
    
        
        # set index col as datetime 
        data_temp_old["DateTimeUTC"] = pd.to_datetime(data_temp_old["DateTimeUTC"])
        data_temp_old.set_index("DateTimeUTC", inplace = True)
        data_vwc_old["DateTimeUTC"] = pd.to_datetime(data_vwc_old["DateTimeUTC"])
        data_vwc_old.set_index("DateTimeUTC", inplace = True)
        data_ec_old["DateTimeUTC"] = pd.to_datetime(data_ec_old["DateTimeUTC"])
        data_ec_old.set_index("DateTimeUTC", inplace = True)
        
        # concatenate (= append) current file to merged data
        data_temp_new = pd.concat([data_temp_old, df_temp]).sort_index()
        data_vwc_new = pd.concat([data_vwc_old, df_vwc]).sort_index()
        data_ec_new = pd.concat([data_ec_old, df_ec]).sort_index()
        
        #Check for index duplicates and remove them 
        dup_temp = data_temp_new.index.duplicated(keep = 'first').sum() #first -> keep first occurence, last -> keep last occurence, false -> keep none
        if dup_temp > 0:
            print(dup_temp, " duplicates in index of " + current_file + " Temperature Timeseries" )
            data_temp_new = data_temp_new[~data_temp_new.index.duplicated(keep ='first')] # remove rows with duplicates in index
            
        dup_vwc = data_vwc_new.index.duplicated(keep = 'first').sum()
        if dup_vwc > 0:
            print(dup_vwc, " duplicates in index of " + current_file + " VWC Timeseries" )
            data_vwc_new = data_vwc_new[~data_vwc_new.index.duplicated(keep ='first')] # remove rows with duplicates in index
            
        dup_ec = data_ec_new.index.duplicated(keep = 'first').sum()
        if dup_ec > 0:
            print(dup_ec, " duplicates in index of " + current_file + " ECC Timeseries" )
            data_ec_new = data_ec_new[~data_ec_new.index.duplicated(keep ='first')] # remove rows with duplicates in index
            
        
        # Plot merged datasets ---------------------------------------------------------------
        plt.plot(data_temp_new.index, data_temp_new.DataValue, "r.", ms = 0.5)
        plt.title(current_file + " Temp ALL")
        plt.xticks(rotation = 45)
        plt.show()
        
        plt.plot(data_vwc_new.index, data_vwc_new.DataValue, "b.", ms = 0.5)
        plt.title(current_file + " VWC ALL")
        plt.xticks(rotation = 45)
        plt.show()
        
        plt.plot(data_ec_new.index, data_ec_new.DataValue, "g.", ms = 0.5)
        plt.title(current_file + " EC ALL")
        plt.xticks(rotation = 45)
        plt.show()
        
        # safe newly merged data (overwrite old csv file) -----------------------------------------------------
        data_temp_new.to_csv(targetpath + "/" + current_file +"_Temp.csv", na_rep = "NaN")
        data_vwc_new.to_csv(targetpath + "/" + current_file +"_VWC.csv", na_rep = "NaN")
        data_ec_new.to_csv(targetpath + "/" + current_file +"_EC.csv", na_rep = "NaN")
        
        print(current_file+" looks good")
    
    except:
        print("> Exception: Probably no "+ current_file + " file in the folder or some issues with header")




# %% Manually overwrite/change stuff in merged files:

# # Replace precipitation data from certain file with nan in the data_final file
# site_to_replace = filenames[3]
# print(site_to_replace)
# df_faulty_file = 


    
