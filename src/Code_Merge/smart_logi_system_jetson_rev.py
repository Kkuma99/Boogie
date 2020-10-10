#!/usr/bin/env python
import rospy
from std_msgs.msg import String
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import mpl_toolkits.mplot3d.art3d as art3d
import pyzbar.pyzbar as pyzbar
import cv2

# ROS 통신으로 Host PC에 Data를 전송(Subscribe)하는 함수
def send_data_to_host(boxData):
    pub = rospy.Publisher('chatter',String,queue_size=10)
    rospy.init_node('talker', anonymous = True)
    rate = rospy.Rate(10) # 10hz
    if not rospy.is_shutdown():
        hello_str = boxData
        rospy.loginfo(hello_str)
        pub.publish(hello_str)
        rate.sleep()


# 트랙바를 위한 dummy 함수
def nothing(x):
    pass


# 카메라로 받아오는 영상을 표시할 화면을 설정하는 함수
def set_window():
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    cv2.createTrackbar('threshold', 'image', 0, 255, nothing)  # 트랙바 생성
    cv2.setTrackbarPos('threshold', 'image', 59)  # 트랙바의 초기값 지정


# 상자 인식 알고리즘을 수행하는 함수
def box_detection(img_color, result):
    # 가우시안 블러 적용
    blurred = cv2.GaussianBlur(img_color, (5, 5), 0)

    # 그레이스케일로 변환
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)

    # threshold 설정
    threshold = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    low = cv2.getTrackbarPos('threshold', 'image')  # 트랙바의 현재값을 가져옴
    retval, bin = cv2.threshold(gray, low, 255, cv2.THRESH_BINARY)  # 바이너리 이미지 생성

    # contour 검출
    val, contours, hierarchy = cv2.findContours(bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # 면적이 가장 큰 contour 추출
    max_area = 0
    max_index = -1
    index = -1
    for i in contours:
        area = cv2.contourArea(i)
        index = index + 1
        if area > max_area:
            max_area = area
            max_index = index

    # 원본 이미지에 컨투어 표시
    cv2.drawContours(result, contours, max_index, (0, 255, 0), 3)

    # 컨투어를 둘러싸는 가장 작은 사각형 그리기
    cnt = contours[max_index]
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    result = cv2.drawContours(result, [box], 0, (0, 0, 255), 2)

    return result, box


# 상자의 크기와 바코드 정보를 얻어내는 알고리즘을 수행하는 함수
def get_box_info(img_color, result, box, barcode_data, inputBox, NUM_BOX):
    gray_barcode = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)  # 그레이 스케일로 변환

    # 상자가 화면의 중앙에 왔을 때 크기 측정과 바코드 스캔
    cv2.rectangle(img_color, (310, 0), (330, 480), (255, 0, 0), 1)
    center = box[1][0] + (box[3][0] - box[1][0]) / 2    # 상자 중심 x좌표
    # print(center)
    if img_color.shape[1]/2-10 <= center <= img_color.shape[1]/2+10:    # 상자가 화면의 중앙 부근에 왔을 때
        decoded = pyzbar.decode(gray_barcode)
        for d in decoded:
            x, y, w, h = d.rect
            cv2.rectangle(result, (x, y), (x + w, y + h), (0, 0, 255), 2)

            barcode_data = d.data.decode("utf-8")  # 바코드 인식 결과
            barcode_type = d.type   # 바코드 타입

            # 화면에 바코드 정보 띄우기
            text = '%s (%s)' % (barcode_data, barcode_type)
            cv2.putText(result, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)

            # 박스 픽셀크기 측정
            box_l_pixel = round(np.sqrt((box[2][0] - box[1][0]) ** 2 + (box[1][1] - box[2][1]) ** 2), 0)  # 상자의 픽셀 길이
            box_w_pixel = round(np.sqrt((box[0][0] - box[1][0]) ** 2 + (box[0][1] - box[1][1]) ** 2), 0)  # 상자의 픽셀 너비
            # 박스 실제크기 계산
            box_l = int(round(box_l_pixel/40.8, 0))
            box_w = int(round(box_w_pixel/40.8, 0))

            if not int(barcode_data[1:3]) in inputBox[ord(barcode_data[0])-65]:   # 중복되는 데이터가 없다면
                inputBox[ord(barcode_data[0])-65][int(barcode_data[1:3])] = {'l': box_l, 'w': box_w, 'h': BOX_H}
                NUM_BOX[ord(barcode_data[0])-65] += 1
                print('Size of box: ', box_w, box_l)  # 상자의 크기 출력

    return barcode_data, result


