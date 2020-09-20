/*****************************************************************************
** Includes
*****************************************************************************/
#include <stdio.h>
#include <QtGui>
#include <QApplication>
#include "../include/turtlebot3_manipulation_gui/main_window.hpp"

/*****************************************************************************
** Main
*****************************************************************************/

int main(int argc, char **argv) {
    QApplication app(argc, argv);
    turtlebot3_manipulation_gui::MainWindow w(argc,argv);

    char n[1]; // data 전달받을 주소지 

    // application 보여주고 거기서 실행 log 보여주기 
    w.show();

    w.on_btn_timer_start_clicked(); // 처음에 Qtimer 시작해야하기 때문에 클릭 
    app.connect(&app, SIGNAL(lastWindowClosed()), &app, SLOT(quit()));

    //주소지 따른 행동 
    float a[4] = {0.550, 0.638, 0.068, -0.005}; // 주소지 a가 행동할 방향 
    float b[4] = {0.550, 0.638, 0.068, -0.005}; // 주소지 b가 행동할 방향 
    float c[4] = {0.550, 0.638, 0.068, -0.005}; // 주소지 c가 행동할 방향 
    // 치기 
    float a_1[4] = {0.550, 0.638, 0.068, -0.005}; // a 박스 전달 
    float b_1[4] = {0.550, 0.638, 0.068, -0.005}; // b 박스 전달 
    float c_1[4] = {0.550, 0.638, 0.068, -0.005}; // c 박스 전달 

    std::cout << "주소지는 a/b/c/: ";
    std::cin >> n;

    while(1){
		if(strcmp(n,"a")==0){
		    w.on_btn_send_joint_angle_clicked(a[0], a[1], a[2], a[3]);
		    std::cin >> n; // 버퍼가 필요 - 다른 아이디어 있으면 대체 
            w.on_btn_send_joint_angle_clicked(a_1[0], a_1[1], a_1[2], a_1[3]);
            std::cin >> n; // 버퍼가 필요 - 다른 아이디어 있으면 대체 
		    w.on_btn_init_pose_clicked();
		    std::cout << "a\n";
		}

		else if(strcmp(n,"b")==0){
		    w.on_btn_send_joint_angle_clicked(b[0], b[1], b[2], b[3]);
		    std::cin >> n;
            w.on_btn_send_joint_angle_clicked(b_1[0], b_1[1], b_1[2], b_1[3]);
            std::cin >> n;
		    w.on_btn_init_pose_clicked();
		    std::cout << "b\n";
		}

		else if(strcmp(n,"c")==0){
            w.on_btn_send_joint_angle_clicked(c[0], c[1], c[2], c[3]);
            std::cin >> n;
            w.on_btn_send_joint_angle_clicked(c_1[0], c_1[1], c_1[2], c_1[3]);
            std::cin >> n;
            w.on_btn_init_pose_clicked();
		    std::cout << "c\n";
		}

        else{ // data sending 종료 시  
            break;
        }
        int result = app.exec();
        return result;
    }
}
