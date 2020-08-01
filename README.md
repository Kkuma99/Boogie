# Boogie the Guider 정리 블로그

## 개요
- 프로젝트명: Boogie The Guider
- 참여자: 강민지(wbclair7@konkuk.ac.kr), 권미경(kmk3942@konkuk.ac.kr) [2명]
- 프로젝트 일자: 2019년 12월 ~ 진행중
- 주제: Turtlebot3 Waffle과 Open Manipulator를 이용한 건물 안내로봇 제작

현재 이 블로그는 연구상황 정리, 참고 자료 정리와 더불어 다른 사람들이 진행 시 겪을 수 있는 오류에 보탬이 되고자 개설하게 되었다. 진행 상황과 더불어 참고한 문헌 혹은 참고할만한 문헌, 에러 해결 방법 등에 대해서 올릴 예정이다.

-------------
## 2020년도 겨울방학 이전 진행상황
- 기존의 RaspberryPi 대신 Jetson TX2를 Turtlebot에 탑재하여 개발환경 구축(Ubuntu 16.04 / ROS kinetic)
- 259장의 이미지를 YOLO training 후 화살표 이미지 detect 성공

```
Jetson TX2의 환경 구축단계에 상당한 시행착오를 겪었음. 
단계는 다음과 같다 ->

- Jetson TX2에 최신 버전인 jetpack 4.3을 설치 (우분투 18.04 버전으로 ROS melodic 버전이 stable하지 않았음)

- Jetpack 다운그레이드를 위하여 초기화를 하고 우분투 16.04로 변경하였음. 
jetpack 3.3.1을 사용하였으나 설치과정에서 중간에 필요한 툴들이 깔리지 않았음.

이에 이어 OpenCV 및 CUDA와 CUdnn을 직접 설치하였으나 내장 메모리의 부족 단계로 다시 초기화를 진행

- Jetpack 3.3.1을 재설치
```

--------------
## 2020.03.05

### TIP (참고용)
-리눅스에서 압축풀기: 
https://dbrang.tistory.com/625


