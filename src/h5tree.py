#!/usr/bin/env python

# TODO: * add search pattern / anti-pattern on datasets/groups
#       * nicer verbose output for scalar, h5refernce

import argparse
from collections import defaultdict
from functools import partial

import h5py
from termcolor import colored

# globals
total_groups = 0
total_datasets = 0
group_color = "green"
dataset_color = "yellow"
attr_color = "red"
scalar_color = attr_color
short_gap = " " * 2
long_gap = " " * 4

T_branch = "├── "
L_branch = "└── "
I_branch = "│   "
blank = " " * 4

terminated = defaultdict(lambda: False)


def str_count(n: int, name: str) -> str:
    """return a string representing number of groups/datasets"""
    if n != 1:
        return "{} {}s".format(n, name)
    else:
        return "{} {}".format(n, name)


def display_header(grouppath: str, filepath: str, group: h5py.Group, verbose: bool = False) -> None:
    """display the tree header"""
    if grouppath == "/":
        header = filepath
    else:
        header = "{}/{}".format(filepath, grouppath)

    if verbose:
        message = str_count(len(group), "object")
        if group.attrs:
            message += ", " + str_count(len(group.attrs), "attribute")
        header += short_gap + "({})".format(message)

    print(colored(header, group_color))


def display_attributes(group: h5py.Group, n: int, only_groups: bool, verbose: bool = False) -> None:
    """display the attribute on a single line"""
    num_attrs = len(group.attrs)
    front = ""
    for i in range(n):
        if terminated[i]:
            front = front + blank
        else:
            front = front + I_branch

    if num_attrs > 0:
        for i, attr in enumerate(group.attrs):
            if i == num_attrs - 1 and (len(group.keys()) == 0 or only_groups):
                front_edit = front + L_branch
            else:
                front_edit = front + T_branch
            attr_output = front_edit + colored(attr, attr_color)

            if verbose:
                attr_output += colored(short_gap + str(group.attrs[attr]), None)
            print(attr_output)


def display(
    verbose: bool, attributes: bool, groups: bool, level: int, pattern: str, name: str, obj
) -> None:
    """display the group or dataset on a single line"""
    global total_groups, total_datasets, terminated

    if pattern and pattern not in name:
        return

    depth = name.count("/")
    # abort if below level
    if level and depth >= level:
        return

    # reset terminated dict
    for d in terminated:
        if d > depth:
            terminated[d] = False

    # construct text at the front of line
    subname = name[name.rfind("/") + 1 :]
    front = ""
    for i in range(depth):
        if terminated[i]:
            front = front + blank
        else:
            front = front + I_branch

    if list(obj.parent.keys())[-1] == subname:
        front += L_branch
        terminated[depth] = True
    else:
        front += T_branch

    # is group
    if isinstance(obj, h5py.Group):
        output = front + colored(subname, group_color)
        if verbose:
            message = str_count(len(obj), "object")
            if obj.attrs:
                message += ", " + str_count(len(obj.attrs), "attribute")
            output += colored(short_gap + "({})".format(message), group_color)

        total_groups += 1
        print(output)

    # is dataset
    elif not groups:
        color = dataset_color
        if not obj.shape:
            color = scalar_color
        output = front + colored(subname, dataset_color)

        if verbose:
            output += short_gap + "{}, {}".format(obj.shape, obj.dtype)

        total_datasets += 1
        print(output)

    # include attributes
    if attributes:
        display_attributes(obj, depth + 1, verbose)


def main() -> None:
    # create the parser options
    parser = argparse.ArgumentParser(prog="h5tree")
    parser.add_argument("path", type=str, help="filepath/grouppath")
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose output")
    parser.add_argument("-a", "--attributes", action="store_true", help="show attributes")
    parser.add_argument("-g", "--groups", action="store_true", help="only show groups")
    parser.add_argument(
        "-L",
        "--level",
        nargs="?",
        type=int,
        help="maximum number of directories to recurse into",
        default=None,
    )
    parser.add_argument("-p", "--pattern", nargs="?", type=str, help="pattern", default=None)

    # argcomplete.autocomplete(parser)
    args = parser.parse_args()

    # parse the parsed input
    filepath = args.path
    ext = ".h5"
    sep_index = args.path.find(ext) + len(ext)

    filepath = args.path[:sep_index]
    grouppath = args.path[sep_index + 1 :]
    if not grouppath:
        grouppath = "/"

    # open file and print tree
    with h5py.File(filepath, "r") as f:
        group: h5py.Group = f[grouppath]  # type: ignore
        display_header(grouppath, filepath, group, args.verbose)
        if args.attributes:
            display_attributes(group, 1, args.verbose)

        group.visititems(
            partial(display, args.verbose, args.attributes, args.groups, args.level, args.pattern)
        )

    if args.verbose:
        footer = "{}, {}".format(
            str_count(total_groups, "group"), str_count(total_datasets, "dataset")
        )
        print("\n", footer, sep="")
