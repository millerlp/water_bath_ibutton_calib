water_bath_ibutton_calib

--------------

This repo contains python scripts that can be used to control an 
ANOVA A-series digital water bath or older Cole-Parmer Polystat
water baths (early 2000's models with a blue base, not modern 2010's 
models). 

`ANOVA_water_bath_ibutton_calib.py` should work with modern
A-series water baths from http://www.waterbaths.com

`water_bath_ibutton_calib.py` should work with old Cole-Parmer Polystat
waterbaths from the early 2000's. 

The scripts will set the water bath to a low starting temperature and
then raise the temperature in 5C steps, with a 10 minute pause at
each new temperature. This should allow temperature sensors such as
thermocouples or iButton dataloggers to record several readings at a 
stable, known temperature, to allow calibration (assuming you have an 
accurate temperature measuring device to verify that your water bath 
temperatures are accurate). 

Requires the use of the `pyserial` package. Written for Python 2.7.