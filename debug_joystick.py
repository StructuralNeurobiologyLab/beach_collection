from pipython import GCSDevice
from time import sleep
import pygame
import math
from motorcontrol_pico_class import SerialInstrument



def move_joystick(pidevice, joystick, pump, slice_count, log, abs_rot=0,
                  positions=False,
                  speed=1,
                  left_xbound=0,
                  right_xbound=150,
                  lower_ybound=0,
                  upper_ybound=150,
                  pickup=False):

    zpos = pidevice.qPOS()["3"]
    zpos_final = 0

    end_collection = False
    finished = False
    move_locked = True

    # COM_PORT = "COM6"  # Instrument port location
    # TIMEOUT = 1
    # instrument = SerialInstrument(COM_PORT, TIMEOUT)

    button_8 = False

    new_attempt = False
    cut_done = False

    while True:
        if positions:
            dist = math.sqrt((positions['dropoff_pos_xy'][0] - pidevice.qPOS()["1"])**2 + (positions['dropoff_pos_xy'][1] - pidevice.qPOS()["2"])**2)
        else:
            dist = 0
        pygame.event.get()

        delta_y = joystick.get_axis(0)  # todo: remove -1 after calibration
        delta_x = -joystick.get_axis(1)

        if pickup and move_locked:
            delta_x = 0
            delta_y = 0

        if abs(delta_x) < 0.0025:
            delta_x = 0
        if abs(delta_y) < 0.0025:
            delta_y = 0

        xpos = max(left_xbound, min(right_xbound, pidevice.qPOS()["1"] + speed * delta_x))
        ypos = max(lower_ybound, min(upper_ybound, pidevice.qPOS()["2"] + speed * delta_y))

        print(f"new x,y {xpos, ypos}, delta {delta_x, delta_y}, new z {zpos}")
        print(pidevice.read('VEL?'))

        if delta_x == 0 and delta_y == 0:
            pidevice.MOV(1, pidevice.qPOS()["1"])
            pidevice.MOV(2, pidevice.qPOS()["2"])
        else:
            pidevice.VEL(1, 20 * abs(delta_x))
            pidevice.VEL(2, 20 * abs(delta_y))
            pidevice.MOV(1, xpos)
            pidevice.MOV(2, ypos)

        #sleep(0.1)

        if joystick.get_button(0) == True:
            print("done with joystick")
            pidevice.VEL(1, 20)
            pidevice.VEL(2, 20)
            sleep(0.1)
            break

        elif joystick.get_button(3) == True:
            print('toggle pickup pos xy')
            if move_locked == True:
                move_locked = False
                print('move unlocked')
            else:
                move_locked = True
                print('move locked')

        elif joystick.get_button(4) == True:
            zpos += 0.1
            pidevice.MOV(3, zpos)
            zpos_final = zpos

        elif joystick.get_button(5) == True:
            zpos -= 0.1
            pidevice.MOV(3, zpos)
            zpos_final = zpos

        elif joystick.get_button(6) == True:
            print('retract wafer')
            wpos = pidevice.qPOS()["4"]
            pidevice.MOV(4, max(0, wpos - 0.01))

        elif joystick.get_button(7) == True:
            print('retract wafer')
            wpos = pidevice.qPOS()["4"]
            pidevice.MOV(4, max(0, wpos - 0.001))

        elif joystick.get_button(8) == True:
            button_8 = True
            # make cut


        elif joystick.get_button(9) == True:
            zpos += 0.01
            pidevice.MOV(3, zpos)
            zpos_final = zpos

        elif joystick.get_button(10) == True:
            # return to pickup position without cut
            if positions:
                new_attempt = True
                pidevice.VEL(1, 20)
                pidevice.VEL(2, 20)
                pidevice.MOV(3, positions['dropoff_pos_z'])
                zpos = positions['dropoff_pos_z']
                sleep(1)
                pidevice.MOV(1, positions['pickup_pos_xy'][0])
                pidevice.MOV(2, positions['pickup_pos_xy'][1])
                sleep(abs(positions['pickup_pos_xy'][0] - positions['dropoff_pos_xy'][0])/20+0.1)

        elif joystick.get_button(11) == True:
            # return to dropoff position without cut
            if positions:
                pidevice.VEL(1, 20)
                pidevice.VEL(2, 20)
                pidevice.MOV(1, positions['dropoff_pos_xy'][0])
                pidevice.MOV(2, positions['dropoff_pos_xy'][1])
                sleep(abs(positions['pickup_pos_xy'][0] - positions['dropoff_pos_xy'][0])/20+0.1)
                new_attempt = False

        elif joystick.get_button(12) == True:
            if pump:
                pump.run()

        elif joystick.get_button(13) == True:
            print('ending collection')
            pidevice.VEL(1, 20)
            pidevice.VEL(2, 20)

            #instrument.disconnect()

            end_collection = True
            break

        elif button_8 and not joystick.get_button(8) and slice_count != 'end':
            button_8 = False
            fn = str(slice_count)
            while len(fn) < 7:
                fn = '0' + fn
            with open(log + fn + '.txt', 'w') as f:
                pass
            slice_count += 1

        elif not new_attempt and not cut_done and dist > 5 and slice_count != 'end':
            cut_done = True
            fn = str(slice_count)
            while len(fn) < 7:
                fn = '0' + fn
            with open(log + fn + '.txt', 'w') as f:
                pass
            slice_count += 1

        # elif joystick.get_button(14) == True:
        #     # rotation left
        #     print(instrument.write("left",8,1))
        #     abs_rot += 1
        #
        # elif joystick.get_button(15) == True:
        #     # rotation left
        #     print(instrument.write("right", 8, 1))
        #     abs_rot += 1
    return xpos, ypos, zpos_final, end_collection, slice_count



if __name__ == "__main__":
    pidevice = GCSDevice()
    pidevice.ConnectUSB(serialnum="120060503")
    print('connected: {:s}'.format(pidevice.qIDN().strip()))

    #pidevice.MOV(1, 100)
    #pidevice.MOV(2, 75)
    #pidevice.MOV(3, 132)
    #pidevice.MOV(4, 100)
    sleep(2)

    pygame.init()
    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    pygame.event.get()

    move_joystick(pidevice, joystick, 3)