"""
Created on Mon May 13 17:46:12 2024

@author: hemesath
"""

import os
import json
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

from cap import ncdt6500_get_data, ncdt6500_decode
import ne1000





class SemiManualCollection:

    def __init__(self):
        self.AXES = ['1', '2', '3', '4']

        self.internal_water_level_control = False
        if self.internal_water_level_control:
            self.TCP_ADDRESS = '169.254.168.150'
            self.PORT = 'COM5'
            self.ADDRESS = 1
            self.DIA = 38

            self.dev = ne1000.Ne1000Serial(self.PORT)
            self.volume = ne1000.Ne1000Volume(2, 'ml')
            self.rate = ne1000.Ne1000Rate(10, 'MM')

        pygame.init()
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        pygame.event.get()

        # Create an instance of the controller
        self.mycon = LeicaMicrotomeController()
        # Get Part ID
        print("Getting Part ID...")
        part_id = self.mycon.get_part_id()

        print("Setting cutting thickness to 500 nm...")
        self.td = 500
        self.set_cutting_thickness()

        print("Setting cutting speed to 0.8mm/s...")
        self.sd = 800


        #Set stage positions
        if os.path.isfile('stage_posS.json'):
            with open('stage_posS.json', 'r') as f:
                stage_posS = json.load(f)
            self.start_pos = stage_posS['start_pos']
            self.stage_pos = self.start_pos
            self.pickup_pos_xy = stage_posS['pickup_pos_xy']
            self.pickup_pos_z = stage_posS['pickup_pos_z']
            self.dropoff_pos_xy = stage_posS['dropoff_pos_xy']
            self.dropoff_pos_z = stage_posS['dropoff_pos_z']
        else:
            self.start_pos = [112, 64, 115, 140]
            self.stage_pos = self.start_pos
            self.pickup_pos_xy = [112, 64]
            self.pickup_pos_z = 122
            self.dropoff_pos_xy = [60, 66]
            self.dropoff_pos_z = 115

        self.main_menu()
        
    def main_menu(self):
        print('\n\n######################\n\nMain Menu\n\n######################\n\n')
        print('1) Start collection with Robot\n')
        print('2) Change cutting thickness\n')
        print('3) Change cutting speed\n')
        print('4) Change wafer position\n')

        c = input('\nChoose an option:\n')

        if c == '1':
            self.robot_collection()
        elif c == '2':
            try:
                td = input('\nEnter cutting thickness in nm:\n')
                self.td = int(td)
                self.set_cutting_thickness()
            except ValueError:
                print('An error occurred: Cutting thickness could not be changed')
                input()
                self.main_menu()
        elif c == '3':
            try:
                sd = input('\nEnter cutting cutting speed in um/s:\n')
                self.sd = int(sd)
                self.set_cutting_speed()
            except ValueError:
                print('An error occurred: Cutting speed could not be changed')
                input()
                self.main_menu()
        elif c == '4':
            try:
                sp = input('\nEnter position of wafer stage in mm:\n')
                self.stage_pos[3] = int(sp)
            except ValueError:
                print('An error occurred: Wafer position could not be changed')
                input()
                self.main_menu()

    def set_cutting_thickness(self):
        th = hex(self.td).split('x')[-1]
        th1 = '0000' + th
        self.mycon.set_feedrate(th1[-4:])
        thickness = self.mycon.get_feedrate()  # Get current thickness
        print(f"Current cutting thickness: {int(thickness[7:11], 16)}nm")

    def set_cutting_speed(self):
        sh = hex(self.sd).split('x')[-1]
        sh1 = '0000' + sh
        self.mycon.set_cutting_speed(sh1[-4:])
        speed = self.mycon.get_cutting_speed()  # Get current speed
        print(f"Current cutting speed: {int(speed[7:11], 16)}um/s")

    def robot_collection(self):
        with GCSDevice() as pidevice:
            pidevice.ConnectUSB(serialnum="120060503")
            print('connected: {:s}'.format(pidevice.qIDN().strip()))
            pidevice.MOV(1, self.stage_pos[0])
            pidevice.MOV(2, self.stage_pos[1])
            pidevice.MOV(3, self.stage_pos[2])
            pidevice.MOV(4, self.stage_pos[3])

            while True:
                ##### Cut the slice 
                print("Turn motor on...")
                motor_on = self.mycon.cutting_motor_on()
                motor_status = self.mycon.cutting_motor_status()
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
                    current_state = self.mycon.get_handwheel_position()[7:9]
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
                motor_off = self.mycon.cutting_motor_off()
                motor_status = self.mycon.cutting_motor_status()
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
                
                if self.internal_water_level_control:
                    self.water_level_control()

                # Adjust pickup point
                self.pickup_pos_xy[0], self.pickup_pos_xy[1], temp_pos_z, end_collection = move_joystick(pidevice, self.joystick)
                if end_collection:
                    pygame.joystick.quit()
                    pidevice.CloseConnection()
                    self.save_stage_pos()
                    self.mycon.close()
                    print("Connection closed.")
                    break
                if temp_pos_z > 0:
                    self.pickup_pos_z = temp_pos_z
                # Pick section up (lowing the tip)
                pidevice.MOV(3, self.pickup_pos_z)
                sleep(1)
                # Move section to wafer boat
                pidevice.MOV(1, self.dropoff_pos_xy[0])
                pidevice.MOV(2, self.dropoff_pos_xy[1])
                sleep(10)
                # Move section to wafer with joystick
                _, _, _,end_collection = move_joystick(pidevice, self.joystick)
                if end_collection:
                    pygame.joystick.quit()
                    pidevice.CloseConnection()
                    self.mycon.close()
                    print("Connection closed.")
                    break
                # Lift tip
                pidevice.MOV(3, self.dropoff_pos_z)
                sleep(1)
                # Move arm back to pickup point
                pidevice.MOV(1, self.pickup_pos_xy[0])
                pidevice.MOV(2, self.pickup_pos_xy[1])

    def calibrate_cap_sensor(self):
        cap_reading = input('Please adjust the water level and the Z position of the cap sensor.\nThen enter the output of the cap sensor (in percent) to calibrate the reading:\n')
        x = int(cap_reading)
        y = x * 0.1
        self.ue = y + 0.5
        self.ut = y - 0.5
        print(self.ue)
        print(self.ut)

    def water_level_control(self):
        for channel, raw_data in enumerate(ncdt6500_get_data()):
            print(f"channel #{channel}: {ncdt6500_decode(raw_data):.4g} V")
            waterlevel = ncdt6500_decode(raw_data)
        if waterlevel < self.ut - 0.5:
            raise ValueError('Large change in cap sensor reading detected. Please check the cap sensor for water drops.')
        if waterlevel > self.ue:
            pump = ne1000.Ne1000(self.dev, self.ADDRESS)
            pump.diameter_mm(self.DIA)
            pump.volume(self.volume)
            pump.rate(self.rate)
            pump.direction_infuse()
            pump.run()
            time.sleep(10)
    #  if waterlevel < ut:
    #     pump = ne1000.Ne1000(dev, ADDRESS)
    #     pump.diameter_mm(DIA)
        #    pump.volume(volume)
        #    pump.rate(rate)
        #    pump.direction_withdraw()
        #    pump.run()
        #   time.sleep(10)
        elif waterlevel <= self.ue:
            #continue
            time.sleep(0.1)

    def save_stage_pos(self):
        self.start_pos[0] = self.pickup_pos_xy[0]
        self.start_pos[1] = self.pickup_pos_xy[1]
        stage_posF = {'start_pos': self.start_pos,
                      'pickup_pos_xy': self.pickup_pos_xy,
                      'pickup_pos_z': self.pickup_pos_z,
                      'dropoff_pos_xy': self.dropoff_pos_xy,
                      'dropoff_pos_z': self.dropoff_pos_z}
        with open('stage_posS.json', 'w') as f:
            json.dump(stage_posF, f)



if __name__ == '__main__':
    collect = SemiManualCollection()