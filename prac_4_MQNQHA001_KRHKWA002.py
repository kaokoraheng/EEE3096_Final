###########################################################################################
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

def timeHere(timein):  #returns the correct time (SA)
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

