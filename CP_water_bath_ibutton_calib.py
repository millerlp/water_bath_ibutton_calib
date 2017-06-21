'''
Run a temperature ramp on a Cole-Parmer Digital Polystat water bath (blue) over
RS232. The routine will stop at each temperature in the array 'calib_temps' for
10 minutes, then move on to the next. It will save the timestamps of the
timepoints when each calibration temperature is achieved into a csv file.

Set ibuttons to record a temperature every minute.

Created on Nov 13, 2013

@author: Luke Miller
'''

import time
import serial # from http://pyserial.sourceforge.net/pyserial.html
              # beginner's install instructions for Windows here:
              # http://learn.adafruit.com/arduino-lesson-17-email-sending-movement-detector/installing-python-and-pyserial
import re
import sys # for user input
import os # for checking file paths
import csv # for writing csv output

# Create a vector of temperatures that the calibration ramp will stop at.
calib_temps = [6,10,15,20,25,30,35,40]

# Establish serial communications with the water bath. Cole-Parmer instructions
# recommend 57600 baud, 8-N-1, no flow control. No linefeeds (\n) should be
# used in the communications with the water bath, only carriage returns (\r). 
# Useful commands for the water bath: 
# RS = get current setpoint temperature
# RT = get current internal bath temperature
# SSxxx.xx\r = change bath setpoint (i.e. SS025.50, units of degrees Celsius)
# SE1 = turn on command echo. It seems counterintuitive, but this seems to be
#         necessary for this script to run.

# Begin by establishing a serial connection with the bath. The entry COM1 below
# will need to be changed to suit your specific serial port name. On a Mac this
# will be something like dev/tty.usbserial-xxxxxxx, on Windows it will be a
# COM port like COM1. 
try: 
    bath = serial.Serial(
                         'COM1',
                         baudrate = 57600,
                         timeout = 1)
    print "***********************************"
    print "Serial connection established on "
    print bath.name # print port info
    print "***********************************"
    time.sleep(2)
    bath.write("SE1\r") # turn on command echo
    response = bath.readline() # always read the response to clear the buffer
    #print "SE0 response: %s" % response
    bath.write("RT\r")
    response = float(bath.readline())
    print "Current bath temperature: %2.2f C" % response
    bath.write("RS\r")
    response = float(bath.readline())
    print "Current bath setpoint: %2.2f C" % response
    continue_flag = True
except:
    print "++++++++++++++++++++++++++"
    print "Serial connection failed"
    print "++++++++++++++++++++++++++"
    time.sleep(5)
    continue_flag = False
    
print "+++++++++++++++++++++++++++++"
print "Ramp will start at 6C"
print "+++++++++++++++++++++++++++++"

# The first step will be to set the initial temperature on the water  
        # bath and wait around until it reaches that temperature.
flag = False  # set the while-loop flag
init_temp = 6 # define the initial temperature, degrees Celsius

while flag != True:
    print "Setting initial temperature: %2.2f C" % init_temp
    # Assemble the command to send to the water bath
    command = "SS0" + "%2.2f\r" % init_temp 
    bath.write(command)
    response = bath.readline()  # always read the response to clear 
                                # the buffer
    time.sleep(0.01)
    # Now check that the set point worked
    bath.write("RS\r")
    response = float(bath.readline())
    if response == init_temp:
        print "Setpoint set: %2.2f C" % response
        flag = True  # set True to kill while loop
            
# Next we need to wait around for the water bath to get to the initial 
# temperature.         
flag = False  # reset test flag
while flag != True:
    time.sleep(5)
    bath.write("RT\r")  # request current bath internal temperature
    response = float(bath.readline())
    print "Current bath temp: %2.2f C" % response
    # When the bath temperature gets within 0.05 of the target, we're 
    # close enough
    if (abs(init_temp - response) < 0.05):
        flag = True  # set True to kill while loop
# The script will now hold at the initial temperature until the user 
# tells it to begin ramping the temperature to the target_temp.
print "****************************************************"
print "****************************************************"
print "Initial temperature reached"
print ""
print "Starting temperature ramp"
print "****************************************************"

################################################################################
# open a csv file to output the temperatures and time stamps
fname = "iButton_calib_times_" + time.strftime("%Y%m%d_%H%M",time.localtime()) + ".csv"
    
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
    command = "SS0" + "%2.2f\r" % current_set # assemble command
    bath.write(command) # change set point
    response = bath.readline() # clear buffer response from bath
    
    flag = False # set initial flag
    while flag != True:
        time.sleep(2)
        bath.write("RT\r")  # request current bath internal temperature
        response = float(bath.readline())
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
         
    
    

