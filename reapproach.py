import os
import time

from leicame import LeicaMicrotomeController
from leica_cam_control import CamsViewer

import pygame



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

    cam = CamsViewer()
    cam.set_subfolder('/250117/')
    cam.set_subimage_threshold(2)

    while True:
        pygame.init()
        clock = pygame.time.Clock()

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
            # print(current_state)
            if current_state == b"03":
                was_in_cutting_window = True
                t1 = time.time()
            elif current_state == b"00" and was_in_cutting_window:
                cut_finished = True
                print("cut finished")
                break

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

        slice_count += 1

        cam.set_save_flag(True)
        cam.get_image()
        cam.draw()
        pygame.display.flip()
        clock.tick(60)
        time.sleep(1)


if __name__ == '__main__':
    run_cutting()