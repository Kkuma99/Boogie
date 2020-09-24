#include <stdio.h>
#include <QtGui>
#include <QApplication>
#include "../include/turtlebot3_manipulation_gui/main_window.hpp"
#include "ros/ros.h"
#include "std_msgs/String.h"
#include <iostream>
#include <queue>
#include <string.h>

char c[4];

void chatterCallback(const std_msgs::String::ConstPtr& msg)
{
  ROS_INFO("I heard: [%s]", msg->data.c_str());
  memcpy(c, msg->data.c_str(), sizeof(msg->data.c_str()));
}



int main(int argc, char **argv) {
    QApplication app(argc, argv);
    turtlebot3_manipulation_gui::MainWindow w(argc,argv);

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
    queue<string> q; // data 전달받을 주소지 
    //char c[1];
    char d[4]; // data 전달받을 주소지 
    string A = "A";
    string B = "B";
    string C = "C";

    // application 보여주고 거기서 실행 log 보여주기 
    w.show();

    w.on_btn_timer_start_clicked(); // 처음에 Qtimer 시작해야하기 때문에 클릭 
    w.on_btn_gripper_open_clicked(); // start with gripper closed
    app.connect(&app, SIGNAL(lastWindowClosed()), &app, SLOT(quit()));



    while(1){
                // communication start 
		ros::Subscriber sub = n.subscribe("chatter", 1000, chatterCallback);
                if ((d[0] !=  c[0])||(d[1] !=  c[1])||(d[2] !=  c[2])){
		    d[0] = c[0];
		    d[1] = c[1];
		    d[2] = c[2];
		    q.push(c[0]);
		}
                

		if(q.front()==A){
		    w.on_btn_send_joint_angle_clicked(a[0], a[1], a[2], a[3]);
		    //std::cin >> c; // 버퍼가 필요 - 다른 아이디어 있으면 대체 
           	    w.on_btn_send_joint_angle_clicked(a_1[0], a_1[1], a_1[2], a_1[3]);
                    //std::cin >> c; // 버퍼가 필요 - 다른 아이디어 있으면 대체 
		    w.on_btn_init_pose_clicked();
		    std::cout << "a\n";
                    q.pop();
		}

		else if(q.front()==B){
		    w.on_btn_send_joint_angle_clicked(b[0], b[1], b[2], b[3]);
		    //std::cin >> c;
                    w.on_btn_send_joint_angle_clicked(b_1[0], b_1[1], b_1[2], b_1[3]);
                    //std::cin >> c;
		    w.on_btn_init_pose_clicked();
		    std::cout << "b\n";
                    q.pop();
		}

		else if(q.front()==C){
            	    w.on_btn_send_joint_angle_clicked(c[0], c[1], c[2], c[3]);
                    //std::cin >> c;
                    w.on_btn_send_joint_angle_clicked(c_1[0], c_1[1], c_1[2], c_1[3]);
                    //std::cin >> c;
                    w.on_btn_init_pose_clicked();
		    std::cout << "c\n";
                    q.pop();
		}

                else{ // data sending 종료 시  
                    continue;
                }
                int result = app.exec();
                ros::spin();
                return result;
    }
}
