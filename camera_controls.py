import cv2
from pypylon import pylon
import pygame
from screeninfo import get_monitors


class CamsViewer:

    def __init__(self):

        self.image = None
        self.cam2 = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        self.cam2.Open()
        self.cam2.PixelFormat.SetValue("RGB8")
        self.cam2.Gain.SetValue(20)
        self.cam2.ExposureTime.SetValue(1200)
        with self.cam2.GrabOne(1000) as res:
            img = res.GetArray()
            self.x = img.shape[0] // 2
            self.y = img.shape[1] // 2
            self.org_img_shape = img.shape
        #self.cam1 = cv2.VideoCapture(1)

        monitor = get_monitors()[0]
        self.screen_width = int(monitor.width * 0.5)
        self.screen_height = int(monitor.height * 0.5)
        self.screen_width = int(monitor.height * 0.5)
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Cam Viewer")

        self.image_rect = pygame.Rect(0, 0, self.screen_width, self.screen_height)

        # Zoom
        self.zoom_level = 0
        self.zoom_levels = [1, 0.8, 0.66, 0.5, 0.4, 0.2, 0.13, 0.1]
        self.zoom = self.zoom_levels[self.zoom_level]

    def run(self):
        pygame.init()
        clock = pygame.time.Clock()
        running = True
        while running:
            self.get_image()
            for event in pygame.event.get():
                keys = pygame.key.get_pressed()
                if event.type == pygame.QUIT:
                    running = False

            if event.type == pygame.KEYDOWN:
                if keys[pygame.K_LCTRL]:
                    if event.key == pygame.K_UP:
                        self.zoom_in()
                    elif event.key == pygame.K_DOWN:
                        self.zoom_out()
                elif event.key == pygame.K_LEFT:
                    self.pan_left()
                elif event.key == pygame.K_RIGHT:
                    self.pan_right()
                elif event.key == pygame.K_UP:
                    self.pan_up()
                elif event.key == pygame.K_DOWN:
                    self.pan_down()


            self.draw()
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

    def draw(self):
        """Draws all elements on the screen"""
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.image, self.image_rect)

    def get_image(self):
        with self.cam2.GrabOne(1000) as res:
            img = res.GetArray()
            zoom = self.zoom
            x_low = self.x - int(zoom * img.shape[0] * 0.5)
            x_high = self.x + int(zoom * img.shape[0] * 0.5)
            y_low = self.y - int(zoom * img.shape[1] * 0.5)
            y_high = self.y + int(zoom * img.shape[1] * 0.5)

            img = cv2.resize(img[x_low:x_high, y_low:y_high, :], (self.screen_width, self.screen_height))

            self.image = pygame.surfarray.make_surface(img)
        #is_reading, img2 = self.cam1.read()
        #if is_reading:
        #    self.image = pygame.surfarray.make_surface(img2)

    def zoom_in(self):
        if self.zoom_level > -0.1 and self.zoom_level < 7:
            self.zoom_level += 1
            self.zoom = self.zoom_levels[self.zoom_level]

    def zoom_out(self):
        if self.zoom_level > 0 and self.zoom_level < 7.1:
            self.zoom_level -= 1
            self.zoom = self.zoom_levels[self.zoom_level]

            x_low = self.x - int(self.zoom * self.org_img_shape[0] * 0.5)
            x_high = self.x + int(self.zoom * self.org_img_shape[0] * 0.5)
            y_low = self.y - int(self.zoom * self.org_img_shape[1] * 0.5)
            y_high = self.y + int(self.zoom * self.org_img_shape[1] * 0.5)

            if x_low < 0:
                self.x += (0 - x_low)
            elif x_high > self.org_img_shape[0]:
                self.x -= (x_high - self.org_img_shape[0])

            if y_low < 0:
                self.y += (0 - y_low)
            elif y_high > self.org_img_shape[0]:
                self.y -= (y_high - self.org_img_shape[0])

    def pan_left(self, step=10):
        x_low = self.x - int(self.zoom * self.org_img_shape[0] * 0.5)
        if x_low - step >= 0:
            self.x -= step

    def pan_right(self, step=10):
        x_high = self.x + int(self.zoom * self.org_img_shape[0] * 0.5)
        if x_high + step <= self.org_img_shape[0]:
            self.x += step

    def pan_up(self, step=10):
        y_low = self.y - int(self.zoom * self.org_img_shape[1] * 0.5)
        if y_low - step >= 0:
            self.y -= step

    def pan_down(self, step=10):
        y_high = self.y + int(self.zoom * self.org_img_shape[1] * 0.5)
        if y_high + step <= self.org_img_shape[0]:
            self.y += step


if __name__ == '__main__':
    viewer = CamsViewer()
    viewer.run()

