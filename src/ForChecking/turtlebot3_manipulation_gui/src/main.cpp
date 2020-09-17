/*******************************************************************************
* Copyright 2020 ROBOTIS CO., LTD.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed uto in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*******************************************************************************/

/* Authors: Ryan Shim */

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
    char n[1];
    w.show();
    w.on_btn_timer_start_clicked();
    app.connect(&app, SIGNAL(lastWindowClosed()), &app, SLOT(quit()));
    int a[4] = {};
    float b[4] = {0.550, 0.638, 0.068, -0.005};
    std::cout << "주소지는 a/b/c/: ";
    std::cin >> n;

    if(strcmp(n,"a")==0){
        // 행동 진행 
	w.on_btn_init_pose_clicked();
        //std::cin >> n;
        //sleep(2000);
        //w.on_btn_home_pose_clicked();
	std::cout << "a\n";
    }
    else if(strcmp(n,"b")==0){
	w.on_btn_send_joint_angle_clicked(b[0], b[1], b[2], b[3]);
        std::cin >> n;
	w.on_btn_init_pose_clicked();
	//행동
	std::cout << "b\n";
    }
    else if(strcmp(n,"c")==0){
	//행동
        std::cout << "c\n";
    }
    /*********************
    ** Qt
    **********************/
    //QApplication app(argc, argv);
    //turtlebot3_manipulation_gui::MainWindow w(argc,argv);
    //w.show();
    //app.connect(&app, SIGNAL(lastWindowClosed()), &app, SLOT(quit()));
    int result = app.exec();
    return result;
}
