#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2015  Jean Nassar
# Released under BSD version 4
"""
Display raw feed and low framerate feed.

"""
import cv2

import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError


class Display(object):
    def __init__(self):
        """
        Remap image_raw to your target node from the launch file.

        """
        self.subscriber = rospy.Subscriber("image_raw",
                                           Image, self.callback, queue_size=1)
        self.bridge = CvBridge()
        self.contents = rospy.get_param(rospy.search_param("contents"),
                                        "camera")

    def callback(self, ros_data):
        """
        Callback function of subscribed topic.

        Here, the image is displayed.

        """
        # Convert to CV2.
        try:
            image = self.bridge.imgmsg_to_cv2(ros_data, "bgr8")
        except CvBridgeError as e:
            rospy.logerr(e)

        cv2.imshow(self.contents.capitalize(), image)
        cv2.waitKey(1)


def shutdown_hook():
    """Runs on shutdown."""
    cv2.destroyAllWindows()


def main():
    """Initialize and cleanup ROS node."""
    rospy.init_node("image_feature", anonymous=True)
    rospy.on_shutdown(shutdown_hook)
    display = Display()
    rospy.loginfo("Displaying {}.".format(display.contents))
    rospy.spin()


if __name__ == "__main__":
    main()
