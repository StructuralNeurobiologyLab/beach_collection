import logging

import time

import adis

import tkinter as tk
from tkinter import messagebox


adis.ne1000_log_init(stream_handler_level=logging.DEBUG)

dev = adis.Pt104()
dev.open()

CH1 = adis.Pt104TempCh(dev, 1)
CH2 = adis.Pt104TempCh(dev, 2)

while True:

    try:

        T1 = CH1.read()

        T2 = CH2.read()

        if T2 > 30:
            print("too hot")

            root = tk.Tk()
            root.withdraw()

            messagebox.showerror("Error", "The Temperature at the knife is getting too hot")

           # root.mainloop()

            time.sleep(1)

        elif T2 <= 25:
            time.sleep(1)

    except (adis.PicoNoSamplesAvailableError, adis.PicoRepeatValueError):

        pass

    time.sleep(4)