# 트럭 내부 모습을 시각화하는 함수
def draw_truck(x_range, y_range, z_range):
      yy, zz = np.meshgrid(y_range, z_range)
      ax.plot_wireframe(x_range[0], yy, zz, color="black")
      ax.plot_wireframe(x_range[1], yy, zz, color="black")

      xx, zz = np.meshgrid(x_range, z_range)
      ax.plot_wireframe(xx, y_range[0], zz, color="black")
      ax.plot_wireframe(xx, y_range[1], zz, color="black")


# 적재 순서를 계산하는 알고리즘을 수행하는 함수
def calculate_loading_order(NUM_LOCAL, NUM_BOX, TRUCK_L, TRUCK_W, TRUCK_H, inputBox, truck):
    # 각 지역별 상자의 개수만큼 check 생성(check에 각 상자의 적재 여부 저장)
    check = []
    for i in range(0, NUM_LOCAL):
        check.append([])
        for j in range(0, NUM_BOX[i]):
            check[i].append(0)

    sum_num_box = 0  # 각 지역별 적재 범위를 계산하기 위함
    finish = [0, 0, 0]  # 각 지역별 적재 완료된 상자의 개수를 저장할 변수

    ## 측정을 위한 변수
    count_W = 0     # 상자를 적재할 빈 공간의 너비를 측정하기 위한 변수
    count_L = 0     # 막힌 공간의 길이를 측정하기 위한 변수
    count_H = 0     # 막힌 공간의 높이를 측정하기 위한 변수

    ## Loading Box
    for i in range(NUM_LOCAL):  # 각 지역별로 수행
        floor = 0	# 현재 적재하고 있는 층수
        sum_num_box += NUM_BOX[i]   # 앞 지역부터 상자의 개수를 더함

        while True:
            if finish[i] == NUM_BOX[i]:     # 해당 지역 상자들의 적재가 끝나기 전까지 반복
                break

            # endOfL(현재 층에서 가장 작은 길이를 측정하기 위한 변수) 계산
            endOfL = TRUCK_L
            for j in range(TRUCK_W):    # 너비 방향으로 검사
                count_L = 0
                while truck[count_L][j][floor * BOX_H] != 0:    # 빈 공간이 나올때까지 반복
                    if count_L == TRUCK_L-1:    # truck의 인덱스 끝까지 가면 탈출
                        break
                    count_L += 1    # endOfL을 계산하기 위해 count_L을 증가시킴

                if count_L == TRUCK_L-1:    # count_L이 TRUCK_L-1이어서 위 while문을 탈출했다면
                    count_L += 1    # 실제 길이를 구하기 위해 1을 더함
                # endOfL은 길이의 최소값이므로 최소값을 구함
                if count_L < endOfL:
                    endOfL = count_L

            # 한 층에 각 지역에 할당된 길이만큼 적재되었거나 트럭 길이 끝까지 적재된 경우 층수 증가
            if endOfL >= TRUCK_L * (sum_num_box / sum(NUM_BOX)) or endOfL >= TRUCK_L:
                floor += 1
                if floor > TRUCK_H/BOX_H-1:
                    floor = 0

            # 상자를 적재할 위치 계산
            min_L = TRUCK_L     # 적재된 상자들이 차지한 가장 작은 길이(최소값을 찾기 위해 큰 값으로 초기화)
            measureMode = 0	# 측정 모드 플래그: 비어있는 공간의 너비를 측정하고 있으면 1, 아니면 0
            for j in range(TRUCK_L):    # 길이 방향으로 검사
                count_W = 0
                for k in range(TRUCK_W):    # 너비 방향으로 검사
                    if truck[j][k][floor * BOX_H] == 0:  # 0이면(비어있는 공간이면)
                        if measureMode == 0:    # 측정 모드가 아니었다면
                            if j < min_L:   # 적재한 상자들이 차지하는 공간의 길이의 최소값이면
                                measureMode = 1  # 측정 모드로 전환
                                min_L = j   # 최소값 갱신
                                pos_X = j   # 상자를 적재할 x축 좌표 저장
                                pos_Y = k   # 상자를 적재할 y축 좌표 저장
                                pos_Z = floor * BOX_H
                                count_W = 1     # 빈 공간의 너비를 세기 시작함
                        else:   # 측정모드이면
                            count_W += 1   # 상자가 들어갈 수 있는 너비를 측정하기 위해 count_W를 증가
                    else:   # 1 또는 2이면(막혀있는 공간이면)
                        if measureMode == 1:    # 측정 모드였다면
                            measureMode = 0     # 측정 모드 해제
                if count_W > 0:  # 해당 줄에 빈 공간이 있었다면
                    break   # j에 대한 for 문 탈출

            # 적재할 상자 선택(5가지 조건 확인)
            max_box_W = 0	# count_W 너비 안에 들어갈 수 있는 최대 너비의 상자 너비
            for j in range(NUM_BOX[i]):
                cannot_load = 0
                if check[i][j] == 0 and j in inputBox[i]:
                    if inputBox[i][j]['w'] <= count_W:     # 1. 아직 적재하지 않은 상자이고, 너비가 count_W 이하면
                        if inputBox[i][j]['w'] > max_box_W:     # 2. 최대 너비를 가진 상자를 찾음
                            # 3. 해당 위치에 상자를 적재했을 때 트럭 높이를 넘지 않는지 확인
                            count_H = 0     # 해당 위치에 상자 적재 전 높이
                            while truck[pos_X][pos_Y][count_H] != 0:
                                count_H += 1
                            if count_H+inputBox[i][j]['h'] > TRUCK_H:
                                continue

                            # 4. 해당 위치에 상자를 적재했을 때 트럭 길이를 넘지 않는지 확인
                            count_L = 0
                            while truck[count_L][pos_Y][pos_Z] != 0:
                                count_L += 1
                            if count_L+inputBox[i][j]['l'] > TRUCK_L:
                                continue

                            # 5. 적재할 상자의 아래가 막혀있는지 확인
                            if pos_Z - 1 != -1:  # 가장 아래층인 경우 Z좌표가 -1이므로 따로 조건을 줌
                                for x in range(inputBox[i][j]['l']):
                                    for y in range(inputBox[i][j]['w']):
                                        if truck[pos_X+x][pos_Y+y][pos_Z-1] == 0:
                                            cannot_load = 1
                                            break
                                if cannot_load == 1:
                                    continue
                            boxIndex = j  # 이번에 적재할 상자 인덱스 저장
                            max_box_W = inputBox[i][j]['w']  # 최대 너비 갱신
    
            # 상자 적재 또는 빈 공간 채우기
            if max_box_W == 0:  # 해당 공간에 적재할 수 있는 상자가 없다면 빈공간 채우기
                # 2로 채움
                for y in range(count_W):
                    for z in range(BOX_H):
                        truck[pos_X][pos_Y+y][pos_Z+z] = 2
            else:   # 해당 공간에 적재할 수 있는 상자가 있다면 상자 적재
                for x in range(inputBox[i][boxIndex]['l']):
                    for y in range(inputBox[i][boxIndex]['w']):
                        for z in range(inputBox[i][boxIndex]['h']):
                            if i == 0:
                                truck[pos_X + x][pos_Y + y][pos_Z + z] = 3  # A 지역은 3 할당
                            elif i == 1:
                                truck[pos_X + x][pos_Y + y][pos_Z + z] = 4  # B 지역은 4 할당
                            else:
                                truck[pos_X + x][pos_Y + y][pos_Z + z] = 5  # C 지역은 5 할당
    
                finish[i] += 1   # 적재 완료된 상자 수 갱신
                check[i][boxIndex] = 1  # 적재 완료된 상자 체크

                # 상자의 시각화
                # 밑면
                side = Rectangle((pos_X, pos_Y), inputBox[i][boxIndex]['l'], inputBox[i][boxIndex]['w'], fill=True, facecolor=colors[i], edgecolor='black')
                ax.add_patch(side)
                art3d.pathpatch_2d_to_3d(side, z=pos_Z, zdir='z')
                # 윗면
                side = Rectangle((pos_X, pos_Y), inputBox[i][boxIndex]['l'], inputBox[i][boxIndex]['w'], fill=True, facecolor=colors[i], edgecolor='black')
                ax.add_patch(side)
                art3d.pathpatch_2d_to_3d(side, z=pos_Z+inputBox[i][boxIndex]['h'], zdir='z')
                # 뒷면
                side = Rectangle((pos_Y, pos_Z), inputBox[i][boxIndex]['w'], inputBox[i][boxIndex]['h'], fill=True, facecolor=colors[i], edgecolor='black')
                ax.add_patch(side)
                art3d.pathpatch_2d_to_3d(side, z=pos_X, zdir='x')
                # 앞면
                side = Rectangle((pos_Y, pos_Z), inputBox[i][boxIndex]['w'], inputBox[i][boxIndex]['h'], fill=True, facecolor=colors[i], edgecolor='black')
                ax.add_patch(side)
                art3d.pathpatch_2d_to_3d(side, z=pos_X+inputBox[i][boxIndex]['l'], zdir='x')
                # 왼쪽
                side = Rectangle((pos_X, pos_Z), inputBox[i][boxIndex]['l'], inputBox[i][boxIndex]['h'], fill=True, facecolor=colors[i], edgecolor='black')
                ax.add_patch(side)
                art3d.pathpatch_2d_to_3d(side, z=pos_Y, zdir='y')
                # 오른쪽
                side = Rectangle((pos_X, pos_Z), inputBox[i][boxIndex]['l'], inputBox[i][boxIndex]['h'], fill=True, facecolor=colors[i], edgecolor='black')
                ax.add_patch(side)
                art3d.pathpatch_2d_to_3d(side, z=pos_Y+inputBox[i][boxIndex]['w'], zdir='y')

                plt.draw()  # 화면에 plot
                plt.pause(0.0001)

                print("This Box is [%s%02d]"%(chr(i+65), boxIndex)) # 현재 적재한 상자의 정보를 화면에 출력
                input("Press Enter to load next box")   # Enter 키를 입력하면 다음 상자를 적재

    print("Finish loading all your boxes!")
    plt.draw()  # 마지막으로 plot
    plt.pause(60)   # 1분간 유지

