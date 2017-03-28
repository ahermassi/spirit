# SPIRIT Data Collection

The source code for data collection is in the [`src/data`](../src/data) directory.

* [`record_bag.py`](../src/data/record_bag.py) is a command line tool which records the relevant data into a ROS Bag file.
* [`bag_to_csv.py`](../src/data/bag_to_csv.py) is a script which converts new bagfiles into CSV 
* [`survey.py`](../src/data/survey.py) is a web interface to collect user information, and their opinions after each run of the experiment.
Since [`survey.py`](../src/data/survey.py) requires a `__main__` module to run, a convenience script, [`run_survey`](../src/data/run_survey), which can be run from anywhere.

[`config.py`](../src/data/config.py) contains the configuration options for all the data collection tools.
By default, bagfiles and survey data are stored in [`data/raw`](../data/raw), while the CSV data is stored in [`data/interim`](../data/interim).

[`record_bag.py`](../src/data/record_bag.py) and [`bag_to_csv.py](../src/data/bag_to_csv.py)` can only be used from inside the Docker container.

## Checklist
* [ ] If you will be recording the screen and camera input, make sure OBS is set up properly prior to running the experiment.
  * Set a hotkey which would allow you to start and stop recording, so that you don't need to switch to the application.
  * A good location to store the videos is [`data/raw/recordings`](../data/raw/recordings).
* [ ] Have the users sign the consent and waiver forms.
* [ ] Run the survey.
* [ ] Select the user.
  * If the user has done previous experiments, select their name from the list below the table.
  * Otherwise, click "Add user", input their information, and press "Ok".
* [ ] Move to the corresponding tab and click on the "Run experiment" button.
For my experiment, the users with an even ID started with the onboard view, while those with an odd ID started with SPIRIT.
It is also possible to choose a random experiment, or an experiment which allows the user to see both interfaces at the same time.
* [ ] Now, you want to run the Docker container and connect to the drone according to the [checklist](readme_spirit.md#checklist-collect-data) in the corresponding [readme](readme_spirit.md).
In a separate terminal, `join` the running container.
