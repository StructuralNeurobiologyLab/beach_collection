from pipython import GCSDevice
from time import sleep
import pygame

def move_wafer(pidevice, joystick,lower_ybound=0, upper_ybound=150):
    pos = pidevice.qPOS()["4"]
    print(pos)
    while True:
        pygame.event.get()

        pos = pidevice.qPOS()["4"]

        if joystick.get_button(4) == True:
            if pos + 10 <= upper_ybound:
                pos += 10
                pidevice.MOV(4, pos)
                print(pos)
                sleep(1)
            else:
                print('Upper bound reached')
                print(pos)

        elif joystick.get_button(5) == True:
            if pos - 10 >= lower_ybound:
                pos -= 10
                pidevice.MOV(4, pos)
                print(pos)
                sleep(1)
            else:
                print('Lower bound reached')
                print(pos)

        elif joystick.get_button(9) == True:
            while True:
                try:
                    tpos = int(input("Please enter a position value"))
                    if tpos <= upper_ybound and tpos >= lower_ybound:
                        pidevice.MOV(4, tpos)
                        print(tpos)
                        sleep(abs(tpos-pos)/20+0.5)
                        pos = tpos
                        break
                    else:
                        raise ValueError
                except ValueError:

                    print('ValueError: Please enter a valid value')

        elif joystick.get_button(13) == True:
            print('Ending script...')
            break


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

    move_wafer(pidevice, joystick)

    sleep(0.2)
    pygame.joystick.quit()
    pidevice.CloseConnection()