# Number of locals and boxes
NUM_LOCAL = 3
NUM_BOX = [0, 0, 0]  # 각 지역별 상자 개수

# 배송 지역
LOCAL_A = 0
LOCAL_B = 1
LOCAL_C = 2

# 트럭의 크기
TRUCK_L = 50    # x
TRUCK_W = 25    # y
TRUCK_H = 25    # z

# Boxes to load
inputBox = {}
BOX_H = 5   # 상자 높이를 5cm로 고정
for i in range(0, NUM_LOCAL):
    inputBox[i] = {}

## 트럭의 상태
truck = np.zeros((TRUCK_L, TRUCK_W, TRUCK_H), dtype=np.int8)

# 바코드 데이터 초기화
barcode_data = "XXX"    

# Read image(640*480)
cap = cv2.VideoCapture('/dev/video1')  # 내장 camera인 경우: 0 / USB camera인 경우: 1
cap.set(cv2.CAP_PROP_FPS, 30) # FPS(프레임속도) 30으로 설정
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # 프레임 너비 640으로 설정
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) # 프레임 높이 480으로 설정

set_window()    # 화면 설정

# 지속적인 영상처리를 위한 while문
while True:
    ret, img_color = cap.read()  # 카메라로부터 이미지를 읽어옴

    # 캡처에 실패할 경우 다시 loop의 첫 줄부터 수행하도록 함
    if not ret:
        continue

    result = img_color.copy()   # 화면에 표시하기 위해 img_color를 result에 복사
    result, box = box_detection(img_color, result)   # 상자 인식
    barcode_data, result = get_box_info(img_color, result, box, barcode_data, inputBox, NUM_BOX)    # 상자 정보

    send_data_to_host(barcode_data) # 바코드 데이터를 Host PC로 전송

    cv2.imshow('LOGI', result)  # 화면에 표시
    if cv2.waitKey(1) & 0xFF == 27:  # 1초 단위로 update되며, ESC키를 누르면 탈출하여 종료
        break

# 영상처리에 사용된 메모리를 해제
cap.release()
cv2.destroyAllWindows()

# 입력받은 모든 상자 정보를 출력
print (inputBox)

# 트럭의 시각화를 위한 설정
fig = plt.figure()
ax = fig.gca(projection='3d')
ax.set_aspect('auto')
colors = ['gold', 'dodgerblue', 'limegreen']

draw_truck(np.array([0, TRUCK_L]), np.array([0, TRUCK_W]), np.array([0, TRUCK_H]))  # 트럭 시각화
calculate_loading_order(NUM_LOCAL, NUM_BOX, TRUCK_L, TRUCK_W, TRUCK_H, inputBox, truck) # 상자 적재 순서 계산 및 시각화