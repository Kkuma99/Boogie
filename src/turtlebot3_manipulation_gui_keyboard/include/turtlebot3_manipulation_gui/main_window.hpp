#ifndef TURTLEBOT3_MANIPULATION_GUI_MAIN_WINDOW_H
#define TURTLEBOT3_MANIPULATION_GUI_MAIN_WINDOW_H

/*****************************************************************************
** Includes
*****************************************************************************/

#include <QMainWindow>
#include "ui_main_window.h"
#include "qnode.hpp"
#include <QTimer>
#include <eigen3/Eigen/Eigen>

/*****************************************************************************
** Namespace
*****************************************************************************/

namespace turtlebot3_manipulation_gui {

/*****************************************************************************
** Interface [MainWindow]
*****************************************************************************/
class MainWindow : public QMainWindow {
Q_OBJECT

public:
	MainWindow(int argc, char** argv, QWidget *parent = 0);
	~MainWindow();
  void writeLog(QString str);

public Q_SLOTS:
  void timerCallback();
  void on_btn_timer_start_clicked(void);
  void on_btn_init_pose_clicked(void);
  void on_btn_home_pose_clicked(void);
  void on_btn_gripper_open_clicked(void);
  void on_btn_gripper_close_clicked(void);
  void on_btn_read_joint_angle_clicked(void);
  void on_btn_send_joint_angle_clicked(float& a, float& b, float& c, float& d);
  void on_btn_read_kinematic_pose_clicked(void);
  void on_btn_send_kinematic_pose_clicked(void);
  void on_btn_set_gripper_clicked(void);

  void tabSelected();

private:
	Ui::MainWindowDesign ui;
	QNode qnode;
  QTimer *timer;
};

}  // namespace turtlebot3_manipulation_gui

#endif // TURTLEBOT3_MANIPULATION_GUI_MAIN_WINDOW_H

