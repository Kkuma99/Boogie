#!/usr/bin/env python
import rospy
from std_msgs.msg import String
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import mpl_toolkits.mplot3d.art3d as art3d
import pyzbar.pyzbar as pyzbar
import cv2


# ROS통신으로 호스트PC에 데이터를 전송(퍼블리시)하는 함수
def send_data_to_host(boxData):
    pub = rospy.Publisher('chatter', String, queue_size=10)
    rospy.init_node('talker', anonymous=True)
    rate = rospy.Rate(10)  # 10hz
    if not rospy.is_shutdown():
        hello_str = boxData
        rospy.loginfo(hello_str)
        pub.publish(hello_str)
        rate.sleep()


# 상자 인식 알고리즘을 수행하는 함수
def box_detection(img_color, result, box):
    ''' 초기 설정 '''
    blurred = cv2.GaussianBlur(img_color, (5, 5), 0) # 가우시안 블러 적용
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY) # 그레이스케일로 변환
    retval, bin = cv2.threshold(gray, 0.2*gray.max(), 255, cv2.THRESH_BINARY) # 바이너리 이미지 생성
    # cv2.imshow('bin', bin) # 생성된 바이너리 이미지 확인
    # cv2.waitKey()

    ''' 이미지 세그멘테이션 '''
    # 노이즈 제거
    kernel = np.ones((5,5),np.uint8) # 커널 크기는 5*5
    # opening = cv2.morphologyEx(bin,cv2.MORPH_OPEN,kernel, iterations = 3) # 오프닝 연산으로 배경 노이즈 제거
    opening = cv2.morphologyEx(bin,cv2.MORPH_CLOSE, kernel, iterations = 3) # 클로징 연산으로 객체 내부 노이즈 제거
    # cv2.imshow('opening', opening) # 모폴로지 연산 후 생성된 바이너리 이미지 확인
    # cv2.waitKey()

    # 확실한 배경 확보
    sure_bg = cv2.dilate(opening, kernel, iterations=3) 

    # 뼈대 이미지
    dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
    result_dist_transform = cv2.normalize(dist_transform, None, 255, 0, cv2.NORM_MINMAX, cv2.CV_8UC1)

    #  확실한 전경 확보
    ret, sure_fg = cv2.threshold(result_dist_transform, 0.7*result_dist_transform.max(),255, cv2.THRESH_BINARY)
    sure_fg = np.uint8(sure_fg)
    sure_fg = cv2.dilate(sure_fg, kernel, iterations = 3) # 전경을 확대해줌
    # cv2.imshow('sure_fg', sure_fg)
    # cv2.waitKey()    

    # 확실한 배경 - 확실한 전경 = 모르는 부분
    unknown = cv2.subtract(sure_bg, sure_fg) 

    # 이미지 라벨링
    ret, markers = cv2.connectedComponents(sure_fg) # 확실한 전경 영역을 라벨링 *마커는 0(배경)부터 지정됨
    markers = markers + 1 # 결과 마커를 하나 증가 시켜서 배경을 1로 설정
    markers[unknown==255] = 0 # 모르는 부분을 0으로 라벨링
    
    # 전경, 배경에 0 이상의 값, 불명확한 것에 0 -> 이 알고리즘이 불명확한 것을 판단 + 경계선을 -1로
    markers = cv2.watershed(img_color, markers)
    img_color[markers == -1] = [0, 0, 0] # 객체의 외곽부분 검정색으로
    img_color[markers == 1] = [0, 0, 0] # 배경 부분은 검정색으로, 객체는 원래 색 그대로
    # cv2.imshow('foreground', img_color) # 알고리즘 적용되어 객체만 추출된 이미지 확인
    # cv2.waitKey()

    ''' 검출된 전경의 꼭짓점 찾기 '''
    # 전경의 꼭짓점을 찾기 위해 코너 디텍트
    img_gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
    corners = cv2.goodFeaturesToTrack(img_gray, 150, 0.01, 5) # 코너를 찾을 이미지, 코너 최대 검출 개수, 코너 강도, 코너 사이의 거리
    
    # 코너로 검출된 점에서 최소 좌표와 최대 좌표를 찾아서 꼭짓점 결정
    pos = [0, 10000, 10000, 0, 0, -1, -1, 0] # x, min_y, min_x, y, x, max_y, max_x, y
    for i in corners:
        x, y = i[0]
        if x > 5 and y > 5 and x < 635 and y < 475: # 카메라 화면의 꼭짓점 검출 방지
            if y < pos[1]: # Y의 최소 좌표 찾기 (왼쪽 상단)
                pos[0] = x
                pos[1] = y
            if x < pos[2]: # X의 최소 좌표 찾기 (왼쪽 하단)
                pos[2] = x
                pos[3] = y
            if y > pos[5]: # Y의 최대 좌표 찾기 (오른쪽 하단)
                pos[4] = x
                pos[5] = y
            if x > pos[6]: # X의 최대 좌표 찾기 (오른쪽 상단)
                pos[6] = x
                pos[7] = y
        # cv2.circle(img_color, (x, y), 3, (0, 0, 255), 2) # 코너에 원으로 표시

    # cv2.imshow('corner', img_color) # 코너가 표시된 이미지 확인
    # cv2.waitKey()
    
    # print(pos)
    # cv2.waitKey()

    if abs(pos[5]-pos[7]) <= 30: # 박스가 카메라에 정방향으로 잡힌다면
        
        # 컨투어 검출
        retval, img_bin = cv2.threshold(img_gray, 1, 255, cv2.THRESH_BINARY)  # 바이너리 이미지 생성
        val, contours, hierarchy = cv2.findContours(img_bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        # 면적이 가장 작은 컨투어(=박스) 추출
        min_area = 1000000
        min_index = -1
        index = -1
        for i in contours:
            area = cv2.contourArea(i)
            index = index + 1
            if area < min_area:
                min_area = area
                min_index = index

        if min_index == -1: # 검출된 컨투어가 없으면
            return result, box  # 이전 상태 그대로 반환

        # 결과 이미지에 컨투어 표시
        # cv2.drawContours(result, contours, min_index, (0, 255, 0), 2)

        ''' 결과 반환: 박스가 카메라와 정방향 '''
        # 컨투어를 둘러싸는 가장 작은 사각형 그리기
        cnt = contours[min_index]
        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)
        box = np.int0(box) # 정수형으로 변경
        result = cv2.drawContours(result, [box], 0, (0, 0, 255), 2) # 찾아낸 꼭짓점을 따라 윤곽선 그려줌
        return result, box # 윤곽선 그려진 전체 이미지, 꼭짓점 반환

    else:
        ''' 결과 반환: 박스가 카메라와 정방향 X '''
        box = ((pos[0], pos[1]), (pos[2], pos[3]), (pos[4], pos[5]), (pos[6], pos[7])) # 꼭짓점 지정
        box = np.int0(box) # 정수형으로 변경
        result = cv2.drawContours(result, [box], 0, (0, 0, 255), 2) # 찾아낸 꼭짓점을 따라 윤곽선 그려줌
        return result, box # 윤곽선 그려진 전체 이미지, 꼭짓점 반환


