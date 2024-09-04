# -*- coding: utf-8 -*-


from cap import ncdt6500_get_data, ncdt6500_decode

import ne1000

import socket

from typing import List

import time
from time import sleep
import json

TCP_ADDRESS = '169.254.168.150'

#x is the procentage shown at the ue cap controller at the optimal water level ener x manually at callabration

exp_date = '240829'

x = 78
d = 0.5
y = x * 0.1
ue = y + d
ut = y - d
print(ue)
print(ut)
PORT = 'COM5'
ADDRESS = 1
DIA = 38
# 1ml werden nchgefullt 2 ist 1 ml
dev = ne1000.Ne1000Serial(PORT)
volume = ne1000.Ne1000Volume(2, 'ml')
rate = ne1000.Ne1000Rate(10, 'MM')
pump = ne1000.Ne1000(dev, ADDRESS)
pump.diameter_mm(DIA)
pump.volume(volume)
pump.rate(rate)
pump.direction_infuse()

data = {'waterlevel': {'time': [], 'waterlevel': []}, 'refill': {'time': [], 'refill_ml': []}}
start_time = time.time()

waterlevel_low = False
#was_in_cutting_window = False
while not waterlevel_low:
    for channel, raw_data in enumerate(ncdt6500_get_data()):
        print(f"channel #{channel}: {ncdt6500_decode(raw_data):.4g} V")
        waterlevel = ncdt6500_decode(raw_data)
        data['waterlevel']['time'].append(time.time() - start_time)
        data['waterlevel']['waterlevel'].append(waterlevel)
    if waterlevel > ue:
        data['refill']['time'].append(time.time() - start_time)
        data['refill']['refill_ml'].append(2)
        pump.run()
        time.sleep(15)
  #  if waterlevel < ut:
   #     pump = ne1000.Ne1000(dev, ADDRESS)
   #     pump.diameter_mm(DIA)
    #    pump.volume(volume)
    #    pump.rate(rate)
    #    pump.direction_withdraw()
    #    pump.run()
     #   time.sleep(10)
    elif waterlevel <= ue:
        with open('waterlevel_test_data_' + exp_date + '.json', 'w') as f:
            json.dump(data, f)
        #continue
        time.sleep(60)