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
NUM_BOX = [1, 2, 3]  # 각 지역별 상자 개수

## Locals
LOCAL_A = 0
LOCAL_B = 1
LOCAL_C = 2

## Size of truck(1cm unit)
TRUCK_W = 25    # y
TRUCK_L = 50    # x
TRUCK_H = 25    # z

## Boxes to load
inputBox = {}
BOX_H = 5   # 상자 높이를 5cm로 고정
for i in range(0, NUM_LOCAL):
    inputBox[i] = {}
for i in range(0, NUM_LOCAL):
    for j in range(0, NUM_BOX[i]):
        inputBox[i][j] = {'w': 0, 'l': 0, 'h': 0}
### Sample
for i in range(0, NUM_LOCAL):
    for j in range(0, NUM_BOX[i]):
        w = 5
        l = 5
        # w = random.randint(1, 7)
        # l = random.randint(1, 7)
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
truck = np.zeros((TRUCK_L, TRUCK_W, TRUCK_H), dtype=np.int8)

##
#endOfW = 0
endOfL = 0
#endOfH = 0

count_W = 0 # 상자를 적재할 빈 공간의 너비를 측정하기 위한 변수
count_L = 0 # endOfL을 계산하기 위해 막힌 공간의 길이를 측정하기 위한 변수
count_H = 0

min_L = 0   # 적재된 차지한 가장 작은 길이
# floor = 0   # 현재 적재하고 있는 층수
boxIndex = 0    # 이번에 적재할 상자의 인덱스
max_box_W = 0   # count_W 너비 안에 들어갈 수 있는 최대 너비의 상자 너비
measureMode = 0     # 측정 모드 플래그: 비어있는 공간의 너비를 측정하고 있으면 1, 아니면 0

## Position of box to load(원점과 가장 가까운 좌표)
pos_X = 0
pos_Y = 0
pos_Z = 0

## 각 지역별 적재 완료된 상자의 개수를 저장할 변수
finish = [0, 0, 0]





# Main Code

## Box Detection

## Barcode Detection

## Loading Box
for i in range(NUM_LOCAL):  # 각 지역별로 수행
    floor = 0
    endOfL = 0
    while endOfL < TRUCK_L * (NUM_BOX[i] / sum(NUM_BOX)):    # 한 층에 각 지역에 할당된 길이만큼 적재되기 전까지
        if finish[i] == NUM_BOX[i]:     # 해당 지역 상자들의 적재가 끝나기 전까지 반복
            break
        min_L = TRUCK_L     # 최소값을 찾기 위해 큰 값으로 초기화
        # 상자를 적재할 위치 계산
        for j in range(TRUCK_L):    # 길이 방향으로 검사
            for k in range(TRUCK_W):    # 너비 방향으로 검사
                if truck[j][k][floor * BOX_H] == 0:  # 0이면(비어있는 공간이면)
                    if measureMode == 0:    # 측정 모드가 아니었다면
                        if j < min_L:   # 적재한 상자들이 차지하는 공간의 길이의 최소값이면
                            measureMode = 1  # 측정 모드로 전환
                            min_L = j   # 최소값 갱신
                            pos_X = min_L   # 상자를 적재할 x축 좌표 저장
                            pos_Y = k   # 상자를 적재할 y축 좌표 저장
                            pos_Z = floor * BOX_H
                            count_W = 1     # 빈 공간의 너비를 세기 시작함
                    else:
                        count_W += 1   # 상자가 들어갈 수 있는 너비를 측정하기 위함
                else:   # 1 또는 2이면(막혀있는 공간이면)
                    if measureMode == 1:    # 측정 모드였다면
                        measureMode = 0     # 측정 모드 해제
            if count_W != 0:  # 해당 줄에 빈 공간이 있었다면
                break   # j에 대한 for 문 탈출
        print(pos_X, pos_Y, pos_Z)
        print(count_W)
        # 적재할 상자 선택
        max_box_W = 0
        for j in range(NUM_BOX[i]):
            cannot_load = 0
            if check[i][j] == 0 and inputBox[i][j]['w'] <= count_W:     # 아직 적재하지 않은 상자이고, 너비가 count_W 이하면
                if inputBox[i][j]['w'] > max_box_W:     # 최대 너비를 가진 상자를 찾음
                    # 적재할 수 있는지 확인
                    for x in range(inputBox[i][j]['l']):
                        for y in range(inputBox[i][j]['w']):
                            # 적재할 상자의 아래가 막혀있는지 확인
                            if truck[pos_X+x][pos_Y+y][pos_Z-1] == 0:
                                cannot_load = 1
                                break
                        if cannot_load == 1:
                            break
                    if cannot_load == 1:
                        continue
                    # 해당 위치에 상자를 적재했을 때 트럭 높이를 넘지 않는지 확인
                    count_H = 0     # 해당 위치에 상자 적재 전 높이
                    while truck[pos_X][pos_Y][count_H] != 0:
                        count_H += 1
                    if count_H+inputBox[i][j]['h'] <= TRUCK_H:
                        boxIndex = j  # 상자 인덱스 저장
                        max_box_W = inputBox[i][j]['w']  # 최대 너비 갱신
                    else:
                        continue
        # 상자 적재 또는 빈 공간 채우기
        if max_box_W == 0:  # 해당 공간에 적재할 수 있는 상자가 없다면
            # 2로 채움
            for y in range(count_W):
                for z in range(BOX_H):
                    truck[pos_X][pos_Y+y][pos_Z+z] = 2
        else:   # 해당 공간에 적재할 수 있는 상자가 있다면
            # 1로 채움
            for x in range(inputBox[i][boxIndex]['l']):
                for y in range(inputBox[i][boxIndex]['w']):
                    for z in range(inputBox[i][boxIndex]['h']):
                        truck[pos_X + x][pos_Y + y][pos_Z + z] = 1
            finish[i] += 1   # 적재 완료된 상자 수 갱신
            check[i][boxIndex] = 1
            ##### display
        max_box_W = 0

        # endOfL 계산
        count_L = 0
        endOfL = TRUCK_L
        for j in range(TRUCK_W):
            while truck[count_L][j][floor * BOX_H] != 0:
                count_L += 1
            if count_L < endOfL:
                endOfL = count_L

    floor = floor + 1   # 층이 꽉 찼으므로 다음 층에 적재