- **Jetpack 3.3.1로 새로 설치**
  - 이전에 설치한 Jetpack에서 OpenCV와 Cuda, Cudnn이 제대로 설치되지 않아 개별적으로 설치해서 용량이 부족하다고 판단했기 때문
  
  [참고사이트](https://www.guruhong.com/33)

  이전에 설치되어 있던것에서 재설치가 완벽하게 진행되었음.
  
  이전에는 CUDA 및 CUdnn의 경우 root단에서 확인해보면 실제로 안깔려 있었음.
  jetpack 설치를 다양한 노트북으로 진행했는데 성능의 차이인가 라는 의문이 있음.

  tip -> 재설치를 하게 되는 경우 wifi보단 랜선을 연결하여 설치를 진행하는게 편하다. 또한 반드시 허브를 준비할 것

- **500G SSD 사용하기로 결정**
  - 64G SD 사용하려고 했으나 500G가 더 안정적이라고 판단했기 때문
  - 메모리 문제를 해결하고 다양한 필요 프로그램 설치에 어려움을 없앤다.
  - 사용할 SSD: BARACUDA SATA SSD
  
---

## 2020.03.06
- **SSD로 부팅 설정**
  - Booting Rootfs off SD Card on Jetson TX1

  ssd 를 젯슨에 연결하게 되면 재부팅을 진행한다. 처음에 연결하고 ssd를 확인할 수 없었으나 재부팅 후 확인 가능했음.

  진행 방법: https://www.youtube.com/watch?v=ZpQgRdg8RmA&t=377s

  유튜브에서 시키는대로 따라하면 거의 진행은 가능하다.

  ```
  해결하지 못한 문제점:
  현재 젯팩 3.3.1을 이용하고 있는데 커널이 최신버전으로 올라와 있다.
  git에서 예전 버전을 찾았지만 sh명령어 실행도중 에러가 발생함.
  ```

---

## 2020.03.09
### Kernel과의 싸움
- **SSD를 주메모리로 설정**
참고: Youtube video `Develop on SSD - NVIDIA Jetson TX Dev Kits`
https://www.youtube.com/watch?v=ZpQgRdg8RmA 하던 중에

  `./makeKernel.sh`에서 오류남:
          ```
          recipe for target 'drivers' failed
          ```
      - 그래서 구글링
      https://devtalk.nvidia.com/default/topic/1019770/error-when-building-device-tree-in-l4t-28-1-for-jetson-tx1/
      
    위 링크에서 NVIDA Guide 링크 있어서 참고하여 시도 : `NVIDIA Tegra Linux Driver Package Development Guide`
      https://docs.nvidia.com/jetson/archives/l4t-archived/l4t-271/index.html
      - 하다가 에러가 발생하여 중도에 멈춤

- **opencv3.4.6으로 upgrade**
    - 사용했던 Jetpack 3.3.1에 내장된 opencv3.3.1으로는 gstreamer가 작동하지 않기 때문
    - OpenCV를 다운받고 귀가

- 다음에 할 일 OpenCV 확인하기
    
---

## 2020.03.10
- 오자마자 opencv upgrade 돌려놓은거에 권한 잠겨있어서 암호 입력함

  ... 프로젝트 할 때는 무조건 화면 보호기 끄고 가기
  
- **USB Cam 실행을 위한 설정**
  - OpenCV 3.4.6으로 upgrade 성공 했는데도
      ```
      ~/project/jetson_nano/opencv$ python tegra-cam.py
      ```
      내장 Camera 실행이 안됨
      ```
      ImportError: No module named cv2
      ```
  - 서치 결과 python용 opencv가 설치되지 않아 생긴 문제로 판단
    - python opencv 설치 시도
        ```
        pip install opencv-python
        ```
        : 에러
        ```
        sudo apt install python-opencv
        ```
        : cv2 import 성공
  - 근데 다른 에러남
- **built in 카메라 실행 성공**
  - `use camera on jetson TX2` 
  https://devtalk.nvidia.com/default/topic/1022265/jetson-tx2/use-camera-on-jetson-tx2/
    - Honey_Patouceul
        ```
        Still unclear what is your use case, but I'll try to summarize:

        The onboard camera is a bayer sensor.

        If you access it through v4l2 interface, you'll get bayer format into CPU memory. Try:
        v4l2-ctl -d /dev/video0 --list-formats

        If you access it through gstreamer interface, then plugin nvcamerasrc can provide different formats (I420, NV12...) into NVMM memory. Try:
        gst-inspect-1.0 nvcamerasrc
        and see its src capabilities.
        For example:
        gst-launch-1.0 nvcamerasrc ! 'video/x-raw(memory:NVMM),width=640, height=480, framerate=30/1, format=NV12' ! nvvidconv flip-method=2 ! nvegltransform ! nveglglessink -e
        should show your camera capture in a window. Other plugins may convert into many other formats. Searching this forum you should find many examples.

        You may also have a look to Tegra MultiMedia API and Argus, depending on what you intend to do with it.
        ```
    - 핵심:
        ```
        gst-launch-1.0 nvcamerasrc ! 'video/x-raw(memory:NVMM),width=640, height=480, framerate=30/1, format=NV12' ! nvvidconv flip-method=2 ! nvegltransform ! nveglglessink -e
        ```
- **USB Cameara 실행 성공**
  참고: `How to Capture and Display Camera Video with Python on Jetson TX2`
  https://jkjung-avt.github.io/tx2-camera-with-python/
  ```
  $ python3 tegra-cam.py --usb --vid 1 --width 1280 --height 720
  ```
- 다음에 도전해볼 것
    `How to Capture Camera Video and Do Caffe Inferencing with Python on Jetson TX2`
    https://jkjung-avt.github.io/tx2-camera-caffe/

- **Darknet 설치**
  - 이전에 뜬 에러 `Video-stream stopped`로 인해 다른 다크넷(https://github.com/AlexeyAB/darknet) 설치
  참고: `Video-stream stopped! error`
  https://github.com/stereolabs/zed-yolo/issues/11
    - image_opencv.cpp 파일 수정
    참고: https://github.com/dlwnstjr2004/EskerJuneA/tree/master/src
    - makefile 실패
  - 이전에 설치했던 다크넷(https://github.com/pjreddie/darknet.git)으로 다시 설치함

- **Yolo mark 설치**
  참고: `[5] YOLO 데이터 학습`
  https://juni-94.tistory.com/10?category=802791

- **ROS 설치**
  참고: `ROBOTIS e-Manual Turtlebot3`
  http://emanual.robotis.com/docs/en/platform/turtlebot3/raspberry_pi_3_setup/#raspberry-pi-3-setup

---

## 2020.03.12.

- **OpenCR 재설치**
  - Ubuntu에서 Arduino IDE 실행 안됨
  - 민지 개인노트북에 Arduino IDE 설치하여 OpenCR board에 16.04 버전으로 재설치

---

## 2020.03.16.
- **SLAM 시도(실패)**
  - SLAM 시도해 보려고 했으나 turtlebot bringup에서 오류
    ```
    [ERROR] [1584332348.587128343]: An exception was thrown: open: No such file or directory
    ``` 
    ```
    [ERROR] [1584332750.539349148]: An exception was thrown: open: No such file or directory
    [ERROR] [1584332751.183600]: Error opening serial: [Errno 2] could not open port /dev/ttyACM0: [Errno 2] No such file or directory: '/dev/ttyACM0'
    ```
  - 계속 ttyACM0 포트 관련해서 에러메세지가 뜨는데 구글링해도 답이 안나옴
  - 문득 Jetson의 USB 포트가 3.0인데, 사용하고 있던 USB Hub의 포트가 2.0인 것을 보고 그 문제가 원인인 것으로 예상 - Hub를 바꿔보기로 결정

---

## 2020.03.17.
- **ttyACM0 문제 해결**
  - USB Hub 3.0으로 변경했더니 bringup 잘되고 포트 에러도 안남
- **SLAM 재시도**
  - launch는 다 되는데 teleop 실행 후 조작이 안됨

---

## 2020.03.21.
### OpenCR 보드에 귀신들림..
- **OpenCR 확인**
  - OpenCR 확인을 위해 로봇 분해
  - OpenCR의 PUSH Sw1을 눌러 DXL의 작동을 확인해본 결과 1번 Motor만 돌아가고 2번은 돌아가지 않음
    - 로봇케이블을 바꿔도 증상 동일
    - Turtelbot3 burger(17번)의 DXL을 연결해도 증상 동일
    - OpenCR(17번)을 변경해도 증상 동일
  - 그 와중에 waffle에 쓰던 OpenCR 전원스위치(Toggle) 고장 -> 부품함에 있던 새 OpenCR로 변경(어쨋든 작동 안함)
  - Arduino IDE로 turtlebot3_setup_motor 열고 Serial monitor 켜서 Setup right motor 해봤는데 에러 발생
    ```
    [TxRxResult] There is no status packet!
    ```
  - R+ Manager 2.0 이용해보려고 했으나 OpenCM 보드가 필요하여 못함
  - Robotis에 문의 -> Dynamixel Wizard를 이용해보고, 안되면 A/S 맡기라고 함
  
---

## 2020.03.28.
- **Dynamixel Wizard 이용**
  - Minji_UBUNTU에 Dynamixel Wizard 설치
  - OpenCR에 usb_to_dxl 업로드
  - Scan 했을 때 아무 변화 없음
  - Recovery 실패
- 다음 주 평일 중에 문의전화 예정

---

## 2020.03.31.
- **Dynamixel Wizard를 이용한 점검**
  - ROBOTIS 본사 기술지원팀에 문의한 결과 통신문제일 수도 있다는 가능성을 들었음.
  - OpenCR에 usb_to_dxl을 업로드하여 Dynamixel Wizard를 시도해보았으나 아래 링크에서 U2D2가 아닌 OpenCR을 이용하면 불안정할 수 있다고 하여 U2D2로 시도
    - 참고: `OpenCR Board no longer recognizing dynamixels after firmware update`
    https://github.com/ROBOTIS-GIT/OpenCR/issues/203
    - 참고: `DYNAMIXEL Wizard 2.0 Firmware Recovery with U2D2`
    https://youtu.be/PgbIAK2Qg1Y
    - 학교노트북(5번)의 윈도우에 Dynamixel Wizard 2.0을 설치하고 Dynamixel과 연결 성공
  - 2번 모터의 ID가 ID1으로 되어있어 ID2로 변경하였으나 OpenCR SW test 결과 같은 증상 보임(1번 모터만 작동)
  - 2번 모터를 Firmware Recovery해 보았으나 작동 안함
  - Dynamixel Wizard를 이용한 자가진단 [도구]->[자가진단]
    - 2번 모터를 자가진단해 본 결과 나머지는 정상이었으나 '속도가 사양보다 낮습니다'라는 문구가 뜸
    - 1번 모터를 자가진단 해 본 결과 나머지는 정상이었으나 '속도가 사양보다 높습니다'라는 문구가 뜸
    - 자가진단을 하면서 팩토리리셋(Factory reset)이 되었기 때문에 복구도 해 보았으나(v44, v43 버전 둘 다 해봄) 두 모터 다 작동 안함
  - A/S 요청 필요하다고 판단

---

## 2020.04.16.
- **A/S 센터로 배송 보냄**
  - Tutlebot3 Waffle Pi의 Dynamixel 2개, OpenCR 1개

---

## 2020.04.18.
- **수리 완료하여 부품 다시 받음**
  - OpenCR 스위치: 전원을 양쪽에서 공급하면 일시적으로 작동하지 않을 수 있으나 현재는 문제 없음
  - Dynamixel: setting 문제로 현재는 문제 없다고 함

---

## 2020.05.15.
- **분해한 Turtlebot 다시 조립**
- **OpenCR Dynamixel 작동 test**
  - 또 안됨!!!!! PUSH SW1, SW2 둘다 해봤으나 2번 Dynamixel이 여전히 작동하지 않음
  - teleop 안됨
- **다음 계획**
  - 준형님이 관리하던 Waffle의 Dynamixel을 분해하여 test해도 되는지 여쭤볼 것
  - ROBOTIS에 전화해서 setting후 test 완료된건지 확인
  - U2D2로 다시 Dynamixel setting

---

## 2020.05.22.
- **다른 와플로 test**
  - 우리 dynamixel을 다른 OpenCR에 연결했을 때 ID2 작동 X
  - 다른 dynamixel을 우리 OpenCR에 연결했을 때 ID2 작동 X
- **U2D2로 다시 Dynamixel setting 확인**
- **ROBOTIS에 문의전화**
  - 우리가 시도했던 모든 것들을 시켜서 다시 해봤지만 작동하지 않아서 SMPS를 확인해보라고 하심
  - Dynamixel(XM430-W210-T)이 12V를 인가해야 정상 작동하는데, 우리가 19V짜리 SMPS를 사용하고 있었음
  - *결론: 우리는 한달 넘게 멍청한 짓을 했다. SMPS 잘 확인하자.*
  `12V`

---

## 2020.07.11.
- **와플 환경 다시 test**
  - jetson pinout 참고 사이트: https://www.jetsonhacks.com/nvidia-jetson-nano-j41-header-pinout/
   
   (화살표 있는 부분이 1)
   
  - Jetson TX2와 호환이 안되는 것 같음
  - lidar 값을 받아오질 못하고 텔레옵키 또한 작동 안함 (오로지 roscore 구동 및 그 외의 launch만 진행됨)
  - 라즈베리파이에 환경 구축해둠 (원래 세팅대로 우선 진행하고 젯슨에서는 영상처리 하여 싱크 맞춰서 라즈베리에 넘겨볼 계획)
  
- **할 일**
  - 회사 문의 게시판에 세팅 문의
  - 대회 지원금 외 교내 문의
  - conda - pytorch, cv .. etc download
  - box image - annotation

---

## 2020.07.18.
- **Conda 설치**
- 상자 사진 수집
#### 할일
- 적재 알고리즘 개발
- 이미지 Annotation
  
---

## 2020.07.30.
- ROBOTIS 문의 결과 SBC setting은 도움줄 수 없다고 답변받음
  - Jetson과 RaspberryPi를 따로 구동해야 할 듯함
- **SLAM 시도**
  - 라즈베리파이로 SLAM 실행
  - 로봇팔은 인식하지 않는 것으로 보임
    - teleop로 이동시켜봐도 문제 없어 보임(라이다와의 거리가 너무 가까워서? 이유는 확실하지 않음)
- **GPU**
  - Google의 Cloud GPU를 사용하려고 했으나 페이지에서 다음 절차로 안넘어가짐

---

## 2020.07.31.
- **Box Detecting**
  - 다음 링크를 참고할 예정
  fontenay-ronan.fr/computer-vision-a-box-on-a-industrial-conveyor/
  - 수정 중

#### 내일 할 일
- Box Detecting 알고리즘 개발
- Jetson - Raspberry 간 Sync
- Google Cloud GPU

---

## 2020.08.01.
- **진행정리**
  - GCP는 대회 지급 연구비에서 해결하기 어려운 가격 / 사용하려 해도 사이트에서 가입이 안됨 -> google colab pro 사용 예정 (2달)
  - 로봇팔에 맞춰서 박스 크기 다양하게 프린트 할 예정
  - 컨베이어벨트는 구매 예정
