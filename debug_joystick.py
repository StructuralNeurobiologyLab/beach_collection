import time

from pipython import GCSDevice
from pipython.pitools import waitonwalk
from time import sleep
import pygame


def move_joystick(pidevice, joystick, pump,
                  speed=1,
                  left_xbound=0,
                  right_xbound=150,
                  lower_ybound=0,
                  upper_ybound=150):
    xpos = pidevice.qPOS()["1"]
    ypos = pidevice.qPOS()["2"]
    zpos = pidevice.qPOS()["3"]
    zpos_final = 0

    end_collection = False

    while True:
        pygame.event.get()

        delta_y = joystick.get_axis(0)  # todo: remove -1 after calibration
        delta_x = -joystick.get_axis(1)

        if abs(delta_x) < 0.0025:
            delta_x = 0
        if abs(delta_y) < 0.0025:
            delta_y = 0

        xpos = max(left_xbound, min(right_xbound, xpos + speed * delta_x))
        ypos = max(lower_ybound, min(upper_ybound, ypos + speed * delta_y))

        print(f"new x,y {xpos, ypos}, delta {delta_x, delta_y}, new z {zpos}")

        pidevice.MOV(1, xpos)
        pidevice.MOV(2, ypos)

        sleep(0.1)

        if joystick.get_button(3) == True:
            print('reset pos')
            pidevice.MOV(1, 122)
            pidevice.MOV(2, 75)
            pidevice.MOV(3, 132)
            pidevice.MOV(4, 100)
            sleep(5)
            xpos = pidevice.qPOS()["1"]
            ypos = pidevice.qPOS()["2"]

        elif joystick.get_button(7) == True:
            print('retract wafer')
            wpos = pidevice.qPOS()["4"]
            pidevice.MOV(4, wpos - 1)

        elif joystick.get_button(6) == True:
            print('retract wafer')
            wpos = pidevice.qPOS()["4"]
            pidevice.MOV(4, wpos - 10)

        elif joystick.get_button(0) == True:
            print("done with joystick")
            sleep(2)
            break

        elif joystick.get_button(13) == True:
            print('ending collection')
            end_collection = True
            break

        elif joystick.get_button(4) == True:
            zpos += 0.1
            pidevice.MOV(3, zpos)
            zpos_final = zpos

        elif joystick.get_button(5) == True:
            zpos -= 0.1
            pidevice.MOV(3, zpos)
            zpos_final = zpos

        elif joystick.get_button(9) == True:
            zpos += 0.01
            pidevice.MOV(3, zpos)
            zpos_final = zpos

        elif joystick.get_button(8) == True:
            zpos -= 0.01
            pidevice.MOV(3, zpos)
            zpos_final = zpos

        elif joystick.get_button(15) == True:
            pump.run()

    return xpos, ypos, zpos_final, end_collection


if __name__ == "__main__":
    pidevice = GCSDevice()
    pidevice.ConnectUSB(serialnum="120060503")
    print('connected: {:s}'.format(pidevice.qIDN().strip()))

    pidevice.MOV(1, 122)
    pidevice.MOV(2, 75)
    pidevice.MOV(3, 132)
    pidevice.MOV(4, 100)
    sleep(2)

    pygame.init()
    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    pygame.event.get()

    move_joystick(pidevice, joystick)
