"""
Created on Sep 04 16:02:23 2024

@author: hemesath
"""

import os

import json

from debug_joystick import move_joystick
import time

from pipython import GCSDevice

from time import sleep
import pygame

from cap import ncdt6500_get_data, ncdt6500_decode
import ne1000





class SemiManualCollection:

    def __init__(self):

        self.startup_t = int(time.time())
        self.log = 'logs\\' + str(self.startup_t) + '\\'

        os.makedirs(self.log)
        self.cycle_count = 0
        self.write_log()
        self.cycle_count = 0
        self.AXES = ['1', '2', '3', '4']

        self.internal_water_level_control = False
        self.manual_water_refill = False

        self.auto_loop = False
        self.interrupt = True

        self.cutting_stopped = False

        self.save_cam_images = True

        self.flat_angle = True

        if self.internal_water_level_control:
            self.TCP_ADDRESS = '169.254.168.150'
            self.PORT = 'COM5'
            self.ADDRESS = 1
            self.DIA = 38

            self.dev = ne1000.Ne1000Serial(self.PORT)
            self.volume = ne1000.Ne1000Volume(0.8, 'ml')
            self.rate = ne1000.Ne1000Rate(10, 'MM')

            self.pump = ne1000.Ne1000(self.dev, self.ADDRESS)
            self.pump.diameter_mm(self.DIA)
            self.pump.volume(self.volume)
            self.pump.rate(self.rate)
            self.pump.direction_infuse()
        else:
            self.pump = None

        self.refilled = False

        pygame.init()
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        pygame.event.get()




        #Set stage positions
        if os.path.isfile('stage_posS.json'):
            with open('stage_posS.json', 'r') as f:
                self.stage_posS = json.load(f)
        else:
            self.stage_posS = {}
            self.stage_posS['start_pos'] = [132, 91, 108, 140]
            self.stage_posS['pickup_pos_xy'] = [132, 91]
            self.stage_posS['pickup_pos_z'] = 108
            self.stage_posS['dropoff_pos_xy'] = [60, 91]
            self.stage_posS['dropoff_pos_z'] = 108

        self.main_menu()

    def main_menu(self):
        print('\n\n######################\n\nMain Menu\n\n######################\n\n')
        print('1) Start collection with Robot\n')
        print('4) Change wafer position\n')

        c = input('\nChoose an option:\n')

        if c == '1':
            self.robot_collection()

        elif c == '4':
            try:
                sp = input('\nEnter position of wafer stage in mm:\n')
                #self.stage_pos[3] = int(sp)
            except ValueError:
                print('An error occurred: Wafer position could not be changed')
                input()
                self.main_menu()



    def robot_collection(self):
        with GCSDevice() as pidevice:
            if self.internal_water_level_control:
                if not self.manual_water_refill:
                    self.calibrate_cap_sensor()

            pidevice.ConnectUSB(serialnum="120060503")
            print('connected: {:s}'.format(pidevice.qIDN().strip()))
            pidevice.VEL(1, 20)
            pidevice.VEL(2, 20)
            pidevice.VEL(3, 20)
            pidevice.VEL(4, 20)
            pidevice.MOV(1, self.stage_posS['start_pos'][0])
            pidevice.MOV(2, self.stage_posS['start_pos'][1])
            pidevice.MOV(3, self.stage_posS['start_pos'][2])
            pidevice.MOV(4, self.stage_posS['start_pos'][3])
            time.sleep(10)

            #p = subprocess.Popen(['python', 'MicrotomeControlV2.py', self.log], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            self.write_cam_image_save_output()

            while True:


                #if self.cycle_count == 1:
                #    pickup = False
                #else:
                #    pickup = True
                pickup = True

                # Adjust pickup point

                self.stage_posS['pickup_pos_xy'][0], self.stage_posS['pickup_pos_xy'][1], temp_pos_z, end_collection, self.cycle_count = move_joystick(pidevice, self.joystick, self.pump, self.cycle_count, self.log, pickup=pickup)
                if end_collection and not self.cutting_stopped:
                    print('remove the wafer')
                    self.cycle_count = 'end'
                    self.write_log()
                    self.cutting_stopped = True
                    end_collection = False

                    pygame.joystick.quit()
                    pygame.joystick.init()
                    self.joystick = pygame.joystick.Joystick(0)
                    self.joystick.init()
                    pygame.event.get()
                elif end_collection and self.cutting_stopped:
                    pidevice.MOV(3, self.stage_posS['dropoff_pos_z'])
                    sleep(0.2)
                    pygame.joystick.quit()
                    pidevice.CloseConnection()
                    self.write_cam_image_save_end()
                    self.save_stage_pos()
                    print("Connection closed.")
                    break
                if temp_pos_z > 0:
                    self.stage_posS['pickup_pos_z'] = temp_pos_z
                # Pick section up (lowing the tip)
                pidevice.MOV(3, self.stage_posS['pickup_pos_z'])
                sleep((self.stage_posS['pickup_pos_z']-self.stage_posS['dropoff_pos_z'])/20 + 0.2)
                if self.cycle_count == 1:
                    self.write_log()
                # detach section from knife
                pidevice.MOV(1, pidevice.qPOS()["1"] - 5)
                sleep(0.5)

                #if not self.cutting_stopped:
                #    self.write_log()

                # Move section to wafer boat
                pidevice.MOV(1, self.stage_posS['dropoff_pos_xy'][0])
                pidevice.MOV(2, self.stage_posS['dropoff_pos_xy'][1])

                if self.internal_water_level_control:
                    if not self.manual_water_refill:
                        self.water_level_control()
                if self.refilled:
                    self.refilled = False
                else:
                    sleep(abs((self.stage_posS['pickup_pos_xy'][0]-5) - self.stage_posS['dropoff_pos_xy'][0]) / 20 + 0.2)

                if not self.flat_angle:
                    # Lift tip slightly
                    pidevice.MOV(3, self.stage_posS['pickup_pos_z']-0.1)
                    time.sleep(0.1/20)

                # Move section to wafer with joystick
                _, _, _, end_collection, self.cycle_count = move_joystick(pidevice, self.joystick, self.pump, self.cycle_count, self.log, positions=self.stage_posS)
                if end_collection and not self.cutting_stopped:
                    print('remove the wafer')
                    self.cycle_count = 'end'
                    self.write_log()
                    self.cutting_stopped = True
                    end_collection = False

                    pygame.joystick.quit()
                    pygame.joystick.init()
                    self.joystick = pygame.joystick.Joystick(0)
                    self.joystick.init()
                    pygame.event.get()
                elif end_collection and self.cutting_stopped:
                    pidevice.MOV(3, self.stage_posS['dropoff_pos_z'])
                    sleep(0.2)
                    pygame.joystick.quit()
                    pidevice.CloseConnection()
                    self.write_cam_image_save_end()
                    self.save_stage_pos()
                    print("Connection closed.")
                    break
                # Lift tip and retract wafer holder
                if not self.flat_angle:
                    pidevice.MOV(4, pidevice.qPOS()["4"] - 0.4)
                    sleep(1.5)
                pidevice.MOV(3, self.stage_posS['dropoff_pos_z'])
                sleep(0.2)
                # Move arm back to pickup point
                pidevice.MOV(1, self.stage_posS['pickup_pos_xy'][0])
                pidevice.MOV(2, self.stage_posS['pickup_pos_xy'][1])
                sleep(abs(pidevice.qPOS()["1"] - self.stage_posS['pickup_pos_xy'][0])/20+0.2)

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
            self.pump.run()
            time.sleep(5)
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
        self.stage_posS['start_pos'][0] = self.stage_posS['pickup_pos_xy'][0]
        self.stage_posS['start_pos'][1] = self.stage_posS['pickup_pos_xy'][1]
        stage_posF = {'start_pos': self.stage_posS['start_pos'],
                      'pickup_pos_xy': self.stage_posS['pickup_pos_xy'],
                      'pickup_pos_z': self.stage_posS['pickup_pos_z'],
                      'dropoff_pos_xy': self.stage_posS['dropoff_pos_xy'],
                      'dropoff_pos_z': self.stage_posS['dropoff_pos_z']}

        with open('stage_posS.json', 'w') as f:
            json.dump(stage_posF, f)

    def check_events(self):
        events = pygame.event.get()
        for e in events:
            if e.type == 1539:
                if e.dict['button'] == 0:
                    self.interrupt = True
                elif e.dict['button'] == 15:
                    if self.manual_water_refill:
                        self.pump.run()
                        sleep(15)

    def write_log(self):
        if self.cycle_count == 'end':
            with open(self.log + self.cycle_count + '.txt', 'w') as f:
                pass
        else:
            fn = str(self.cycle_count)
            while len(fn) < 7:
                fn = '0' + fn
            with open(self.log + fn + '.txt', 'w') as f:
                pass
            self.cycle_count += 1

    def write_cam_image_save_output(self):
        if self.save_cam_images:
            with open('images/image_logs/' + str(self.startup_t) + '_save_images.txt', 'w') as f:
                pass

    def write_cam_image_save_end(self):
        if self.save_cam_images:
            with open('images/image_logs/' + str(self.startup_t) + '_ended.txt', 'w') as f:
                pass


if __name__ == '__main__':
    collect = SemiManualCollection()