import cv2
from pypylon import pylon
import pygame
from screeninfo import get_monitors


class CamsViewer:

    def __init__(self):
        self.save_image = True
        # Camera
        self.image = None
        self.cam2 = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        self.cam2.Open()
        self.cam2.PixelFormat.SetValue("RGB8")
        self.cam2.Gain.SetValue(1)
        self.cam2.ExposureTime.SetValue(3200)
        with self.cam2.GrabOne(1000) as res:
            img = res.GetArray()
            self.x = img.shape[0] // 2
            self.y = img.shape[1] // 2
            self.org_img_shape = img.shape
        #self.cam1 = cv2.VideoCapture(1)

        # Pygame screen
        monitor = get_monitors()[0]
        self.screen_width = int(monitor.width * 0.75)
        self.screen_height = int(monitor.height * 0.75)
        self.screen_width = int(monitor.height * 0.75)
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

    def run(self):
        pygame.init()
        clock = pygame.time.Clock()
        running = True
        while running:
            self.get_image()
            for event in pygame.event.get():
                keys = pygame.key.get_pressed()
                if event.type == pygame.QUIT:
                    self.cam2.Close()
                    running = False

            if self.edit_ellipse_mode:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for i in range(len(self.ellipse_points)):
                            if not self.ellipse_points[i]:
                                self.ellipse_points[i] = pygame.mouse.get_pos()
                                break
                self.check_ellipse_points()
            else:
                if event.type == pygame.KEYDOWN:
                    if keys[pygame.K_LCTRL]:
                        if event.key == pygame.K_UP:
                            self.zoom_in()
                        elif event.key == pygame.K_DOWN:
                            self.zoom_out()
                    elif event.key == pygame.K_LEFT:
                        self.pan_right()
                    elif event.key == pygame.K_RIGHT:
                        self.pan_left()
                    elif event.key == pygame.K_UP:
                        self.pan_up()
                    elif event.key == pygame.K_DOWN:
                        self.pan_down()
                    elif event.key == pygame.K_LALT:
                        self.edit_ellipse_mode = True
                    elif event.key == pygame.K_LSHIFT:
                        if self.reduced:
                            self.unreduce_ellipse()
                        else:
                            self.reduce_ellipse()

            self.draw()
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

    def draw(self):
        """Draws all elements on the screen"""
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.image, self.image_rect)
        if self.edit_ellipse_mode:
            pygame.draw.rect(self.screen, "red", self.ee_mode_indicator_rect, 5)
            for p in self.ellipse_points:
                if p:
                    p_rect = pygame.Rect(0, 0, 3, 3)
                    p_rect.center = p
                    pygame.draw.rect(self.screen, "white", p_rect)
        if self.show_ellipse:
            pygame.draw.ellipse(self.screen, self.ellipse_color, self.ellipse_dimensions, self.ellipse_line_strength)

    def get_image(self):
        with self.cam2.GrabOne(1000) as res:
            img = res.GetArray()
            zoom = self.zoom
            x_low = self.x - int(zoom * img.shape[0] * 0.5)
            x_high = self.x + int(zoom * img.shape[0] * 0.5)
            y_low = self.y - int(zoom * img.shape[1] * 0.5)
            y_high = self.y + int(zoom * img.shape[1] * 0.5)

            if self.save_image:
                self.save_image = False
                img2 = cv2.cvtColor(cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE), cv2.COLOR_BGR2RGB)
                cv2.imwrite('images/wafer_test.png', img2)

            img = cv2.flip(cv2.resize(img[x_low:x_high, y_low:y_high, :], (self.screen_width, self.screen_height)), 0)

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

    def check_ellipse_points(self):
        if None not in self.ellipse_points:
            self.calc_ellipse_rect()

    def calc_ellipse_rect(self):
        xmin = min([i[0] for i in self.ellipse_points])
        xmax = max([i[0] for i in self.ellipse_points])
        ymin = min([i[1] for i in self.ellipse_points])
        ymax = max([i[1] for i in self.ellipse_points])

        self.ellipse_dimensions = pygame.Rect(xmin, ymin, xmax-xmin, ymax-ymin)

        self.edit_ellipse_mode = False
        self.show_ellipse = True

    def reduce_ellipse(self):
        center = self.ellipse_dimensions.center
        width = self.ellipse_dimensions.width
        height = self.ellipse_dimensions.height
        print(height, width)

        self.ellipse_dimensions = pygame.Rect(0, 0, width*self.use_factor, height*self.use_factor)
        self.ellipse_dimensions.center = center
        print(self.ellipse_dimensions.height,self.ellipse_dimensions.width)
        self.reduced = True

    def unreduce_ellipse(self):
        center = self.ellipse_dimensions.center
        width = self.ellipse_dimensions.width
        height = self.ellipse_dimensions.height
        print(height, width)

        self.ellipse_dimensions = pygame.Rect(0, 0, width / self.use_factor, height / self.use_factor)
        self.ellipse_dimensions.center = center
        print(self.ellipse_dimensions.height, self.ellipse_dimensions.width)
        self.reduced = False

if __name__ == '__main__':
    viewer = CamsViewer()
    viewer.run()

