/*****************************************************************************
** Includes
*****************************************************************************/

#include <QtGui>
#include <QApplication>
#include "../include/turtlebot3_manipulation_gui/main_window.hpp"

/*****************************************************************************
** Main
*****************************************************************************/
/* 박스 치기 위한 코드 */
// 1번 데이터 주소 받기 (우선은 사용자에게 입력 받는 것으로 주소지 3개)
// 2번 입력받은 데이터를 3가지 if문으로 처리하기
// 조건을 받으면 클래스 가져와서 각도 조절 해서 치고 원래 포즈로 돌아가도록

int main(int argc, char **argv) {

    /*********************
    ** Qt
    **********************/
    QApplication app(argc, argv);
    turtlebot3_manipulation_gui::MainWindow w(argc,argv);
    w.show(); # 보여주고 프린트 되는 것 확인하기
    app.connect(&app, SIGNAL(lastWindowClosed()), &app, SLOT(quit()));
    int result = app.exec();

	return result;
}
