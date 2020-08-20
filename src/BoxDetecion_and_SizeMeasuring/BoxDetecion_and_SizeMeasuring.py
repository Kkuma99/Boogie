import numpy as np
import cv2

# 트랙바를 위한 dummy 함수
def nothing(x):
    pass

# Read image
# img = cv2.imread('box-1.jpg')
cap = cv2.VideoCapture(1)  # 내장 camera인 경우: 0 / USB camera인 경우: 1

cv2.namedWindow('image', cv2.WINDOW_NORMAL)
cv2.createTrackbar('threshold', 'image', 0, 255, nothing)  # 트랙바 생성
cv2.setTrackbarPos('threshold', 'image', 127)  # 트랙바의 초기값 지정

while (True):
    ret, img_color = cap.read()  # 카메라로부터 이미지를 읽어옴

    # 캡처에 실패할 경우 다시 loop의 첫 줄부터 수행하도록 함
    if ret == False:
        continue

    # Gaussian blur
    blurred = cv2.GaussianBlur(img_color, (5, 5), 0)

    # Convert to graysscale
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)

    # Autocalculate the thresholding level
    threshold = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Threshold
    low = cv2.getTrackbarPos('threshold', 'image')  # 트랙바의 현재값을 가져옴
    retval, bin = cv2.threshold(gray, low, 255, cv2.THRESH_BINARY)    # 트랙바의 threshold값 받아옴
    retval, bin = cv2.threshold(gray, low, 255, cv2.THRESH_BINARY)  # 새천년관 1006호에서 threshold: 142

    # Find contours
    contours, hierarchy = cv2.findContours(bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

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
    cv2.drawContours(img_color, contours, max_index, (0, 255, 0), 3)
    # cv2.imwrite("box-1-biggest-contour.png", img)

    # Draw a rotated rectangle of the minimum area enclosing our box (red)
    cnt = contours[max_index]
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect)
    box = np.int0(box)

    img_color = cv2.drawContours(img_color, [box], 0, (0, 0, 255), 2)

    # Show original picture with contour
    cv2.imshow('image', img_color)

    if cv2.waitKey(1) & 0xFF == 32: # 스페이스바를 누르면 상자의 픽셀 크기 측정
        box_w_pixel = round(np.sqrt((box[0][0] - box[1][0]) ** 2 + (box[0][1] - box[1][1]) ** 2), 0)  # 상자의 픽셀 너비
        box_l_pixel = round(np.sqrt((box[2][0] - box[1][0]) ** 2 + (box[1][1] - box[2][1]) ** 2), 0)  # 상자의 픽셀 길이
        print('Size of box: ', box_w_pixel, box_l_pixel)

    if cv2.waitKey(1) & 0xFF == 27:  # 1초 단위로 update되며, esc키를 누르면 탈출하여 종료
        break

cap.release()
cv2.destroyAllWindows()