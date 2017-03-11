#!/usr/bin/env python3
from itertools import combinations
from pathlib import Path
import pickle
from random import choice, shuffle

from remi import gui, start, App

from .survey_utils import ExperimentType, User, Experiment, Tlx, Survey


class MyApp(App):
    def __init__(self, *args):
        super().__init__(*args)

    def main(self):
        self.users = []
        self.save_location = (Path(__file__).parent
                              .joinpath("../../data/raw/survey_data.pickle"))

        container = gui.Widget(width=500, margin="0px auto")

        menu = gui.Menu(width="100%", height="30px")

        menu_file = gui.MenuItem("File", width=100, height=30)
        menu_load = gui.MenuItem("Load...", width=100, height=30)
        menu_load.set_on_click_listener(self.cbk_select_pickle)
        menu_save = gui.MenuItem("Save", width=100, height=30)
        menu_save.set_on_click_listener(self.cbk_save)
        menu_save_as = gui.MenuItem("Save As...", width=100, height=30)
        menu_save_as.set_on_click_listener(self.cbk_save_as)

        menu.append(menu_file)
        menu_file.append(menu_load)
        menu_file.append(menu_save)
        menu_file.append(menu_save_as)

        menubar = gui.MenuBar(width="100%", height="30px")
        menubar.append(menu)

        self.uploader = gui.FileUploader("./", margin="10px")
        self.uploader.set_on_success_listener(self.cbk_load)

        self.save_location_label = gui.Label(f"Saving to {self.save_location}", margin="10px")

        self.table = gui.Table.new_from_list([("ID", "Name", "Onboard", "SPIRIT", "Both")],
            width=300, margin="10px")

        select_user_label = gui.Label("Select a user:", margin="10px")
        self.user_list = gui.ListView(margin="10px", width=300)
        self.user_list.set_on_selection_listener(self.cbk_user_selected)

        add_user_button = gui.Button("Add user", width=200, height=30, margin="10px")
        add_user_button.set_on_click_listener(self.cbk_add_user)

        save_button = gui.Button("Save", width=200, height=30, margin="10px")
        save_button.set_on_click_listener(self.cbk_save)

        try:
            self._load(self.save_location)
        except FileNotFoundError:
            pass
        self.update_table()
        self.update_user_list()

        container.append(menubar)
        container.append(self.uploader)
        container.append(self.save_location_label)
        container.append(self.table)
        container.append(select_user_label)
        container.append(self.user_list)
        container.append(add_user_button)
        container.append(save_button)

        return container

    def update_user_list(self):
        self.user_list.empty()
        for user in self.users:
            self.user_list.append(str(user), key=user)

    def update_table(self):
        self.table.empty(keep_title=True)
        self.table.append_from_list([
                (user.id_, user.name,
                    len([x for x in user.experiments if x.type_ == ExperimentType.Onboard]),
                    len([x for x in user.experiments if x.type_ == ExperimentType.Spirit]),
                    len([x for x in user.experiments if x.type_ == ExperimentType.Combined])
                ) for user in self.users])


    def cbk_add_user(self, widget):
        self.dialog = gui.GenericDialog(title="New user", message="Click Ok to save the user", width="500px")

        self.dname = gui.TextInput(width=200, height=30)
        self.dialog.add_field_with_label("dname", "Name", self.dname)

        self.dage = gui.TextInput(width=200, height=30)
        self.dialog.add_field_with_label("dage", "Age", self.dage)

        self.dgender = gui.DropDown.new_from_list(["Female", "Male", "Other"], width=200, height=30)
        self.dgender.select_by_value("Male")
        self.dialog.add_field_with_label("dgender", "Gender", self.dgender)

        self.dteleop = gui.TextInput(width=200, height=30)
        self.dteleop.set_value("0")
        self.dialog.add_field_with_label("dteleop", "Total hours flying teleoperated UAVs", self.dteleop)

        self.dflying = gui.TextInput(width=200, height=30)
        self.dflying.set_value("0")
        self.dialog.add_field_with_label("dflying", "Total hours flying other vehicles", self.dflying)

        self.dialog.set_on_confirm_dialog_listener(self.add_user_dialog_confirm)
        self.dialog.show(self)

    def cbk_user_selected(self, widget, user):
        self.dialog = gui.GenericDialog(title="User page", message="Click Ok to return", width="500px")

        self.dialog.add_field_with_label("dname", "ID", gui.Label(f"{user.id_}"))
        self.dialog.add_field_with_label("dname", "Name", gui.Label(f"{user.name}"))
        self.dnex = gui.Label(len(user.experiments))
        self.dialog.add_field_with_label("dnex", "Number of experiments", self.dnex)

        run_random_experiment_button = gui.Button("Run random experiment")
        run_random_experiment_button.set_on_click_listener(self.run_random_experiment, user)

        self._user_tlx_tables = {}
        self.update_tabs(user)

        self.dialog.add_field("drandom", run_random_experiment_button)
        self.dialog.add_field("dtabs", self.tab_box)
        self.dialog.set_on_confirm_dialog_listener(self.done_user_confirm)
        self.dialog.show(self)

    def update_tabs(self, user):
        self.tab_box = gui.TabBox(width="80%")
        for type_ in ExperimentType:
            self.widget = gui.Widget(width="100%")
            button = gui.Button(f"Run {type_.name} view experiment", margin="10px")
            button.set_on_click_listener(self.run_experiment, user, type_)
            self.widget.append(button)

            if type_ in self._user_tlx_tables:
                print("Found it!")
                self.widget.append(self._user_tlx_tables[type_])

            self.tab_box.add_tab(self.widget, f"{type_.name} view", None)


    def add_user_dialog_confirm(self, widget):
        name = self.dialog.get_field("dname").get_value()
        age = self.dialog.get_field("dage").get_value()
        gender = self.dialog.get_field("dgender").get_value()
        teleop = self.dialog.get_field("dteleop").get_value()
        flying = self.dialog.get_field("dflying").get_value()
        new_user = User(name, age, gender, teleop, flying)
        self.users.append(new_user)
        self.update_table()
        self.update_user_list()

    def done_user_confirm(self, widget):
        self.update_table()

    def run_random_experiment(self, widget, user):
        ran_types = {experiment.type_ for experiment in user.experiments}
        if (ExperimentType.Onboard in ran_types) and (ExperimentType.Spirit in ran_types):
            self.run_experiment(widget, user, choice(list(ExperimentType)))
        elif (ExperimentType.Onboard not in ran_types) and (ExperimentType.Spirit not in ran_types):
            self.run_experiment(widget, user, choice([ExperimentType.Onboard, ExperimentType.Spirit]))
        elif ExperimentType.Onboard not in ran_types:
            self.run_experiment(widget, user, ExperimentType.Onboard)
        else:
            self.run_experiment(widget, user, ExperimentType.Spirit)

    def run_experiment(self, widget, user, type_):
        self.dialog = gui.GenericDialog(title="Experiment", message=f"{user.name}, please run a {type_.name} view experiment.", width="600px")

        tlx_button = gui.Button("NASA TLX")
        tlx_button.set_on_click_listener(self.do_tlx, user, type_)
        self.dialog.add_field("dtlxbutton", tlx_button)

        survey_button = gui.Button("Survey")
        survey_button.set_on_click_listener(self.do_survey, user, type_)
        self.dialog.add_field("dsurveybutton", survey_button)

        self.survey = Survey()
        self.survey_sliders = {}
        self.tlx = Tlx()
        self.tlx_sliders = {}

        experiment = Experiment(user, type_, self.survey, self.tlx)

        self.dialog.set_on_confirm_dialog_listener(self.add_experiment, user, experiment)
        self.dialog.show(self)

    def do_tlx(self, widget, user, type_):
        self.dialog = gui.GenericDialog(title="NASA-TLX", message=f"NASA Task Load Index for the {type_.name} view experiment performed by {user.name}. How much did each component contribute to your task load? (scale from 0 to 20)", width="600px")

        for component in self.tlx.components.values():
            self.dialog.add_field(component.code, gui.Label(f"{component.name}: {component.description}", margin="10px"))
            slider = gui.Slider(component.score, 0, 20, 1, width="80%")
            slider.set_oninput_listener(self.tlx_slider_changed, component.code)
            slider_value = gui.Label(slider.get_value(), margin="10px")
            self.tlx_sliders[component.code] = (slider, slider_value)
            box = gui.Widget(width="100%", layout_orientation=gui.Widget.LAYOUT_HORIZONTAL, height=50)
            box.append(slider_value)
            box.append(slider)
            self.dialog.add_field(component.code + "_score", box)

        self.dialog.set_on_confirm_dialog_listener(self.tlx_done, user, type_)
        self.dialog.show(self)

    def tlx_slider_changed(self, widget, value, code):
        self.tlx_sliders[code][1].set_text(value)

    def tlx_done(self, widget, user, type_):
        for code, (slider, slider_value) in self.tlx_sliders.items():
            self.tlx.components[code].score = int(slider_value.get_text())
        self._tlx_weighting(user, type_)


    def do_survey(self, widget, user, type_):
        self.dialog = gui.GenericDialog(title="Survey", message=f"Survey for the {type_.name} view experiment performed by {user.name}. How would you rate each item? (scale from 1 to 7)", width="600px")

        for question in self.survey.questions.values():
            self.dialog.add_field(question.code, gui.Label(f"{question.description}", margin="10px"))
            slider = gui.Slider(question.score, 1, 7, 1, width="80%")
            slider.set_oninput_listener(self.survey_slider_changed, question.code)
            slider_value = gui.Label(slider.get_value(), margin="10px")
            self.survey_sliders[question.code] = (slider, slider_value)
            box = gui.Widget(width="100%", layout_orientation=gui.Widget.LAYOUT_HORIZONTAL, height=50)
            box.append(slider_value)
            box.append(slider)
            self.dialog.add_field(question.code + "_score", box)

        self.longform = gui.TextInput(single_line=False, hint="What other things would you like to say?", height="100px", margin="10px")

        self.dialog.add_field("dlongformlabel", gui.Label("Other feedback:", margin="10px"))
        self.dialog.add_field("dlongform", self.longform)

        self.dialog.set_on_confirm_dialog_listener(self.survey_done, user, type_)
        self.dialog.show(self)

    def survey_slider_changed(self, widget, value, code):
        self.survey_sliders[code][1].set_text(value)

    def survey_done(self, widget, user, type_):
        for code, (slider, slider_value) in self.survey_sliders.items():
            self.survey.questions[code].score = int(slider_value.get_text())
        self.survey.longform = self.longform.get_text()

    def _tlx_weighting(self, user, type_):
        self.all_combos = list(list(pair) for pair in combinations(self.tlx.components.keys(), 2))
        shuffle(self.all_combos)
        self.weights = {k: 0 for k in self.tlx.components.keys()}

        self.weight_index = 0
        self.pair = ["", ""]

        self.dialog = gui.GenericDialog(title="NASA-TLX Weighting", message=f"NASA Task Load Index for the {type_.name} view experiment performed by {user.name}. Which component do you feel contributed more to your task load?", width="300px")

        self.weight_progress_label = gui.Label(f"1/{len(self.all_combos)}")
        self.dialog.add_field("dweightprogress", self.weight_progress_label)

        box = gui.HBox(width="100%", height=50, margin="10px")
        self.button_left = gui.Button("", margin="10px")
        self.button_right = gui.Button("", margin="10px")
        box.append(self.button_left)
        box.append(self.button_right)
        self.dialog.add_field("dweightbox", box)

        self.pair = self.all_combos[self.weight_index]
        shuffle(self.pair)
        self.button_left.set_text(self.tlx.components[self.pair[0]].name)
        self.button_right.set_text(self.tlx.components[self.pair[1]].name)
        self.button_left.set_on_click_listener(self.weight_button_pressed, self.pair[0])
        self.button_right.set_on_click_listener(self.weight_button_pressed, self.pair[1])

        self.dialog.set_on_confirm_dialog_listener(self.weighting_done)
        self.dialog.show(self)


    def weighting_done(self, widget):
        for code, weight in self.weights.items():
            self.tlx.components[code].weight = weight


    def weight_button_pressed(self, widget, code):
        if self.weight_index == 14:
            self.dialog.confirm_dialog()
            return
        self.weights[code] += 1
        self.weight_index += 1

        self.weight_progress_label.set_text(f"{self.weight_index + 1} / {len(self.all_combos)}")
        self.pair = self.all_combos[self.weight_index]
        shuffle(self.pair)
        self.button_left.set_text(self.tlx.components[self.pair[0]].name)
        self.button_right.set_text(self.tlx.components[self.pair[1]].name)
        self.button_left.set_on_click_listener(self.weight_button_pressed, self.pair[0])
        self.button_right.set_on_click_listener(self.weight_button_pressed, self.pair[1])


    def add_experiment(self, widget, user, experiment):
        user.experiments.append(experiment)
        self.update_tabs(user)
        self.dnex.set_text(len(user.experiments))

    def cbk_save(self, widget):
        self._save()

    def _save(self):
        with open(self.save_location, "wb") as fout:
            pickle.dump(self.users, fout)
        self.notification_message("Saved", f"Data saved successfully to {self.save_location}")

    def _get_new_save_location(self, save_as=False):
        self.input_dialog = gui.InputDialog("Save location", "Path", width=500, height=160)
        self.input_dialog.set_on_confirm_value_listener(self.change_save_location, save_as)
        self.input_dialog.show(self)

    def change_save_location(self, widget, value, save_as):
        self.save_location = value
        self.save_location_label.set_text(f"Saving to {value}")
        if save_as:
            self._save()

    def cbk_save_as(self, widget):
        self._get_new_save_location(save_as=True)

    def cbk_select_pickle(self, widget):
        file_selector = gui.FileSelectionDialog("File Selection Dialog", "Select data pickle.", False, "../../data/raw")
        file_selector.set_on_confirm_value_listener(self.cbk_load)
        file_selector.show(self)

    def _load(self, filename):
        with open(filename, "rb") as fin:
            self.users = pickle.load(fin)
        User.count = max(user.id_ for user in self.users) + 1
        self.update_table()
        self.update_user_list()

    def cbk_load(self, widget, filenames):
        if isinstance(filenames, list):
            filenames = filenames[0]
        self._load(filenames)


if __name__ == "__main__":
    start(MyApp, title="Dashboard | SPIRIT")
