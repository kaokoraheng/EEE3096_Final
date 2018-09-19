############################################################################################
#!/usr/bin/python
#IMPORTS
import spidev
import time
import os
import sys
import RPi.GPIO as GPIO

from datetime import datetime

# import only system from os 
from os import system, name

############################################################################################
#Defined Variable
############################################################################################

#channels in which the seonsors are connected
ldr = 0
tempsensor = 1
pot = 2

#Mappings made between the GPIO pins
#and the buttons corresponding to them
reset = 4              
frequency = 17
stop = 27
display = 22


start_time = time.time()  #we will subtract this from the 'current time' to measure elapsed time
go = True  #use this to stop and start monitoring

############################################################################################
#List
############################################################################################

mylist = []
mylist2 = []

############################################################################################

# FUNCTION DEFINITIONS
############################################################################################


# define our clear function for clearing the console
def clear():  
        _ = system('clear')

# function to fetch data from the ADC
def GetData(channel): # channel must be an integer 0-7
   adc = spi.xfer2([1,(8+channel)<<4,0]) # sending 3 bytes
   data = ((adc[1]&3) << 8) + adc[2]
   return data


# function definition: threaded callback
def callback1(reset): #resets timer and clears console
    global start_time
    start_time = time.time()

    clear()

def callback2(frequency):
      global delay
      if delay == 2:
          delay = 0.5
      elif delay == 1:
          delay = 2
      elif delay == 0.5:
          delay = 1

def callback3(stop):
      global go
      if go == True:
          go = False
	  
      else:
          go = True
   
def callback4(display):
      global mylist
      global mylist2
      mylist2 = mylist
      length = len(mylist2)  #length of list
      print("Time           Timer      Pot       Temp      Light")
      if length > 4:
           for i in range(5):
              print(mylist2[length-5+i])
      else:
          for j in range(length):
              print(mylist2[j])

def timeHere(timein):  #returns the correct time
     x = str(timein)
     x = x.split('.')
     pt = datetime.strptime(x[0] ,'%H:%M:%S')
     total_seconds = pt.second+pt.minute*60+pt.hour*3600
     returntimingForm(total_seconds - 2968)

#receives time in seconds and returns it in the format hh:mm:ss    
def timingForm(seconds):
    hours = int(seconds//3600)    #use integer division to get the hours in the total seconds
    hours = '{:02}'.format(hours) #format the hours from the form 1 to 01
    rem1 = seconds%3600      #get the remainder
    minutes = int(rem1//60)       #use integer division to get the minutes in the remaining seconds
    minutes = '{:02}'.format(minutes) #format the minutes from the form 1 to 01
    seconds = int(rem1%60)        #get the mainder, the seconds
    seconds = '{:02}'.format(seconds) #format the seconds from the form 1 to 01
    time = str(hours) + ":" + str(minutes) + ":" + str(seconds) #format
    return time              #return time

# function to convert data to voltage level, # places: number of decimal places needed
def ConvertPotV(data, places):
        volts = (data * 3.3) / float(1023)
        volts = round(volts,places)
        return volts

def ConvertToLDR_V(data, places):
        percent = (data * 100)/float(1023)     #convert the data/light to a percentage
        percent = round(percent, places)       #round the floating point value to places number of decimal places
        return percent                         #return the percentage

def ConvertToTemp(data, places):
        vout = ConvertPotV(data, 2)        #first convert the 10 bit number to a voltage with two decimal places
        temp = ( 100*vout ) - 50            #convert the output voltage to a temperature using the information from the datasheeet
        return temp                         #return the temperature

##############################################################################################################################


GPIO.setmode(GPIO.BCM) #specify numbering system

#Setup the Button Pull Up and Pull Down Resistors 
GPIO.setup(reset, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(frequency, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(stop, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(display, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Cause delays to be percieved
delay = 0.5   #default delay is 500 ms = 0.5 s
           
# Under a rising-edge detection, regardless of current execution # callback function will be called
GPIO.add_event_detect(reset, GPIO.RISING, callback=callback1, bouncetime=200)
GPIO.add_event_detect(frequency, GPIO.RISING, callback=callback2, bouncetime=200)
GPIO.add_event_detect(stop, GPIO.RISING, callback=callback3, bouncetime=200)
GPIO.add_event_detect(display, GPIO.RISING, callback=callback4, bouncetime=200)

spi = spidev.SpiDev() # create spi object
spi.open(0,0)
spi.max_speed_hz = 1000000

try:
    while True:
      
      while go == True:
              
          #Default
          current_time =timeHere(datetime.now().time())  #get the current time
          elapsed_time_in_seconds = time.time() - start_time   #measure elapsed time WCT in seconds
          elapsed_time =timingForm(elapsed_time_in_seconds)   #elapsed time correctly formatted
          
          
          #read the sensors          
          #potentiometer: in channel 2
          pot_data = GetData(2) #10 bits from ADC
          pot_volts = ConvertPotV(pot_data, 2)  #convert to volts to display
          
          #temperature sensor: in channel 1
          temp_data = GetData(1) #10 bits from the ADC
          temp = ConvertToTemp(temp_data, 2) #cnvert to degrees Celsius
          
          #light sensor/LDR: in channel 0
          light_data = GetData(0) #10 bits from the ADC
          light = ConvertToLDR_V(light_data, 2)   #convert to percentage
          
          
          print("Time           Timer      Pot       Temp      Light")
          system_data = current_time  + "    " + str(elapsed_time) + "      " + str(pot_volts) + " V     " + str(temp) + " C     " + str(light) + "%"
          print(system_data)
          
          mylist.append(system_data)
          time.sleep(delay)

except KeyboardInterrupt:
          spi.close()
