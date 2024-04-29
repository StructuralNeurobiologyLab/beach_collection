# Import the LeicaMicrotomeController class
from leicame import LeicaMicrotomeController
import serial
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
print(f"Current cutting thickness: {int(thickness[7:11],16)}nm")

print("Setting cutting speed to 0.8mm/s...")
sd = 800
sh = hex(sd).split('x')[-1]
sh1 = '0000' + sh
mycon.set_cutting_speed(sh1[-4:])
speed = mycon.get_cutting_speed()  # Get current speed
print(f"Current cutting speed: {int(speed[7:11],16)}um/s")

print("Turn motor on...")
motor_on = mycon.cutting_motor_on()
motor_status = mycon.cutting_motor_status()
if motor_status[7:9] == b'01':
    print("it's on")
elif motor_status[7:9] == b'00':
    print("it's off")
elif motor_status[7:9] == b'E0':
    print("invalid callabration")
else:
    print("invalid response")

print("get_handwheel_position...")
handwheel_position = mycon.get_handwheel_position()
if handwheel_position[7:9] == b'00':
    print("retract")
elif handwheel_position[7:9] == b'01':
    print("before cutting window")
elif handwheel_position[7:9] == b'02':
    print("after cutting window")
elif handwheel_position[7:9] == b'03':
    print("in cutting window")
elif handwheel_position[7:9] == b'E0':
    print("invalid callabration")
else:
    print("invalid response")

print("Turn motor off...")
motor_off = mycon.cutting_motor_off()
motor_status = mycon.cutting_motor_status()
if motor_status[7:9] == b'01':
    print("it's on")
elif motor_status[7:9] == b'00':
    print("it's off")
elif motor_status[7:9] == b'E0':
    print("invalid callabration")
else:
    print("invalid response")

mycon.close()
print("Connection closed.")