# 상자의 크기와 바코드 정보를 얻어내는 알고리즘을 수행하는 함수
def get_box_info(img_color, result, box, barcode_data, inputBox, NUM_BOX):
    gray_barcode = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY) # 그레이 스케일로 변환

    ''' 바코드 면적 계산 '''
    retval, bin_barcode = cv2.threshold(gray_barcode, 0.7*gray_barcode.max(), 255, cv2.THRESH_BINARY) # 바이너리 이미지 생성
    kernel = np.ones((5,5), np.uint8)
    opening = cv2.morphologyEx(bin_barcode, cv2.MORPH_CLOSE, kernel, iterations = 3) # 바코드 라벨 컨투어 추출 위해 안쪽을 채워줌
    # cv2.imshow('barcode', opening) # 전처리된 바이너리 이미지 확인
    # cv2.waitKey()

    # 컨투어 검출
    val, contours, hierarchy = cv2.findContours(opening, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # 면적이 가장 큰 컨투어(=바코드) 추출
    max_area = 0
    max_index = -1
    index = -1
    for i in contours:
        area = cv2.contourArea(i)
        index = index + 1
        if area > max_area:
            max_area = area
            max_index = index
    
    # 결과 이미지에 바코드 컨투어 표시
    cv2.drawContours(result, contours, max_index, (0, 0, 255), 2)
    # cv2.imshow('result_barcode', result) # 바코드 컨투어 표시된 이미지 확인
    # print(max_area) # 바코드 면적 확인
    # cv2.waitKey()

    ''' 바코드 정보 읽어오기 '''
    cv2.rectangle(result, (310, 0), (330, 480), (255, 0, 0), 1) # 화면 중앙 표시
    center = box[1][0] + (box[3][0] - box[1][0]) / 2  # 상자 중심 X 좌표

    if img_color.shape[1] / 2 - 10 <= center <= img_color.shape[1] / 2 + 10:  # 상자가 화면의 중앙 부근에 왔을 때
        
        decoded = pyzbar.decode(gray_barcode) # 바코드 스캔

        for d in decoded:
            x, y, w, h = d.rect
            cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 255), 2)

            barcode_data = d.data.decode("utf-8")  # 바코드 인식 결과
            barcode_type = d.type  # 바코드 타입

            # 화면에 바코드 정보 띄우기
            text = '%s (%s)' % (barcode_data[0:3], barcode_type)
            cv2.putText(result, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)

            # 박스 픽셀크기 측정
            box_l_pixel = round(np.sqrt((box[2][0] - box[1][0]) ** 2 + (box[1][1] - box[2][1]) ** 2), 0)  # 상자의 픽셀 길이(가로)
            box_w_pixel = round(np.sqrt((box[0][0] - box[1][0]) ** 2 + (box[0][1] - box[1][1]) ** 2), 0)  # 상자의 픽셀 너비(세로)
            
            # 박스 실제크기 계산
            box_l = int(round(box_l_pixel / 35, 0)) # 길이(가로)
            box_w = int(round(box_w_pixel / 35, 0)) # 너비(세로)
            box_h = int(round((max_area/(640*480))*300, 0)) # 높이 *바코드 면적과 전체화면의 비율에 비례상수 곱하여 계산
            box_k = 20 # 무게
            # box_k = int(barcode_data[3:5]) # 무게
            # print(box_h, box_k)

            if not int(barcode_data[1:3]) in inputBox[ord(barcode_data[0]) - 65]:  # 중복되는 데이터가 없다면
                inputBox[ord(barcode_data[0]) - 65][int(barcode_data[1:3])] = {'l': box_l, 'w': box_w, 'h': box_h, 'k': box_k} # 박스의 정보 담아주기
                NUM_BOX[ord(barcode_data[0]) - 65] += 1 # 박스의 개수 하나 늘려주기
                print('Info of box: %dcm %dcm %dcm %dkg' % (box_w, box_l, box_h, box_k))  # 상자의 정보 출력
                # print('Info of box: ', box_w, box_l, box_h, box_k)  # 상자의 정보 출력

    return result, barcode_data


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
    
    ''' 변수 및 리스트 선언 '''
    # 각 지역별 상자의 개수만큼 배열 생성(각 상자의 적재 여부 저장)
    check = []
    for i in range(0, NUM_LOCAL): # 운송지 개수만큼 카테고리 생성
        check.append([]) # 빈 리스트 생성
        for j in range(0, NUM_BOX[i]): # 박스 개수만큼 빈 리스트에 요소 추가
            check[i].append(0) # 0으로 초기화

    sum_num_box = 0  # 각 지역별 적재 범위를 계산하기 위함, 전체 박스의 개수
    finish = [0, 0, 0]  # 각 지역별 적재 완료된 상자의 개수를 저장할 변수

    count_W = 0  # 상자를 적재할 빈 공간의 너비를 측정하기 위한 변수 (Y축)
    count_L = 0  # 막힌 공간의 길이를 측정하기 위한 변수 (X축)
    count_H = 0  # 막힌 공간의 높이를 측정하기 위한 변수 (Z축)

    ''' 상자 적재 '''
    for i in range(NUM_LOCAL):  # 각 지역별로 수행
        floor = 0  # 현재 적재하고 있는 층수
        sum_num_box += NUM_BOX[i]  # 각 지역의 상자의 개수를 더함
 
        while True:
            if finish[i] == NUM_BOX[i]: break # 해당 지역 상자들의 적재가 끝나면 종료

            # END_L 계산
            END_L = TRUCK_L # 현재 층에서 가장 작은 길이를 측정하기 위한 변수
            for y in range(TRUCK_W): # Y축 방향으로 검사
                count_L = 0
                while truck[count_L][y][floor * BOX_H] != 0:  # 빈 공간이 나올때까지 반복
                    if count_L == TRUCK_L - 1:  # 트럭의 인덱스 끝까지 가면 탈출
                        count_L += 1  # 탈출하기 전 실제 길이를 구하기 위해 1을 더함
                        break
                    count_L += 1  # END_L을 계산하기 위해 count_L을 증가시킴
                if count_L < END_L: END_L = count_L # 최솟값 갱신

            # 한 층에 각 지역에 할당된 길이만큼 적재되었거나, 트럭 길이 끝까지 적재된 경우 층수 증가
            if END_L >= TRUCK_L * (sum_num_box / sum(NUM_BOX)) or END_L >= TRUCK_L: 
                floor += 1
                if floor > TRUCK_H / BOX_H - 1: floor = 0 # 최대 층수를 넘었으면 초기화

            ''' 상자를 적재할 위치 계산 '''
            MIN_L = TRUCK_L  # 적재된 상자들이 차지한 가장 작은 길이
            measureMode = 0  # 플래그: 비어있는 공간의 너비를 측정하고 있으면 1, 아니면 0

            for x in range(TRUCK_L):  # X축 방향으로 검사
                count_W = 0
                for y in range(TRUCK_W):  # Y축 방향으로 검사

                    if truck[x][y][floor * BOX_H] == 0:  # 0이면 (비어있는 공간이면)
                        if measureMode == 0:  # 측정 모드가 아니었다면
                            if x < MIN_L:  # 적재한 상자들이 차지하는 공간의 길이의 최소값이면
                                measureMode = 1  # 측정 모드로 전환
                                MIN_L = x  # 최소값 갱신
                                pos_X = x  # 상자를 적재할 x축 좌표 저장
                                pos_Y = y  # 상자를 적재할 y축 좌표 저장
                                pos_Z = floor * BOX_H # 상자를 적재할 z축 좌표 저장 # 이 부분 수정하면 높이에 따라 적재 가능?
                                count_W = 1  # 빈 공간의 너비를 세기 시작함
                        else:  # 측정모드면
                            count_W += 1  # 상자가 들어갈 수 있는 너비를 측정하기 위해 count_W를 증가

                    else:  # 1 또는 2이면 (막혀있는 공간이면)
                        if measureMode == 1: measureMode = 0  # 측정 모드였다면 측정 모드 해제

                if count_W > 0: break # 해당 줄에 빈 공간이 있었다면 x에 대한 반복문 탈출

            ''' 적재할 상자 선택(5가지 조건 확인) '''
            max_box_W = 0  # count_W 너비 안에 들어갈 수 있는 최대 너비의 상자 너비

            for j in range(NUM_BOX[i]): # 박스 하나하나에 대해 모두 검사
                cannot_load = 0

                if check[i][j] == 0 and j in inputBox[i]:    # 0. 아직 적재하지 않은 상자이고
                    if inputBox[i][j]['w'] <= count_W:       # 1. 너비가 count_W 이하면
                        if inputBox[i][j]['w'] > max_box_W:  # 2. 최대 너비를 가진 상자를 찾음
                            # 이 부분에 무게에 대한 조건 추가? 최대 무게를 가진 상자를 찾음

                            # 3. 해당 위치에 상자를 적재했을 때 트럭 높이를 넘지 않는지 확인
                            count_H = 0  
                            while truck[pos_X][pos_Y][count_H] != 0: count_H += 1 # 해당 위치에 상자 적재 전 높이를 구해줌
                            if count_H + inputBox[i][j]['h'] > TRUCK_H: continue # 높이 넘으면 불합격

                            # 4. 해당 위치에 상자를 적재했을 때 트럭 길이를 넘지 않는지 확인
                            count_L = 0
                            while truck[count_L][pos_Y][pos_Z] != 0: count_L += 1 # 해당 위치에 상자 적재 전 길이를 구해줌
                            if count_L + inputBox[i][j]['l'] > TRUCK_L: continue # 길이 넘으면 불합격

                            # 5. 적재할 상자의 아래가 막혀있는지 확인
                            if pos_Z != 0:  # 가장 아래층인 경우는 제외
                                for x in range(inputBox[i][j]['l']):
                                    for y in range(inputBox[i][j]['w']):
                                        if truck[pos_X + x][pos_Y + y][pos_Z - 1] == 0: # 막혀있지 않다면 # 이 부분 수정하면 높이에 따라 적재 가능?2
                                            cannot_load = 1 # 적재할 수 없음
                                            break
                                if cannot_load == 1: continue # 불합격

                            boxIndex = j  # 적재할 상자 인덱스 저장
                            max_box_W = inputBox[i][j]['w']  # 최대 너비 갱신

            ''' 상자 적재 또는 빈 공간 채우기 '''
            if max_box_W == 0:  # 해당 공간에 적재할 수 있는 상자가 없다면 빈공간 채우기
                for y in range(count_W):
                    for z in range(BOX_H): # 이 부분 수정하면 높이에 따라 적재 가능?3
                        truck[pos_X][pos_Y + y][pos_Z + z] = 2 # 빈공간은 2로 채우기

            else:  # 해당 공간에 적재할 수 있는 상자가 있다면 상자 적재
                for x in range(inputBox[i][boxIndex]['l']):
                    for y in range(inputBox[i][boxIndex]['w']):
                        for z in range(inputBox[i][boxIndex]['h']):
                            if i == 0: truck[pos_X + x][pos_Y + y][pos_Z + z] = 3    # A 지역은 3 할당
                            elif i == 1: truck[pos_X + x][pos_Y + y][pos_Z + z] = 4  # B 지역은 4 할당
                            else: truck[pos_X + x][pos_Y + y][pos_Z + z] = 5         # C 지역은 5 할당
                finish[i] += 1  # 적재 완료된 상자 수 갱신
                check[i][boxIndex] = 1  # 적재 완료된 상자 체크

                ''' 상자의 시각화 '''
                # 밑면
                side = Rectangle((pos_X, pos_Y), inputBox[i][boxIndex]['l'], inputBox[i][boxIndex]['w'], fill=True, facecolor=colors[i], edgecolor='black')
                ax.add_patch(side)
                art3d.pathpatch_2d_to_3d(side, z=pos_Z, zdir='z')
                # 윗면
                side = Rectangle((pos_X, pos_Y), inputBox[i][boxIndex]['l'], inputBox[i][boxIndex]['w'], fill=True, facecolor=colors[i], edgecolor='black')
                ax.add_patch(side)
                art3d.pathpatch_2d_to_3d(side, z=pos_Z + inputBox[i][boxIndex]['h'], zdir='z')

                # 뒷면
                side = Rectangle((pos_Y, pos_Z), inputBox[i][boxIndex]['w'], inputBox[i][boxIndex]['h'], fill=True, facecolor=colors[i], edgecolor='black')
                ax.add_patch(side)
                art3d.pathpatch_2d_to_3d(side, z=pos_X, zdir='x')
                # 앞면
                side = Rectangle((pos_Y, pos_Z), inputBox[i][boxIndex]['w'], inputBox[i][boxIndex]['h'], fill=True, facecolor=colors[i], edgecolor='black')
                ax.add_patch(side)
                art3d.pathpatch_2d_to_3d(side, z=pos_X + inputBox[i][boxIndex]['l'], zdir='x')

                # 왼쪽
                side = Rectangle((pos_X, pos_Z), inputBox[i][boxIndex]['l'], inputBox[i][boxIndex]['h'], fill=True, facecolor=colors[i], edgecolor='black')
                ax.add_patch(side)
                art3d.pathpatch_2d_to_3d(side, z=pos_Y, zdir='y')
                # 오른쪽
                side = Rectangle((pos_X, pos_Z), inputBox[i][boxIndex]['l'], inputBox[i][boxIndex]['h'], fill=True,facecolor=colors[i], edgecolor='black')
                ax.add_patch(side)
                art3d.pathpatch_2d_to_3d(side, z=pos_Y + inputBox[i][boxIndex]['w'], zdir='y')

                plt.draw() # 화면에 그리기
                plt.pause(0.0001)
                print("This Box is [%s%02d]" % (chr(i + 65), boxIndex)) # 현재 적재한 상자의 정보를 화면에 출력
                input("Press Enter to load next box") # 엔터 입력하면 다음 상자 적재

    print("Finish loading all your boxes!")
    plt.draw()    # 마지막으로 그려주기
    plt.pause(60) # 1분 유지


