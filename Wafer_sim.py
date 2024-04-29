# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 19:46:30 2024

@author: laura
"""
import matplotlib.pyplot as plt
import numpy as np

def square(width=30, length=55, standoff=5):
    wafer = np.zeros((508,508))

    for x in range(254): # create the wafer
        y1= 254 - int(np.sqrt(254**2-x**2))
        y2= 253 + int(np.sqrt(254**2-x**2))
        wafer[253+x, y1:y2] = 1
        wafer[254-x, y1:y2] = 1

    for x in range(204): # create the part of the wafer that can be filled
        y1= 254 - int(np.sqrt(204**2-x**2))
        y2= 253 + int(np.sqrt(204**2-x**2))
        wafer[253+x, y1:y2] = 2
        wafer[254-x, y1:y2] = 2

    section_x = width
    section_y = length

    distance = standoff

    w_a = np.sum(wafer == 2)


    x=0
    y=0
    midpoints = []
    while x < 508-section_x:
        s = False # check if any slices have been set
        while y < 508-section_y:
            if np.all(wafer[x:x+section_x, y:y+section_y] == 2):
                wafer[x:x+section_x, y:y+section_y] = 3
                midpoints.append(((x+section_x/2)/10, (y+section_y/2)/10)) # already recalibrate to mm here
                y += section_y + distance
                s = True
                # plot midpoint 
                #wafer[x+section_x//2, y+section_y//2] = 4
            else:
                y += 1
        if s:
            x += section_x + distance
        else:
            x += 1
        y = 0

    s_a = np.sum(wafer == 3)
    coverage = s_a/w_a

    print("Coverage:", coverage)

    plt.imshow(wafer)
    plt.show()
    # rearange in cover order
    midpoints.sort(key = lambda x: x[0])
    
    # convert to motor axis position
    for i in range(len(midpoints)):
        midpoints[i] = 145 - midpoints[i][0], midpoints[i][1] + 50
    
    
    return midpoints

if __name__ == '__main__':
    print(square()) 