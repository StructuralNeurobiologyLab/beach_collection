import time

from pipython import GCSDevice
from pipython.pitools import waitonwalk
from time import sleep
import pygame


def move_joystick(pidevice, joystick,
                  speed=1,
                  left_xbound=0,
                  right_xbound=150,
                  lower_ybound=0,
                  upper_ybound=150):
    xpos = pidevice.qPOS()["1"]
    ypos = pidevice.qPOS()["2"]

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

        print(f"new x,y {xpos, ypos}, delta {delta_x, delta_y}")

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

        if joystick.get_button(0) == True:
            print("done with joystick")
            sleep(2)

            break

    return xpos, ypos


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
