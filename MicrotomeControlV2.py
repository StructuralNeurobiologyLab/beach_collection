import os
import time


from leicame import LeicaMicrotomeController


def check_robot_fb(slice_count, logs):
    while True:
        try:
            file_list = sorted(os.listdir(logs))

            fb = file_list[-1][0:-4]
            if fb == 'end':
                return True, True
            elif int(fb) == slice_count:
                return False, False
            else:
                return True, False
        except OSError:
            print('error when reading file list')


def run_cutting():
    
    slice_count = 1
    robot_fb = None
    logs = 'logs\\' + sorted(os.listdir('logs'))[-1] + '\\'
    if not os.path.isdir(logs):
        raise ValueError('log folder does not exist')

    # Create an instance of the controller
    mycon = LeicaMicrotomeController()
    # Get Part ID
    print("Getting Part ID...")
    part_id = mycon.get_part_id()

    while True:
        print('Slice count:', slice_count)
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
        file_written = False
        while not cut_finished:
            current_state = mycon.get_handwheel_position()[7:9]
#           print(time.time())
            #print(current_state)
            if current_state == b"03":
                was_in_cutting_window = True
                t1 = time.time()
            elif current_state == b"00" and was_in_cutting_window:
                cut_finished = True
                print("cut finished")
                break



        stopping, ending = check_robot_fb(slice_count, logs)
        if stopping:
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

        while stopping:
            if ending:
                return None
            time.sleep(1)
            stopping, ending = check_robot_fb(slice_count, logs)

        slice_count += 1

if __name__ == '__main__':

    run_cutting()
    
    