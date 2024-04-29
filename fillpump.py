import ne1000

PORT = 'COM5'
ADDRESS = 1
DIA = 38
#fill 50 ml
volume = ne1000.Ne1000Volume(100, 'ml')
rate = ne1000.Ne1000Rate(10, 'MM')

dev = ne1000.Ne1000Serial(PORT)

pump = ne1000.Ne1000(dev, ADDRESS)
pump.diameter_mm(DIA)
pump.volume(volume)
pump.rate(rate)
pump.direction_withdraw()
#pump.direction_infuse()
pump.run()
