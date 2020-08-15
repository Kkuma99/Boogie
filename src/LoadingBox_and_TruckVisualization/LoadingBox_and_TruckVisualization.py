import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import time
from collections import namedtuple
import numpy as np

# 선언
## 지역
LOCAL_A = 0
LOCAL_B = 1
LOCAL_C = 2
## 지역과 상자 개수
NUM_LOCAL = 3
NUM_BOX = 30
## 트럭 크기(10cm 단위)
W_TRUCK = 45
L_TRUCK = 20
H_TRUCK = 20

## 적재할 상자
InputBox = {0: {'width': 30, 'length': 40, 'height': 20},
            1: {'width': 50, 'length': 60, 'height': 20}}