# ------------------------------------------------------------ main ------------------------------------------------------------


# 운송지와 박스의 개수
NUM_LOCAL = 3 # A, B, C
NUM_BOX = [0, 0, 0]  # 각 지역별 상자 개수

# 배송 지역
LOCAL_A = 0
LOCAL_B = 1
LOCAL_C = 2

# 박스 정보
BOX_H = 5     # 상자 높이
box = ()      # 박스의 윤곽을 그리기 위한 튜플
inputBox = {} # 박스의 정보를 담는 딕셔너리
for i in range(0, NUM_LOCAL):
    inputBox[i] = {}

# 트럭의 크기, 상태
TRUCK_L = 30  # x
TRUCK_W = 15  # y
TRUCK_H = 15  # z
truck = np.zeros((TRUCK_L, TRUCK_W, TRUCK_H), dtype=np.int8)

# 바코드 데이터 초기화
barcode_data = "XXX"

# 이미지 읽어오기 (640*480)
cap = cv2.VideoCapture('/dev/video1')      # 내장카메라: 0 / USB카메라: 1
cap.set(cv2.CAP_PROP_FPS, 30)              # 프레임속도 30으로 설정
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)     # 프레임 너비 640으로 설정
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)    # 프레임 높이 480으로 설정
cv2.namedWindow('LOGI', cv2.WINDOW_NORMAL) # 화면 설정

