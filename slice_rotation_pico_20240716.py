# JSON example  {"direction": "left", "freq": 1, "degree":400}

#tiny stepper:microsteps 1;min speed 8 current about 200mA

import sys
import machine
import utime
import select
import json

from machine import Pin



#data = {"direction" : "left", "freq" : 0, "degree" : 0}
data = {"direction" : "left", "freq" : 1, "degree":400}


STP_PIN = 7  # GPIO number where step pin is connected
DIR_PIN = 6   # GPIO number where dir pin is connected
RST_PIN = 9
SLP_PIN = 8

STP = machine.Pin(STP_PIN, machine.Pin.OUT,machine.Pin.PULL_DOWN)
DIR = machine.Pin(DIR_PIN, machine.Pin.OUT)
RST = machine.Pin(RST_PIN, machine.Pin.OUT)
SLP = machine.Pin(SLP_PIN, machine.Pin.OUT)

STP.value(0)

MOD0 = machine.Pin(12, machine.Pin.OUT) 
MOD1 = machine.Pin(11, machine.Pin.OUT) 
MOD2 = machine.Pin(10, machine.Pin.OUT)

microsteps = 1

def stepping(steps):

    if steps == 1:
        MOD0.value(0)
        MOD1.value(0)
        MOD2.value(0)
    elif steps == 4:
        MOD0.value(0)
        MOD1.value(1)
        MOD2.value(0)
    elif steps == 8:
        MOD0.value(1)
        MOD1.value(1)
        MOD2.value(0)
    elif steps == 16:
        MOD0.value(0)
        MOD1.value(0)
        MOD2.value(1)
    elif steps == 32:
        MOD0.value(1)
        MOD1.value(1)
        MOD2.value(1)
        
stepping(microsteps)

    
def movement(data):
    RST.value(1)
    SLP.value(1)
    
    count =  data["degree"] / 1.8

    if data["freq"] > 0 and data["degree"] > 0:
        while count >= 0:
            STP.value(1)
            utime.sleep((1/data["freq"])/2)
            STP.value(0)
            utime.sleep((1/data["freq"])/2)
            count -=1
            if  poll_obj.poll(0):
             #   sys.stdout.write("nope")
                #print("nope")
                break
            
    RST.value(0)
    SLP.value(0)
        
def direction(data):
    if data["direction"] == 'left':       
        DIR.value(1)
    elif data["direction"] == 'right':
        DIR.value(0)
    else:
        print("Unknown direction")
    
poll_obj = select.poll()
poll_obj.register(sys.stdin, select.POLLIN)

while True:
    if poll_obj.poll(0):
        json_data = sys.stdin.readline().strip()
        if json_data:
            try:
                data = json.loads(json_data)
                sys.stdout.write(json_data)
                if data:
                    direction(data)
                    movement(data)
            except ValueError:
                print("error: invalid JSON string '" + str(json_data) + "'")
    RST.value(0)
    SLP.value(0)
    
    
 
 
  
       
