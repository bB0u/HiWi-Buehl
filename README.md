# HiWi-Buehl
Data Processing for the Hydrological Monitoring Network in the Bühlert catchment operated by KIT.

A google map with the postions of the measuring devices can be found [here](https://www.google.com/maps/d/edit?mid=1ZYPXmtpy7SuYAP1PAG6mhgypOxP9pXSi&usp=sharing).

The data is supposed to be incorporated in the [V-FOR-Water](https://www.vforwater.de/index.php) platform.

The Python Scripts in this repository aim to merge the data collected from several types of loggers.
Data collection usually takes place once a month and is conducted by a HiWi (research assistance).
The types of loggers and the individual loggers are listed here: 

## Rain gauges using OnSet HoBO event logger
- log precipitation in 0.2 mm increments with a 5 min temporal resolution
- temperature as well
- non heated &rightarrow snow is not measured &rightarrow data from winter can be discarded
- prone to clogging 

## Soil Moisture using Campbell Scientific logger
- two stations with two depths each
- log electrical conductivity, volumetric soil moisture and temperature

## OTT Hydromet Pressure Transducer measuring the water level at a spring with Thomson weir (triangular weir)
- logs water level, temperature and electrical conductivty
- weir is not completely teight &rightarrow some of the spring discharge is not captured

## TruTrack WT-HR Water level and temperature logger
- record interflow after strong precipitation events, otherwise they are mostl dry 
