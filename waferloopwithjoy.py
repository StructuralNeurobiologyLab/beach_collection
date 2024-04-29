# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 18:38:29 2024

@author: laura
"""
from pipython import GCSDevice
from pipython.pitools import waitonwalk
from leicame import LeicaMicrotomeController
import serial
import time
from time import sleep
from Wafer_sim import square
from debug_joystick import move_joystick
import time

from pipython import GCSDevice
from pipython.pitools import waitonwalk
from time import sleep
import pygame

pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()
pygame.event.get()


####### Initialisation
# Get the waifer positions (h, y)
positions = square(width=30, length=55, standoff=5)
print(positions)

# Create an instance of the controller
mycon = LeicaMicrotomeController()
# Get Part ID
print("Getting Part ID...")
part_id = mycon.get_part_id()

print("Setting cutting thickness to 500 nm...")
td = 500
th = hex(td).split('x')[-1]
th1 = '0000' + th
mycon.set_feedrate(th1[-4:])
thickness = mycon.get_feedrate()  # Get current thickness
print(f"Current cutting thickness: {int(thickness[7:11], 16)}nm")

print("Setting cutting speed to 0.8mm/s...")
sd = 800
sh = hex(sd).split('x')[-1]
sh1 = '0000' + sh
mycon.set_cutting_speed(sh1[-4:])
speed = mycon.get_cutting_speed()  # Get current speed
print(f"Current cutting speed: {int(speed[7:11], 16)}um/s")

AXES = ['1', '2', '3', '4']
MVR_STEPSIZE = 10
SETTLING_TIME = 0.5

with GCSDevice() as pidevice:
    pidevice.ConnectUSB(serialnum="120060503")
    print('connected: {:s}'.format(pidevice.qIDN().strip()))
    for axis in AXES:
        pidevice.MOV(1, 112)
        pidevice.MOV(2, 75)
        pidevice.MOV(3, 110)
        pidevice.MOV(4, 140)

    ######## Main Loop
    for h, y in positions:

        ##### Cut the slice 
        print("Turn motor on...")
        motor_on = mycon.cutting_motor_on()
        motor_status = mycon.cutting_motor_status()
        if motor_status[7:9] == b'01':
            print("it's on")
        elif motor_status[7:9] == b'00':
            print("it's off")
            break
        elif motor_status[7:9] == b'E0':
            print("invalid callabration")
            break
        else:
            print("invalid response")
            break

        cut_finished = False
        was_in_cutting_window = False
        while not cut_finished:
            current_state = mycon.get_handwheel_position()[7:9]
 #           print(time.time())
            print(current_state)
            if current_state == b"03":
                was_in_cutting_window = True
            elif current_state == b"00" and was_in_cutting_window:
                cut_finished = True
                print("cut finished")
                break
                # continue
            # time.sleep(0.1)

        print("Turn motor off...")
        motor_off = mycon.cutting_motor_off()
        motor_status = mycon.cutting_motor_status()
        if motor_status[7:9] == b'01':
            print("it's on")
            break
        elif motor_status[7:9] == b'00':
            print("it's off")
        elif motor_status[7:9] == b'E0':
            print("invalid callabration")
            break
        else:
            print("invalid response")
            break

        move_joystick(pidevice, joystick)

        ####### Move the slice to wafer
        for axis in AXES:
            pidevice.MOV(3, 122)  # tip down
        sleep(1)
        for axis in AXES:  # move to transition wafer boat
            pidevice.MOV(1, 60)
            pidevice.MOV(2, 75)
        sleep(10)
        for axis in AXES:  # move onto specified wafer position
            pidevice.MOV(1, 27)
            pidevice.MOV(2, y)
            pidevice.MOV(4, h-15)
        sleep(5)
        for axis in AXES:  # move tip up
            pidevice.MOV(3, 110)
        sleep(1)
        for axis in AXES:  # return to pick- up point
            pidevice.MOV(1, 112)
            pidevice.MOV(2, 75)
        sleep(15)

    for axis in AXES:  # return to pick- up point
        time.sleep(20)
        pidevice.MOV(4, 0)

########## Finishing
pygame.joystick.quit()
pidevice.CloseConnection()
mycon.close()
print("Connection closed.")
