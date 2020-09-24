#include <stdio.h>
#include <stdlib.h>
#include <QtGui>
#include <QApplication>
#include "../include/turtlebot3_manipulation_gui/main_window.hpp"
#include "ros/ros.h"
#include "std_msgs/String.h"
#include <iostream>
#include <queue>
#include <string.h>
//#include <opencv2/opencv.hpp>

char c[4];

void chatterCallback(const std_msgs::String::ConstPtr& msg)
{
  ROS_INFO("I heard: [%s]", msg->data.c_str());
  memcpy(c, msg->data.c_str(), sizeof(msg->data.c_str()));
  std::cout << c[0] ;
}



int main(int argc, char **argv) {
    QApplication app(argc, argv);
    turtlebot3_manipulation_gui::MainWindow w(argc,argv);

/*
    // cv
    Mat img_color, img_blurred, img_gray;
    Rect rect;
    VideoCapture cap(1);
*/
    //주소지 따른 행동 
    float a[4] = {0.950,0.200, 0.400, 0.500}; // 주소지 a가 행동할 방향 
    float b[4] = {0.700,0.250, 0.000, 0.800};; // 주소지 b가 행동할 방향 
    float c[4] = {0.950, 0.650, -0.300, 0.300}; // 주소지 c가 행동할 방향 
    // 치기 
    float a_1[4] = {0.950,0.400, 0.400, -0.350}; // a 박스 전달 
    float b_1[4] = {0.65, 0.550, -0.250, 0.400}; // b 박스 전달 
    float c_1[4] = {0.600, 0.650, -0.300, 0.300}; // c 박스 전달 
    
    // 통신 init
    ros::init(argc, argv, "listener");
    ros::NodeHandle n;

    using namespace std;
    //using namespace cv;
    queue<char> q; // data 전달받을 주소지 
    char d[4]; // data 전달받을 주소지 
    char A = 'A';
    char B = 'B';
    char C = 'C';

    // application 보여주고 거기서 실행 log 보여주기 
    w.show();

    w.on_btn_timer_start_clicked(); // 처음에 Qtimer 시작해야하기 때문에 클릭 
    std::cout << " timer clicked ";
    //w.on_btn_gripper_close_clicked(); // start with gripper closed
    std::cout << " gripper clossed ";
    app.connect(&app, SIGNAL(lastWindowClosed()), &app, SLOT(quit()));

    while(1){
                /*
		cap.read(img_color);
		if (img_color.empty()) {
			break;
		}
		GaussianBlur(img_color, img_blurred, Size(5, 5), 0, 0, 4);
		cvtColor(img_blurred, img_gray, COLOR_BGR2GRAY);
		threshold(img_gray, img_gray, 100, 255, THRESH_BINARY);
		vector<vector<Point> > contours; // Vector for storing contour
		vector<Vec4i> hierarchy;

		double area;
		double max_area = 0;
		int max_index = -1;
		findContours(img_gray, contours, hierarchy, CV_RETR_CCOMP, CV_CHAIN_APPROX_SIMPLE); // Find the contours in the image

		for (int i = 0; i < contours.size(); i++) {
			area = contourArea(contours[i], false);
			if (area > max_area) {
				max_area = area;
				max_index = i;
				rect = boundingRect(contours[i]);
			}
		}
		drawContours(img_color, contours, max_index, Scalar(0, 255, 0), 2, 8, hierarchy);
		rectangle(img_color, rect, Scalar(0, 0, 255), 2, 8, 0);
                */

                // communication start 
		//ros::Subscriber sub = n.subscribe("chatter", 1000, chatterCallback);
                //if ((d[0] !=  c[0])||(d[1] !=  c[1])||(d[2] !=  c[2])){
		//    d[0] = c[0];
		//    d[1] = c[1];
		//    d[2] = c[2];
		//    q.push(c[0]);
		//}
                
		std::cout << "input:";
                std::cin >> d;
                q.push(d[0]);

                
		if(q.front()==A){
                    sleep(5);
                    std::cout << "A start\n";
		    w.on_btn_send_joint_angle_clicked(a[0], a[1], a[2], a[3]);
		    std::cin >> d[0]; // 버퍼가 필요 - 다른 아이디어 있으면 대체 
                    std::cout << " buffer 1\n ";
           	    w.on_btn_send_joint_angle_clicked(a_1[0], a_1[1], a_1[2], a_1[3]);
                    std::cin >> d[0]; // 버퍼가 필요 - 다른 아이디어 있으면 대체 
                    std::cout << " buffer 2\n ";
		    w.on_btn_init_pose_clicked();
		    std::cout << "a\n";
                    std::cin >> d[0];
                    q.pop();
		}

		else if(q.front()==B){
		    std::cout << "B start\n";
		    w.on_btn_send_joint_angle_clicked(b[0], b[1], b[2], b[3]);
		    std::cin >> d[0]; // 버퍼가 필요 - 다른 아이디어 있으면 대체 
                    std::cout << " buffer 1\n ";
                    w.on_btn_send_joint_angle_clicked(b_1[0], b_1[1], b_1[2], b_1[3]);
		    std::cin >> d[0]; // 버퍼가 필요 - 다른 아이디어 있으면 대체 
                    std::cout << " buffer 2\n ";
		    w.on_btn_init_pose_clicked();
		    std::cout << "b\n";
                    std::cin >> d[0];
                    q.pop();
                    std::cout << " pop\n";
		}

		else if(q.front()==C){
                    std::cout << "V start\n";
            	    w.on_btn_send_joint_angle_clicked(c[0], c[1], c[2], c[3]);
		    std::cin >> d[0]; // 버퍼가 필요 - 다른 아이디어 있으면 대체 
                    std::cout << " buffer 1\n ";
                    w.on_btn_send_joint_angle_clicked(c_1[0], c_1[1], c_1[2], c_1[3]);
		    std::cin >> d[0]; // 버퍼가 필요 - 다른 아이디어 있으면 대체 
                    std::cout << " buffer 2\n ";
                    w.on_btn_init_pose_clicked();
		    std::cout << "c\n";
                    std::cin >> d[0];
                    q.pop();
                    std::cout << " pop\n";
		}

                else{ // data sending 종료 시  
                    continue;
                }
                //int result = app.exec();
                ros::spin();
                //return result;
    }
    int result = app.exec();
    return result;
}

