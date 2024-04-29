from leicame import LeicaMicrotomeController
import serial
import time

# Create an instance of the controller
mycon = LeicaMicrotomeController()
# Get Part ID
print("Getting Part ID...")
part_id = mycon.get_part_id()

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
