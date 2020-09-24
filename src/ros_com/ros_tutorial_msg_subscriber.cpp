#include "ros/ros.h"                                            // import rospy
#include "oroca_ros_tutorials/msgTutorial.h"
#include <std_msgs/String.h>                                    // import std_msgs.msg import String

// def callback(data)
void msgCallback(const oroca_ros_tutorials::msgTutorial::ConstPtr& msg)
{
	ROS_INFO("recieve msg: %d", msg->data
        // rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
}

int main(int argc, char **argv)
{
	ros::init(argc, argv, "ros_tutorial_msg_subscriber");
        //rospy.init_node("listener",anoymous=True)

	ros::NodeHandle nh;

	ros::Subscriber ros_tutorial_sub = nh.subscribe("ros_tutorial_msg", 10, msgCallback);
        //rospy.Subscriber(:publisher", String callback)

	ros::spin();
        //rospy.spin()
	
	return 0;
}
