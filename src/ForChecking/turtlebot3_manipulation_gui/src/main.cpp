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
    std::cout << "주소지는 a/b/c/: ";
    std::cin >> n;
    w.show();
    app.connect(&app, SIGNAL(lastWindowClosed()), &app, SLOT(quit()));
    int result = app.exec();

    if(strcmp(n,"a")==0){
        // 행동 진행 
	std::cout << "a\n";
    }
    else if(strcmp(n,"b")==0){
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
    //int result = app.exec();
    return result;
}
