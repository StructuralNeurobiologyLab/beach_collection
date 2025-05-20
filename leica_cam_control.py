import os

import cv2
import time
import pygame
from screeninfo import get_monitors


class CamsViewer:

    def __init__(self):

        # Camera
        self.image = None
        self.cam2 = cv2.VideoCapture(0)
        self.exposure = -7
        self.cam2.set(cv2.CAP_PROP_EXPOSURE, self.exposure)
        #self.cam2.set(cv2.CAP_PROP_GAIN, self.exposure)
        img = self.grab_image()
        self.x = img.shape[0] // 2
        self.y = img.shape[1] // 2
        self.org_img_shape = img.shape
        #self.cam1 = cv2.VideoCapture(1)

        # Pygame screen
        monitor = get_monitors()[0]
        self.screen_width = int(img.shape[1] * 0.75)
        self.screen_height = int(img.shape[0] * 0.75)
        self.screen_width = int(img.shape[1] * 0.75)
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Cam Viewer")

        # Image display
        self.image_rect = pygame.Rect(0, 0, self.screen_width, self.screen_height)

        # Ellipse tool
        self.ellipse_color = "yellow"
        self.ellipse_line_strength = 1
        self.ellipse_dimensions = pygame.Rect(1, 1, 1, 1)
        self.show_ellipse = False

        # Edit ellipse mode
        self.edit_ellipse_mode = False
        self.ellipse_points = [None, None, None, None]
        self.ee_mode_indicator_rect = pygame.Rect(0, 0, self.screen_width, self.screen_height)

        # Zoom
        self.zoom_level = 0
        self.zoom_levels = [1, 0.8, 0.66, 0.5, 0.4, 0.2, 0.13, 0.1]
        self.zoom = self.zoom_levels[self.zoom_level]

        # Wafer
        self.use_factor = 1 - 1/5.08    # define distance to the edge of the wafer
        self.reduced = False

        # Image handling
        self.save_image_flag = False
        self.save_image_count = 0
        self.sub_image_count = 0
        self.sub_image_threshold = 2
        self.subfolder = '/250217/'
        self.record_collection = False


    def run(self):
        pygame.init()
        clock = pygame.time.Clock()
        running = True
        while running:
            self.check_image_logs()
            self.get_image()
            self.save_image_flag = False
            for event in pygame.event.get():
                keys = pygame.key.get_pressed()
                if event.type == pygame.QUIT:
                    self.cam2.release()
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.exposure += 1
                        self.cam2.set(cv2.CAP_PROP_EXPOSURE, self.exposure)
                    elif event.key == pygame.K_DOWN:
                        self.exposure -= 1
                        self.cam2.set(cv2.CAP_PROP_EXPOSURE, self.exposure)
                    elif event.key == pygame.K_p:
                        self.save_image_flag = True
                        print('saving image')

            self.draw()
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

    def draw(self):
        """Draws all elements on the screen"""
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.image, self.image_rect)


    def get_image(self):
        img = self.grab_image()
        if self.save_image_flag or self.record_collection:
            self.save_image(img)
        img = cv2.cvtColor(cv2.rotate(cv2.flip(cv2.resize(img, (self.screen_width, self.screen_height)), 0), cv2.ROTATE_90_CLOCKWISE), cv2.COLOR_BGR2RGB)

        self.image = pygame.surfarray.make_surface(img)
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
        if not os.path.isdir('images' + self.subfolder):
            os.makedirs('images' + self.subfolder)

        cv2.imwrite('images' + self.subfolder + 'image' + str(self.save_image_count) + '.png', img)

        self.save_image_count += 1

    #def set_subfolder(self, f):
    #    self.subfolder = f
    #    if not os.path.isdir('images' + self.subfolder):
    #        os.makedirs('images' + self.subfolder)

    #def set_subimage_threshold(self, t):
    #    self.sub_image_threshold = t

    #def set_save_flag(self, f):
    #    self.save_image_flag = f

    def check_image_logs(self):

        latest_dir = sorted(os.listdir('logs'))[-1]
        if latest_dir + '_save_images.txt' in os.listdir('images/image_logs'):
            if not latest_dir + '_ended.txt' in os.listdir('images/image_logs'):
                if not self.record_collection:
                    self.record_collection = True
                    self.subfolder = '/' + latest_dir + '/leica_cam/'
                    self.save_image_count = 0
            else:
                self.record_collection = False




if __name__ == '__main__':
    viewer = CamsViewer()
    viewer.run()

