#!/usr/bin/env python2
# (C) 2015  Jean Nassar
# Released under BSD
import glob
import imp
import inspect
from lxml import etree as et
import os
import subprocess as sp

import rospkg
import tqdm
import yaml


CONFIG_FILE = "launch_params.yaml"
NAMESPACES = {"xacro": "{http://www.ros.org/wiki/xacro}"}
# et.register_namespace("xacro", "http://www.ros.org/wiki/xacro")


def get_ros_dir(package, dirname):
    return os.path.join(rospkg.RosPack().get_path(package), dirname)


def get_file_root(path):
    """
    >>> get_file_root("/tmp/test.txt")
    'test'

    """
    return os.path.splitext(os.path.basename(path))[0]


def compile_xacro(inpath, outpath, stdout):
    sp.call("rosrun xacro xacro {inpath} --inorder -o {outpath}"
            .format(inpath=inpath, outpath=outpath).split(),
            stdout=stdout)
    

def get_past_image_keys(launch_params):
    keys = {}
    past_image_params = launch_params["past_image"]
    for eval_method in past_image_params:
        if eval_method != "general":
            keys[eval_method] = past_image_params[eval_method].keys()
    return keys


def load_xml(path):
    parser = et.XMLParser(remove_blank_text=True)
    return et.parse(path, parser)
    

def remove_old_elements(node):
    for element in node.findall("{}if".format(NAMESPACES["xacro"])):
        node.remove(element)


def add_new_keys(node, keys):
    for method_name, key_list in keys.items():
        element = et.Element("{}if".format(NAMESPACES["xacro"]),
                             attrib={"value": "${{method == '{}'}}"
                             .format(method_name)})
        for key in key_list:
            et.SubElement(element, "param",
                          attrib={"name": key,
                                  "value": "${{method_ns['{}']}}".format(key)})
        node.append(element)


def add_message(tree):
    root = tree.getroot()
    root.addprevious(
        et.Comment("Generated automatically from launch config file.")
    )


def update_past_image_generator(keys, path="xacro/past_images.launch.xacro"):
    tree = load_xml(path)
    for node in tree.findall("node[@name='past_image_selector']"):
        remove_old_elements(node)
        add_new_keys(node, keys)
    tree.write(path, encoding="utf-8", xml_declaration=True, pretty_print=True)


def verify_coeffs(method, past_image_keys):
    """

    Parameters
    ----------
    method
    past_image_keys

    Raises
    ------
    AttributeError
        If a key does not exist.
    TypeError
        If a key is not callable.

    """
    method_params = past_image_keys[method]
    os.chdir(get_ros_dir("spirit", "src"))
    helpers = imp.load_source("helpers", "helpers.py")  # Needed for import
    evaluators = imp.load_source("evaluators", "evaluators.py")

    components = [param.split("coeff_", 1)[1] for param in method_params
                  if param.startswith("coeff_")]
    evaluator = getattr(evaluators, method)

    bad_keys = [component for component in components
                if not (inspect.ismethod(getattr(evaluator, component))
                        or inspect.isfunction(getattr(evaluator, component)))]
    if bad_keys:
        raise TypeError("The following components are not callable: {}"
                        .format(bad_keys))


def main():
    os.chdir(get_ros_dir("spirit", "config"))
    with open(CONFIG_FILE) as fin:
        launch_params = yaml.load(fin)
    method = launch_params["past_image"]["general"]["eval_method"]
    past_image_keys = get_past_image_keys(launch_params)
    verify_coeffs(method, past_image_keys)

    os.chdir(get_ros_dir("spirit", "launch"))
    update_past_image_generator(past_image_keys)

    with open(os.devnull, "w") as DEVNULL:
        for path in tqdm.tqdm(glob.glob("xacro/*.xacro"),
                              desc="Regenerating launch files",
                              unit=" files",
                              leave=True):
            root = get_file_root(path)
            compile_xacro(path, os.path.join("launchers", root), DEVNULL)


if __name__ == "__main__":
    main()
