import os

from cap import ncdt6500_get_data, ncdt6500_decode
import ne1000
import time

class WaterLevelControl():
    def __init__(self):
        self.TCP_ADDRESS = '169.254.168.150'
        self.PORT = 'COM5'
        self.ADDRESS = 1
        self.DIA = 38

        self.dev = ne1000.Ne1000Serial(self.PORT)
        self.volume = ne1000.Ne1000Volume(0.1, 'ml')
        self.rate = ne1000.Ne1000Rate(10, 'MM')

        self.pump = ne1000.Ne1000(self.dev, self.ADDRESS)
        self.pump.diameter_mm(self.DIA)
        self.pump.volume(self.volume)
        self.pump.rate(self.rate)
        self.pump.direction_infuse()

        self.calibrate_cap_sensor()
        self.run_water_level_control()

    def water_level_control(self):
        for channel, raw_data in enumerate(ncdt6500_get_data()):
            print(f"channel #{channel}: {ncdt6500_decode(raw_data):.4g} V")
            waterlevel = ncdt6500_decode(raw_data)
        if waterlevel < self.ut - 0.5:
            raise ValueError('Large change in cap sensor reading detected. Please check the cap sensor for water drops.')
        if waterlevel > self.ue:
            self.pump.run()
            time.sleep(5)
        #  if waterlevel < ut:
        #     pump = ne1000.Ne1000(dev, ADDRESS)
        #     pump.diameter_mm(DIA)
        #    pump.volume(volume)
        #    pump.rate(rate)
        #    pump.direction_withdraw()
        #    pump.run()
        #   time.sleep(10)
        elif waterlevel <= self.ue:
            # continue
            time.sleep(0.1)

    def calibrate_cap_sensor(self):
        cap_reading = input('Please adjust the water level and the Z position of the cap sensor.\nThen enter the output of the cap sensor (in percent) to calibrate the reading:\n')
        x = int(cap_reading)
        y = x * 0.1
        self.ue = y + 0.1
        self.ut = y - 0.1
        print(self.ue)
        print(self.ut)

    def run_water_level_control(self):
        while True:
            self.water_level_control()
            logs = 'logs\\' + sorted(os.listdir('logs'))[-1] + '\\'
            file_list = sorted(os.listdir(logs))
            fb = file_list[-1][0:-4]
            if fb == 'end':
                break


if __name__ == '__main__':
    wlc = WaterLevelControl()