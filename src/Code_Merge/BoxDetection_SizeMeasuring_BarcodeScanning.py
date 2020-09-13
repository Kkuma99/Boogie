import numpy as np
import pyzbar.pyzbar as pyzbar
import cv2


# 트랙바를 위한 dummy 함수
def nothing(x):
    pass


# Read image(640*480)
cap = cv2.VideoCapture(1)  # 내장 camera인 경우: 0 / USB camera인 경우: 1
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

cv2.namedWindow('image', cv2.WINDOW_NORMAL)
cv2.createTrackbar('threshold', 'image', 0, 255, nothing)  # 트랙바 생성
cv2.setTrackbarPos('threshold', 'image', 127)  # 트랙바의 초기값 지정

text = "NONE"
x = y = w = h = 0
barcode_data = 0

while True:
    ret, img_color = cap.read()  # 카메라로부터 이미지를 읽어옴
    #img_color = cv2.resize(img_color, (640, 480))

    # 캡처에 실패할 경우 다시 loop의 첫 줄부터 수행하도록 함
    if not ret:
        continue

    # Gaussian blur
    blurred = cv2.GaussianBlur(img_color, (5, 5), 0)

    # Convert to graysscale
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    gray_barcode = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)

    # Autocalculate the thresholding level
    threshold = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Threshold
    low = cv2.getTrackbarPos('threshold', 'image')  # 트랙바의 현재값을 가져옴
    retval, bin = cv2.threshold(gray, low, 255, cv2.THRESH_BINARY)  # 트랙바의 threshold값 받아옴
    # retval, bin = cv2.threshold(gray, low, 255, cv2.THRESH_BINARY)  # 새천년관 1006호에서 threshold: 142

    # Find contours
    val, contours, hierarchy = cv2.findContours(bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE) # Jetson
    # contours, hierarchy = cv2.findContours(bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE) # Window

    # Sort out the biggest contour (biggest area)
    max_area = 0
    max_index = -1
    index = -1

    for i in contours:
        area = cv2.contourArea(i)
        index = index + 1
        if area > max_area:
            max_area = area
            max_index = index

    # Draw the raw contours
    cv2.drawContours(img_color, contours, max_index, (0, 255, 0), 2)

    # Draw a rotated rectangle of the minimum area enclosing our box (red)
    cnt = contours[max_index]
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    img_color = cv2.drawContours(img_color, [box], 0, (0, 0, 255), 1)

    # 상자가 화면의 중심에 왔을 때 크기 측정과 바코드 스캔
    center = box[1][0] + (box[3][0] - box[1][0]) / 2
    print(center)
    if img_color.shape[1]/2-10 <= center <= img_color.shape[1]/2+10:
        box_w_pixel = np.sqrt((box[0][0] - box[1][0]) ** 2 + (box[0][1] - box[1][1]) ** 2)  # 상자의 픽셀 너비
        box_l_pixel = np.sqrt((box[2][0] - box[1][0]) ** 2 + (box[1][1] - box[2][1]) ** 2)  # 상자의 픽셀 길이
        box_w = int(round(box_w_pixel/40.8, 0))
        box_l = int(round(box_l_pixel/40.8, 0))
        print('Size of box: ', box_w, box_l)  # 상자의 픽셀 크기 출력
        decoded = pyzbar.decode(gray_barcode)
        for d in decoded:
            x, y, w, h = d.rect

            barcode_data = d.data.decode("utf-8")  # 바코드 인식 결과
            barcode_type = d.type

            cv2.rectangle(img_color, (x, y), (x + w, y + h), (0, 0, 255), 2)

            text = '%s (%s)' % (barcode_data, barcode_type)
            # 화면에 바코드 정보 띄우기
            cv2.putText(img_color, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)

            box_w_pixel = round(np.sqrt((box[0][0] - box[1][0]) ** 2 + (box[0][1] - box[1][1]) ** 2), 0)  # 상자의 픽셀 너비
            box_l_pixel = round(np.sqrt((box[2][0] - box[1][0]) ** 2 + (box[1][1] - box[2][1]) ** 2), 0)  # 상자의 픽셀 길이
            print('Size of box: ', box_w_pixel, box_l_pixel)  # 상자의 픽셀 크기 출력
            print(barcode_data)  # 바코드 인식 결과 출력

    # Show original picture with contour
    cv2.imshow('image', img_color)

    if cv2.waitKey(1) & 0xFF == 27:  # 1초 단위로 update되며, esc키를 누르면 탈출하여 종료
        break

cap.release()
cv2.destroyAllWindows()
