# SPIRIT (Subimposed Past Image Records Implemented for Teleoperation)

This is my Masters research project.
I built a novel interface for the teleoperation of quadrotors, which allows the operator to have a third-person perspective of flight operations using only pose information and a monocular camera.

This implementation relies on a motion capture (mocap) setup to obtain the position and orientation, but it should work with any other methods, including but not limited to: RT-SLAM, LSD-SLAM, visual odometry, and distance sensors.
Changing the localization method would enable the system to be used outdoors.


## Table of Contents

* [Structure](#structure)
* [Setup and running](#setup-and-running)
  * [Python](#python)
  * [Docker](#docker)
  * [Troubleshooting](#troubleshooting)
* [Components](#components)
  * [SPIRIT](#spirit)
  * [Data collection](#data-collection)
  * [Data analysis](#data-analysis)
  * [Thesis](#thesis)
* [Licensing](#licensing)


## Structure
This repository utilizes a slightly modified version of Driven Data's [data science cookiecutter template](https://drivendata.github.io/cookiecutter-data-science/).
As a structure used by various projects, it should allow for easier reusability and sharing among groups.
It also helps with the reproducability of the data pipleine, and the collection of all pieces in one place.


## Setup and running

### Python
Assumptions:
* Linux system

The data analysis pipeline requires Python 3.6 or above.
If you don't have it on your computer, you can obtain it using `pyenv`.
It is usually best to work inside a `virtualenv` or other sandbox.
Follow the instructions for whichever system you prefer.

Once you have a virtualenv for the project, you can install the necessary packages by running the following command while in the base directory:

    pip install -r requirements.txt

### Docker
Assumptions:
* Linux system (to share sound)
* NVIDIA video card

Prerequisites:
* Docker
* [`nvidia-docker`](https://github.com/NVIDIA/nvidia-docker) (to use OpenGL)

Build by running the `build` file in the base directory, and run it using by running the `run` file.

Note that in Kyoto University, the proxy does not allow building, and until docker allows network sharing, building must happen outside the university.

Once a container has been built, you can use `docker ps` to find the currently running container, and save any new configurations using `docker commit`.
Make sure to update the `run` file to reflect the container you want to run, and (ideally) add the changes to `Dockerfile`.

Run the `join` file in order to join the currently running container.
This can be useful, for instance, for running some of the data collection or analysis programs.

If permission errors occur on files created inside the docker container (such as when commiting code), you can run the `fix_permissions` script from outside the container in order to make you the owner again.

### Troubleshooting

* If you cannot `run` due to `nvidia-docker` complaining about an unsupported Docker version, either update `nvidia-docker` or downgrade Docker.


## Components
This repository contains the four main components of the project, each with its own readme.

The Jupyter notebooks in the [notebooks](notebooks) directory are primarily for exploration, and are only included here for completeness.
They do not get updated, and may lag behind the latest changes in structure or details.

### SPIRIT
[[README]](references/readme_spirit.md)
The crux of the project.
It lives in the [src/ros/spriit](src/ros/spirit) directory, and contains the entire ROS portion. 

In order to run it, follow the [checklist](references/readme_spirit.md#checklist) in the SPIRIT readme.
Note that this does not attempt to gather any data, but instead enables the user to interface with the motion capture system and fly the drone.

### Data collection 
[[README]](references/readme_data.md)
The code for collecting the data is in the [`src/data`](src/data) directory.
It consists of a command line tool to record the relevant data into bagfiles, another to convert the bagfiles into CSV for easier offline analysis, and a web interface to collect user responses to a survey and NASA-TLX results.

The experimentation phase also included video recording using OBS.
Note that, at the time of writing, there was no way to programmatically start and stop a recording session.
As such, this operation must still be done manually.

See the [readme](references/readme_data.md) for more details.

### Data analysis
[[README]](references/readme_analysis.md)
Some written things.

### Thesis
[[README]](references/readme_thesis.md)
Some written things.


## Licensing
* The SPIRIT software, as well as the code used for data collection and analysis, are licensed under the MIT License.
* The thesis is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License.

Permissions beyond the scope of this license are administered by Jean Nassar. Please contact jeannassar5+licensing@gmail.com for more information.

Copyright © 2017 by Jean Nassar.
