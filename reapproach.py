import os
import time

from leicame import LeicaMicrotomeController

import numpy as np
import cv2
import pygame
from screeninfo import get_monitors



class CamsViewer:

    def __init__(self):
        
        # Detection
        self.white_px_threshold = 250
        self.detection_factor = 3
        self.white_px_count = []

        # Camera
        self.image = None
        self.cam2 = cv2.VideoCapture(0)
        self.exposure = -7
        self.cam2.set(cv2.CAP_PROP_EXPOSURE, self.exposure)
        #self.cam2.set(cv2.CAP_PROP_GAIN, self.exposure)
        self.img = self.grab_image()
        self.x = self.img.shape[0] // 2
        self.y = self.img.shape[1] // 2
        self.org_img_shape = self.img.shape
        #self.cam1 = cv2.VideoCapture(1)

        # Pygame screen
        monitor = get_monitors()[0]
        self.sf = 0.75
        self.screen_width = int(self.img.shape[1] * self.sf)
        self.screen_height = int(self.img.shape[0] * self.sf)
        self.screen_width = int(self.img.shape[1] * self.sf)
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Cam Viewer")

        # Image display
        self.image_rect = pygame.Rect(0, 0, self.screen_width, self.screen_height)

        # ROI tool
        self.ROI_color = "yellow"
        self.ROI_line_strength = 1
        self.ROI_dimensions = pygame.Rect(1, 1, 1, 1)
        self.show_ROI = False

        # ROI mode
        self.edit_ROI = True
        self.ROI_points = [None, None]
        self.ee_mode_indicator_rect = pygame.Rect(0, 0, self.screen_width, self.screen_height)

        # Image handling
        self.save_image_flag = False
        self.save_image_count = 0
        self.sub_image_count = 0
        self.sub_image_threshold = 2
        self.subfolder = '/250117/'

        # Microtome
        self.mycon = LeicaMicrotomeController()
        print("Getting Part ID...")
        part_id = self.mycon.get_part_id()
        self.stopping = True

    def run(self):
        pygame.init()
        clock = pygame.time.Clock()
        running = True
        while running:
            self.get_image()
            for event in pygame.event.get():
                keys = pygame.key.get_pressed()
                if event.type == pygame.QUIT:
                    self.cam2.release()
                    
                elif event.type == pygame.MOUSEBUTTONDOWN and self.edit_ROI:
                    if event.button == 1:
                        if not self.ROI_points[0]:
                            self.ROI_points[0] = pygame.mouse.get_pos()
                            print(self.ROI_points)
                        elif not self.ROI_points[1]:
                            self.ROI_points[1] = pygame.mouse.get_pos()
                            print(self.ROI_points)
                            left = min(self.ROI_points[0][0], self.ROI_points[1][0])
                            top = min(self.ROI_points[0][1], self.ROI_points[1][1])
                            width = abs(self.ROI_points[0][0] - self.ROI_points[1][0])
                            height = abs(self.ROI_points[0][1] - self.ROI_points[1][1])
                            self.ROI_dimensions = pygame.Rect(left, top, width, height)
                            self.show_ROI = True
                            self.edit_ROI = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        self.stopping = False
                    if event.key == pygame.K_a:
                        self.stopping = True

            
            self.draw()
            pygame.display.flip()
            clock.tick(60)

            if self.show_ROI and not self.stopping:
                self.calc_nr_white_px()
                if len(self.white_px_count) > 1:
                    if self.white_px_count[-1] > self.detection_factor * self.white_px_count[-1]:
                        user = input('Stop reapproach? y/n\n')
                        if user == 'y':
                            break
                self.do_cut()

        pygame.quit()

    def draw(self):
        """Draws all elements on the screen"""
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.image, self.image_rect)
        if self.show_ROI:
            pygame.draw.rect(self.screen, self.ROI_color, self.ROI_dimensions, self.ROI_line_strength)


    def get_image(self):
        self.img = self.grab_image()
        if self.save_image_flag:
            self.save_image(self.img)
        temp_img = cv2.cvtColor(cv2.rotate(cv2.flip(cv2.resize(self.img, (self.screen_width, self.screen_height)), 0), cv2.ROTATE_90_CLOCKWISE), cv2.COLOR_BGR2RGB)

        self.image = pygame.surfarray.make_surface(temp_img)
        #is_reading, img2 = self.cam1.read()
        #if is_reading:
        #    self.image = pygame.surfarray.make_surface(img2)

    def grab_image(self):
        if not self.cam2.isOpened():
            raise ConnectionError('Port 0 is not working.')
        else:
            is_reading, img1 = self.cam2.read()
            if is_reading:
                #print(img1.shape)
                return img1
            else:
                raise ConnectionError('Cam Port 0 not reading')

    def save_image(self, img):
        #self.sub_image_count += 1

        cv2.imwrite('images' + self.subfolder + 'image' + str(self.save_image_count) + '_' + str(self.sub_image_count) + '_' + str(time.time()) + '.png', img)

        self.save_image_count += 1

    def set_subfolder(self, f):
        self.subfolder = f
        if not os.path.isdir('images' + self.subfolder):
            os.makedirs('images' + self.subfolder)

    def set_subimage_threshold(self, t):
        self.sub_image_threshold = t

    def set_save_flag(self, f):
        self.save_image_flag = f

    def do_cut(self):
        print("Turn motor on...")
        motor_on = self.mycon.cutting_motor_on()
        motor_status = self.mycon.cutting_motor_status()
        if motor_status[7:9] == b'01':
            print("it's on")
        elif motor_status[7:9] == b'00':
            print("it's off")
            raise Exception
        elif motor_status[7:9] == b'E0':
            print("invalid callabration")
            raise Exception
        else:
            print("invalid response")
            raise Exception

        cut_finished = False
        was_in_cutting_window = False
        file_written = False
        while not cut_finished:
            current_state = self.mycon.get_handwheel_position()[7:9]
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
        motor_off = self.mycon.cutting_motor_off()
        motor_status = self.mycon.cutting_motor_status()
        if motor_status[7:9] == b'01':
            print("it's on")
            raise Exception
        elif motor_status[7:9] == b'00':
            print("it's off")
        elif motor_status[7:9] == b'E0':
            print("invalid callabration")
            raise Exception
        else:
            print("invalid response")
            raise Exception
        
    def calc_nr_white_px(self):     
        img_gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        img_gray[img_gray<self.white_px_threshold] = 0
        img_gray[img_gray>=self.white_px_threshold] = 1
        
        t = int(self.ROI_dimensions.top / self.sf)
        h = int(self.ROI_dimensions.height / self.sf)
        l = int(self.ROI_dimensions.left / self.sf)
        w = int(self.ROI_dimensions.width / self.sf)

        self.white_px_count.append(np.sum(img_gray[t:t+h, l:l+w]))


if __name__ == '__main__':
    viewer = CamsViewer()
    viewer.run()

