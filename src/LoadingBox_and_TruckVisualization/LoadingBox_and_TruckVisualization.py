import matplotlib.pyplot as plt
import numpy as np
from itertools import product
from matplotlib.patches import Rectangle
import mpl_toolkits.mplot3d.art3d as art3d
import time
import random


# Define
## Number of locals and boxes
NUM_LOCAL = 3
NUM_BOX = [10, 12, 14]

## Locals
LOCAL_A = 0
LOCAL_B = 1
LOCAL_C = 2

## Size of truck(10cm unit)
TRUCK_W = 25	# y
TRUCK_L = 51	# x
TRUCK_H = 25	# z

## Boxes to load
inputBox = {}
BOX_H = 2
for i in range(0, NUM_LOCAL):
    inputBox[i] = {}
for i in range(0, NUM_LOCAL):
    for j in range(0, NUM_BOX[i]):
        inputBox[i][j] = {'w':0, 'l':0, 'h':0}
### Sample
for i in range(0, NUM_LOCAL):
    for j in range(0, NUM_BOX[i]):
        w = random.randint(1, 10)
        l = random.randint(1, 10)
        inputBox[i][j]['w'] = w
        inputBox[i][j]['l'] = l
        inputBox[i][j]['h'] = BOX_H
print(inputBox)

## Loading status of boxes
check = []
for i in range(0, NUM_LOCAL):
    check.append([])
for i in range(0, NUM_LOCAL):
    for j in range(0, NUM_BOX[i]):
        check[i].append(0)
print(check)

## Truck status
truck = np.zeros((TRUCK_L, TRUCK_W, TRUCK_H), dtype = np.int8)

##
#endOfW = 0
#endOfL = 0
#endOfH = 0

count_W = 0
count_L = 0

min_L = 0
floor = 0
boxIndex = 0
max_box_W = 0

## Position of box to load now
pos_X = 0
pos_Y = 0
pos_Z = 0

## 
finish = [0, 0, 0]


# Main Code

#while endOfW < TRUCK_W:
for i in range(NUM_LOCAL):
    while finish[i] == 0:
        while min_L < 15 * i:
            ##### if height is full, go to 1st floor
            for j in range(TRUCK_W):
                if truck[0][j][floor] == 0:
                    count_L = j
                    count_W = count_W + 1
                    if count_L < min_L:
                        min_L = count_L
                        pos_X = min_L
                        pos_Y = pos_Y + count_W
                        count_W = 0
            for j in range(NUM_BOX[i]):
                if check[i][j] == 0 and inputBox[i][j]['w'] <= count_W:
                    if inputBox[i][j]['w'] > max_box_W:
                        boxIndex = j
                        max_box_W = inputBox[i][j]['w']
            if max_box_W == 0:
                ##### fill with 2
            else:
                ##### load the box and fill with 1
                ##### display with 3D
        floor = floor + BOX_H
