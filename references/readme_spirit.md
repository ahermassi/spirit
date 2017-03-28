# SPIRIT (Subimposed Past Image Records Implemented for Teleoperation)

This is my Masters research project, and can be found [on Github](https://github.com/masasin/spirit).

## Table of Contents
* [Checklist](#checklist)
* [Troubleshooting](#troubleshooting)

## Checklist

The following checklist is specifically designed for use with the Mocap Optitrack system available in the Kyoto University Mechatronics Laboratory, and the computer SPIRIT was originally run on.
It can be adapted as necessary.
For instance, if odometry is used to find the drone's pose, the motion capture part is not needed.

In order to run the system:

* [ ] Make sure the targets are in the correct position.
* [ ] Set up the hardware.
  * [ ] Connect the mocap cameras to the mocap router via ethernet.
  * [ ] Connect the mocap PC to the mocap router via ethernet.
  * [ ] Connect the mocap PC to the operating station via ethernet.
  * [ ] Connect the PS3 controller to the operating station via USB.
* [ ] Set up the mocap PC. (Windows environment)
  * [ ] Set the motion capture PC's IP address (currently ローカルエリア接続４) to 192.168.0.1.
  * [ ] Start Motive.
  * [ ] Open a recent project file, or:
    * [ ] Perform wanding and ground-plane setup.
    * [ ] Put the drone markers in the field of view of the camera.
    * [ ] Create a rigid body from the markers on the drone.
  * [ ] Open the Rigid Bodies pane.
    * [ ] Set the name to something convenient, such as "drone". (Optional)
    * [ ] Under Advanced, set User Data to "1".
    * [ ] Under Orientation, click "Reset to Current Orientation".
  * [ ] Open the Streaming pane. Ensure all settings are as follows:
    * Broadcast Frame Data: On
    * Local Interface: 192.168.0.1
    * Stream Markers: True
    * Stream Rigid Bodies: True
    * Type: Multicast
    * Command Port: 1510
    * Data Port: 1511
    * Multicast Interface: 239.255.42.99
* [ ] Set up the operating station. (Linux environment)
  * [ ] Create a Wired Ethernet connection with the following settings:
    * Automatically connect to this network when it is available: True
    * IPv4 Method: Manual
    * Address: 192.168.0.2
    * Netmask: 255.255.255.0
    * Gateway: 192.168.0.1
  * [ ] Activate the controller by pressing the central PS button.
  * [ ] Ensure that the volume is high enough, and that any earphones are worn.
  * [ ] Run the docker container.
* [ ] Set up the drone.
    * [ ] Charge the battery if it is not charged. WARNING: Do not leave on charge for too long when full.
    * [ ] Connect the battery. 
    * [ ] Put the indoor hull on the drone.
    * [ ] Ensure correct startup.
    * [ ] Connect the operating station to the drone WiFi. The password is the string of digits on the SSID.
* [ ] Set up the ROS environment. (Docker container on operating station)
  * [ ] Run the following commands to enable the necessary packages inside the work environment:
    * [ ] `workon spirit`
    * [ ] Enable global site-packages with `toggleglobalsitepackages` if necessary. Rerun the command if you see "Disabled global site-packages".
  * [ ] Set appropriate values in the `config/launch_params.yaml` file. (Optional)
  * [ ] Regenerate the launch files: `config/regenerate_launch_files.py`.
* [ ] Launch the system: `roslaunch spirit spirit.launch`.
* [ ] <a name="checklist-collect-data" />If you want to collect data, start the collection according to the [data collection readme](readme_data.md).
* [ ] Ensure that:
  * [ ] A live camera feed is displayed. (depends on configuration)
  * [ ] The past image feed is displayed. (depends on configuration)
  * [ ] If the past image feed is displayed, "No data yet" is not displayed.
  * [ ] The battery is high. (The drone will not take off with a low battery.)
* [ ] Test the controller connection:
  * [ ] Tap the Emergency button (default is R1). The drone lights should turn red momentarily, and the status should change to Emergency.
* [ ] Launch the drone and fly. Tap the Takeoff button to take off, and the Land button to land. Use the Emergency button in emergencies. Tap the Arrived button to indicate that you believe that you are at the target.
* [ ] After landing:
  * [ ] Stop any recording of data.
  * [ ] Retrieve the drone.
  * [ ] Disconnect and charge the battery.

## Troubleshooting

  * Check the launch configuration file to see if you didn't turn an option off by mistake.
  * Make sure that the configuration files have been generated.
  * If 192.168.0.1 does not appear in Motive, it means it was started before being connected to the operating station for the first time. Restart Motive and repeat the rest of that section.
  * If the live camera feed is not displayed, and the past image feed is black, check that the operating station is connected to the drone's WiFi.
  * If the drone does not take off, check that the battery is charged.
  * If the past image feed is black, check that:
    * the mocap system is connected
    * the mocap system is sending data
    * the mocap system identifies the drone as a rigid body
    * the rigid body's User Data is set to "1"
    * the drone is actually being tracked
  * If no sound plays when the drone tracking is lost:
    * Ensure that the volume is not muted or low.
    * Ensure that earphones are unplugged, or worn.
    * Otherwise, stop sounds from other sources and restart the computer. The issue can be reproduced by running Google Play Music.
  * If the controller is not detected:
    * Ensure that the controller is connected.
    * Exit the docker container and reconnect.
