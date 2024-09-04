import os
import sys
import time

#from leicame import LeicaMicrotomeController


def check_robot_fb(robot_fb, logs):
    while True:
        try:
            file_list = sorted(os.listdir(logs + 'robot'))
            if file_list[-1][0] == 'r':
                fb = int(file_list[-1][1:])
                if fb > robot_fb:
                    return True, fb
                else: 
                    return True, robot_fb
        except OSError:
            print('error when reading file list')


def run_cutting():
    
    slice_count = 1
    robot_fb = None
    logs = 'logs\\' + sys.argv[1] + '\\'
    if not os.path.isdir(logs):
        raise ValueError('log folder does not exist')

    # Create an instance of the controller
    mycon = LeicaMicrotomeController()
    # Get Part ID
    print("Getting Part ID...")
    part_id = mycon.get_part_id()

    while True:
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
            print(current_state)
            if current_state == b"03":
                was_in_cutting_window = True
                t1 = time.time()
            elif current_state == b"00" and was_in_cutting_window:
                cut_finished = True
                print("cut finished")
                break
            if was_in_cutting_window and time.time() - t1 > 1 and not file_written:
                slice_str = str(slice_count)
                while len(slice_str) < 6:
                    slice_str = '0' + slice_str
                try:
                    with open(logs + 'cutting\\' + slice_str + '.txt', 'w') as f:
                        pass
                    slice_count += 1
                    file_written = True
                except OSError:
                    print('error when creating the output file:', slice_str)

        while True:
            stopping, robot_fb = check_robot_fb(robot_fb, logs)
            if stopping:
                break
            else:
                time.sleep(1)

if __name__ == '__main__':
    print(int('00030'))
    
    