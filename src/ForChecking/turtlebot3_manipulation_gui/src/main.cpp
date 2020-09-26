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
#include <opencv2/opencv.hpp>

using namespace std;
using namespace cv;

char curr[4] = "XXX";

void chatterCallback(const std_msgs::String::ConstPtr &msg)
{
	//ROS_INFO("I heard: [%s]", msg->data.c_str());
	memcpy(curr, msg->data.c_str(), sizeof(msg->data.c_str()));
	//printf("%c\n", curr[0]);
}

/* ------------------------- main ----------------------------*/
int main(int argc, char **argv)
{
	QApplication app(argc, argv);
	turtlebot3_manipulation_gui::MainWindow w(argc, argv);

	// cv
	Mat img_color, img_blurred, img_gray;
	Rect rect;
	Rect red;
	VideoCapture cap(1);
	//cap.set(CAP_PROP_EXPOSURE, -8);
	cap.set(CAP_PROP_FPS, 50);

	int flag = 0;
	//주소지 따른 행동
	float a[4] = {0.950, 0.200, 0.400, 0.500}; // 주소지 a가 행동할 방향
	float b[4] = {0.700, 0.250, 0.000, 0.800};
	;											// 주소지 b가 행동할 방향
	float c[4] = {0.950, 0.650, -0.300, 0.300}; // 주소지 c가 행동할 방향
	// 치기
	float a_1[4] = {0.950, 0.400, 0.400, -0.350}; // a 박스 전달
	float b_1[4] = {0.65, 0.550, -0.250, 0.400};  // b 박스 전달
	float c_1[4] = {0.600, 0.650, -0.300, 0.300}; // c 박스 전달

	/*    // 통신 init
    ros::init(argc, argv, "listener");
    ros::NodeHandle n;
*/
	queue<char> q; // data 전달받을 주소지
	char prev[4] = "XXX";
	char A = 'A';
	char B = 'B';
	char C = 'C';

	// application 보여주고 거기서 실행 log 보여주기
	w.show();
	w.on_btn_timer_start_clicked(); // 처음에 Qtimer 시작해야하기 때문에 클릭
	std::cout << " timer clicked ";
	w.on_btn_init_pose_clicked();
	sleep(1);
	w.on_btn_gripper_close_clicked(); // start with gripper closed
	std::cout << " gripper clossed ";
	app.connect(&app, SIGNAL(lastWindowClosed()), &app, SLOT(quit()));

	while (1)
	{
		// VIDEO

		cap >> img_color;
		if (img_color.empty())
		{
			break;
		}
		Rect roi = Rect(250, 100, 300, 300);
		img_color = img_color(roi);
		GaussianBlur(img_color, img_blurred, Size(5, 5), 0, 0, 4);
		cvtColor(img_blurred, img_gray, COLOR_BGR2GRAY);
		threshold(img_gray, img_gray, 100, 255, THRESH_BINARY);
		vector<vector<Point>> contours; // Vector for storing contour
		vector<Vec4i> hierarchy;

		double area;
		double max_area = 0;
		int max_index = -1;
		findContours(img_gray, contours, hierarchy, CV_RETR_CCOMP, CV_CHAIN_APPROX_SIMPLE); // Find the contours in the image
		int centerX;
		int centerY;
		for (int i = 0; i < contours.size(); i++)
		{
			area = contourArea(contours[i], false);
			if (area > 5000 && area < 30000 && area > max_area)
			{
				max_area = area;
				max_index = i;
				rect = boundingRect(contours[i]);
				centerX = rect.x + rect.width / 2;
				centerY = rect.y + rect.height / 2;
				if (centerX > 100 && centerX < 200 && centerY > 150 && centerY < 250)
				{
					red = rect;
					printf("area: %lf\n", max_area);
					printf("center: (%d, %d)\n", centerX, centerY);
					printf("%d\t%d\t%d\t%d\n", rect.x, rect.x + rect.width, rect.y, rect.y + rect.height);
					flag = 1;
				}
			}
		}
		drawContours(img_color, contours, max_index, Scalar(0, 255, 0), 2, 8, hierarchy);
		rectangle(img_color, red, Scalar(0, 0, 255), 2, 8, 0);

		imshow("Manipulator", img_color);
		if (waitKey(1) & 0xFF == 27)
			break;

		/*
                // COMMUNICATION 
		ros::Subscriber sub = n.subscribe("chatter", 10, chatterCallback);
                ros::Rate loop_rate(1);


                if (strcmp(prev, curr)!=0){
		    memcpy(prev, curr, sizeof(prev));
		    q.push(curr[0]);
		    //printf("success to push\n");
		}
*/
		printf("3\n");
		std::cout << "input:";
		std::cin >> prev;
		q.push(prev[0]);

		//loop_rate.sleep();
		//ros::spinOnce();
		//printf("after spinOnce()\n");

		ros::Rate callback_rate(1);
		ros::AsyncSpinner spinner(0);
		spinner.start();
		if (flag == 1)
		{
			if (q.front() == A)
			{
				std::cout << "A start\n";
				w.on_btn_send_joint_angle_clicked(a[0], a[1], a[2], a[3]);
				std::cout << " buffer 1\n ";

				usleep(1300000);
				w.on_btn_send_joint_angle_clicked(a_1[0], a_1[1], a_1[2], a_1[3]);
				std::cout << "buffer 2\n ";

				usleep(1400000);
				w.on_btn_init_pose_clicked();
				std::cout << "a\n";

				q.pop();
				std::cout << "pop\n";
			}

			else if (q.front() == B)
			{
				std::cout << "B start\n";
				w.on_btn_send_joint_angle_clicked(b[0], b[1], b[2], b[3]);
				std::cout << " buffer 1\n ";

				usleep(1300000);
				w.on_btn_send_joint_angle_clicked(b_1[0], b_1[1], b_1[2], b_1[3]);
				std::cout << " buffer 2\n ";

				usleep(1400000);
				w.on_btn_init_pose_clicked();
				std::cout << "b\n";

				q.pop();
				std::cout << " pop\n";
			}

			else if (q.front() == C)
			{
				std::cout << "C start\n";
				w.on_btn_send_joint_angle_clicked(c[0], c[1], c[2], c[3]);
				std::cout << " buffer 1\n ";

				usleep(1300000);
				w.on_btn_send_joint_angle_clicked(c_1[0], c_1[1], c_1[2], c_1[3]);
				std::cout << " buffer 2\n ";

				usleep(1400000);
				w.on_btn_init_pose_clicked();
				std::cout << "c\n";

				q.pop();
				std::cout << " pop\n";
			}

			else
			{ // data sending 종료 시
				printf("else\n");
				continue;
			}
			flag = 0;
			printf("1\n");
			printf("2\n");
		}
	}
	int result = app.exec();
	ros::waitForShutdown();
	return result;
}
