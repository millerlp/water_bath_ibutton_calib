'''
Run a temperature ramp on a ANOVA A-series water bath (blue) over
RS232. The routine will stop at each temperature in the array 'calib_temps' for
10 minutes, then move on to the next. It will save the timestamps of the
timepoints when each calibration temperature is achieved into a csv file.

Set ibuttons to record a temperature every minute.

Created on June 2017

@author: Luke Miller
'''

import time
import serial # from http://pyserial.sourceforge.net/pyserial.html
              # beginner's install instructions for Windows here:
              # http://learn.adafruit.com/arduino-lesson-17-email-sending-movement-detector/installing-python-and-pyserial
import re # for regular expressions, used to parse water bath responses
import sys # for user input
import os # for checking file paths
import csv # for writing csv output

# Create a vector of temperatures that the calibration ramp will stop at.
calib_temps = [6,10,15,20,25,30,35,40]

# Establish serial communications with the water bath. ANOVA instructions
# recommend 9600 baud, 8-N-1, no flow control. No linefeeds (\n) should be
# used in the communications with the water bath, only carriage returns (\r). 
# Useful commands for the water bath: 

# get temp setting = get current setpoint temperature
# temp = get current internal bath temperature
# set temp xxx.xx = change bath setpoint (i.e. set temp 025.50 = 25.5C units of degrees Celsius)

# Begin by establishing a serial connection with the bath. The entry 
# /dev/ttyUSB0 below
# will need to be changed to suit your specific serial port name. On a Mac this
# will be something like dev/tty.usbserial-xxxxxxx, on Windows it will be a
# COM port like COM1. 

try: 
        bath = serial.Serial(
                         '/dev/ttyUSB0',
                         baudrate = 9600, # ANOVA water bath wants 8-N-1, no flow control
                         timeout = 1)
        print "***********************************"
        print "Serial connection established on "
        print bath.name # print port info
        print "***********************************"
        time.sleep(1)
        bath.write("version\r") # Ask for ANOVA firmware version
        response = bath.readlines() # always read the response to clear the buffer
        print response[0]
        bath.write("temp\r")  # get current bath temperature
        # NOTE: the temp response may need more parsing, since it appears 
        # to come back as ['temp\r 20.10\r']
        response = bath.readlines()
        # Use re.search to pick out the digits (and decimal) from the
        # string response stored in 'res'. The .group() function outputs
        # the result
        response = float(re.search(r'[0-9.]{4,}',response[0]).group())
        print "Current bath temperature: %2.2f C" % response
        bath.write("get temp setting\r")
        # The response will come back in the form ['get temp setting\r 21.00\r']
        response = bath.readlines()    
        # Use re.search to pick out the digits (and decimal) from the
        # string response stored in 'res'. The .group() function outputs
        # the result
        response = float(re.search(r'[0-9.]{4,}',response[0]).group())
        print "Current bath setpoint: %2.2f C" % response
        continue_flag = True
except:
        print "++++++++++++++++++++++++++"
        print "Serial connection failed"
        print "++++++++++++++++++++++++++"
        time.sleep(5)
        continue_flag = False
    
# The first step will be to set the initial temperature on the water  
        # bath and wait around until it reaches that temperature.
flag = False  # set the while-loop flag
init_temp = 5 # define the initial temperature, degrees Celsius

print "+++++++++++++++++++++++++++++"
print "Ramp will start at %1f C" % init_temp
print "+++++++++++++++++++++++++++++"



while flag != True:
    print "Setting initial temperature: %2.2f C" % init_temp
    # Assemble the command to send to the water bath
    command = "set temp " + "%2.2f\r" % init_temp 
    bath.write(command)
    response = bath.readlines()  # always read the response to clear the buffer
    time.sleep(0.01)
    # Now check that the set point worked
    bath.write("get temp setting\r")
    # The response here will need to be parsed to remove the echoed
    # command. It will look like ['get temp setting\r 21.00\r']
    response = float(re.search(r'[0-9.]{4,}',response[0]).group())
    if (abs(response - init_temp) < 0.001):
        print "Setpoint set: %2.2f C" % response
        flag = True  # set True to kill while loop
            
# Next we need to wait around for the water bath to get to the initial 
# temperature.         
flag = False  # reset test flag

while flag != True:
    time.sleep(5)
    bath.write("temp\r")  # request current bath internal temperature
    response = bath.readlines()
    # The response here will need to be parsed to remove the echoed
    # command. It will look like ['temp\r 21.00\r']
    response = float(re.search(r'[0-9.]{4,}',response[0]).group())
    print "Current bath temp: %2.2f C" % response
    # When the bath temperature gets within 0.05 of the target, we're 
    # close enough
    if (abs(init_temp - response) < 0.05):
        flag = True  # set True to kill while loop
# The script will now hold at the initial temperature until the user 
# tells it to begin ramping the temperature to the target_temp.
print "****************************************************"
print "****************************************************"
print "Initial temperature %2.2f C reached" % init_temp
print ""
print "Starting temperature ramp"
print "****************************************************"

################################################################################
# open a csv file to output the temperatures and time stamps
fname = time.strftime("%Y%m%d_%H%M",time.localtime()) + "_iButton_calib_times" +  + ".csv"
    
outputfile = open(fname,'wb') # opens file
# Create writer object, use as writer.writerow(data) later on
writer= csv.writer(outputfile, delimiter = ',', dialect = 'excel')
headers = ['TempC','TimePST']
writer.writerow(headers) # write header to output file
# output file is left open so that it can be written to later

################################################################################
# Step through each temperature in the calib_temps array, stopping at each for
# 10 minutes to ensure stable ibutton temperatures. 
for i in range(len(calib_temps)):
    current_set = calib_temps[i] # extract temperature
    command = "set temp " + "%2.2f\r" % current_set # assemble command
    bath.write(command) # change set point
    response = bath.readline() # clear buffer response from bath
    
    flag = False # set initial flag
    while flag != True:
        time.sleep(2)
        bath.write("temp\r") # Query current bath temperature
        response = bath.readlines() # get response
        # Parse the response, which will have a temperature value in it
        # in the form ['temp\r 21.46\r']
        response = float(re.search(r'[0-9.]{4,}',response[0]).group())
        # print "Current bath temp: %2.2f C" % response
        # When the bath temperature gets within 0.05 of the target, we're 
        # close enough
        if (abs(current_set - response) < 0.05):
            flag = True  # set True to kill while loop
    
    # Print time that we reached setpoint
    print "Current bath temp: %2.2f C" % response
    print time.strftime("%H:%M", time.localtime())
    row = [current_set,time.strftime("%Y-%m-%d %H:%M", time.localtime())]
    writer.writerow(row) # write temp and time to csv output file
    # Now sleep for ten minutes
    time.sleep(600)
    
    # After ten minutes, go to the next step of the for loop to move to a new 
    # temperature

print "Finished"
print time.strftime("%H:%M", time.localtime())

outputfile.close() # close the output file. 
dirname = os.getcwd() # get current working directory        
print "Timestamps saved to %s\%s" % (dirname,fname)         
         
junk = raw_input("Press return to quit")
bath.close()         
         
    
    