# 지속적인 영상처리를 위한 루프
while True:
    ''' 1. 이미지 읽어오기 '''
    ret, img_color = cap.read() # 카메라로부터 이미지를 읽어옴
    if not ret: continue        # 캡처에 실패할 경우 반복문의 첫 줄부터 수행하도록 함
    result = img_color.copy()   # 원본 이미지를 결과 이미지에 복사

    ''' 2. 상자 인식 및 정보 전송 '''
    result, box = box_detection(img_color, result, box)  # 상자 인식
    result, barcode_data = get_box_info(img_color, result, box, barcode_data, inputBox, NUM_BOX)  # 상자 정보
    send_data_to_host(barcode_data)  # 바코드 데이터를 Host PC로 전송
    cv2.imshow('LOGI', result)  # 화면에 표시

    ''' 3. 종료 '''
    if cv2.waitKey(1) & 0xFF == 27:  # 1초 단위로 업데이트되며, ESC키를 누르면 탈출하여 종료
        send_data_to_host("END")  # 종료 상태 전송
        break

# 영상처리에 사용된 메모리를 해제
cap.release()
cv2.destroyAllWindows()

# 입력받은 모든 상자 정보를 출력
print(inputBox)

''' 4. 트럭에 상자 적재 '''
# 트럭의 시각화를 위한 설정
fig = plt.figure()
ax = fig.gca(projection='3d')
ax.set_aspect('auto')
colors = ['gold', 'dodgerblue', 'limegreen']

draw_truck(np.array([0, TRUCK_L]), np.array([0, TRUCK_W]), np.array([0, TRUCK_H]))  # 트럭 시각화
calculate_loading_order(NUM_LOCAL, NUM_BOX, TRUCK_L, TRUCK_W, TRUCK_H, inputBox, truck)  # 상자 적재 순서 계산 및 시각화
