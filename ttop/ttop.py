#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ttop is CLI graphical system monitor.
this tools is designed for use with tmux.
https://github.com/ton1517/ttop

Usage:
  ttop [--color <theme>] [--no-color] [--interval <s>] [--no-tmux] [normal | minimal | stack] [horizontal | vertical]
  ttop -h | --help
  ttop -v | --version

Options:
  -h --help           show help.
  -v --version        show version.
  -c --color <theme>  change color thema. (theme: mono, default, bright)
  -C --no-color       use monocolor.
  -i --interval <s>   refresh interval(second) [default: 1.0].
  -T --no-tmux        don't use tmux mode.
"""
from __future__ import absolute_import

from ttop import __version__

import sys
import curses
from multiprocessing import Process
import time

from docopt import docopt

from ttop import core, color, view, tmux
from ttop.color import *

#=======================================
# Config
#=======================================

EXIT_KEYS = (ord("q"), ord("Q"), 27)  # 27:ESC

#=======================================
# Functions
#=======================================


def init_curses():
    """must be called in hook_curses function."""

    # use terminal color.
    if curses.has_colors():
        curses.use_default_colors()
    # hide cursor
    curses.curs_set(0)


def create_updater(scr, arguments):
    ss = core.SystemStatus()
    theme = select_color_theme(arguments)
    layout_class = select_layout_class(arguments)
    layout = layout_class(scr, theme, ss)

    return core.Updater(scr, ss, arguments.interval, layout)


def new_pane_and_exec_process(arguments):
    layout_class = select_layout_class(arguments)
    width, height = (layout_class.WIDTH, layout_class.HEIGHT)
    command = " ".join(sys.argv) + " --no-tmux"

    # if horizontal option, split-window -v. if vertical option, split-window -h.
    tmux.split_window(arguments.horizontal, arguments.vertical, command)
    tmux.move_last_pane()
    tmux.resize_pane(width, height)
    tmux.swap_pane()


def select_color_theme(arguments):
    color_table = color.ColorTable()
    color_theme_name = "default"

    if arguments.no_color:
        color_theme_name = "mono"
    elif arguments.color:
        color_theme_name = arguments.color

    theme_class_name = color_theme_name.capitalize() + "ColorTheme"
    theme_class = globals().get(theme_class_name, DefaultColorTheme)
    return theme_class(color_table)


def select_layout_class(arguments):
    layout_class = None

    if arguments.normal and arguments.horizontal:
        layout_class = view.HorizontalDefaultLayout
    elif arguments.minimal and arguments.horizontal:
        layout_class = view.HorizontalMinimalLayout
    elif arguments.stack and arguments.horizontal:
        layout_class = view.HorizontalStackLayout
    elif arguments.normal and arguments.vertical:
        layout_class = view.VerticalDefaultLayout
    elif arguments.minimal and arguments.vertical:
        layout_class = view.VerticalMinimalLayout
    elif arguments.stack and arguments.vertical:
        layout_class = view.VerticalStackLayout

    return layout_class


def start_process(updater):
    p = Process(target=update_handler, args=(updater,))
    p.daemon = True
    p.start()


def update_handler(updater):
    while True:
        updater.update()
        time.sleep(updater.interval)


def wait_key_and_exit(scr):
    while True:
        c = scr.getch()

        if c in EXIT_KEYS:
            sys.exit()


def hook_curses(scr, arguments):
    init_curses()

    updater = create_updater(scr, arguments)
    start_process(updater)

    wait_key_and_exit(scr)


def main():
    arg_dict = docopt(__doc__, version="ttop " + __version__)
    arguments = core.Arguments(arg_dict)

    if tmux.in_tmux() and not arguments.no_tmux:
        if tmux.get_version() < 1.8:
            print("your tmux version is " + str(tmux.get_version()) + ".")
            print("only support tmux 1.8 or higher.")
            print("you should use --no-tmux option.")
        else:
            new_pane_and_exec_process(arguments)

        sys.exit()

    curses.wrapper(hook_curses, arguments)

if __name__ == "__main__":
    main()
