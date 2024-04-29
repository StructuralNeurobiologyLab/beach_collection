import serial
from pipython import GCSDevice
from pipython.pitools import waitonwalk
AXES = ['1', '2', '3', '4']
MVR_STEPSIZE = 10
SETTLING_TIME = 0.5
with GCSDevice() as pidevice:
    pidevice.ConnectUSB(serialnum="120060503")
    print('connected: {:s}'.format(pidevice.qIDN().strip()))
    for axis in AXES:
        pidevice.MOV(1, 142)
        pidevice.MOV(2, 75)
        pidevice.MOV(3, 110)
        pidevice.MOV(4, 0)