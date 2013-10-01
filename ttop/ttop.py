#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ttop is CUI graphical system monitor.
this tools is designed for use with tmux(or screen).

Usage:
  ttop [--no-color] [--interval <s>] [--no-tmux] [normal | minimal | stack] [horizontal | vertical]
  ttop -h | --help
  ttop -v | --version

Options:
  -h --help           show help.
  -v --version        show version.
  -C --no-color       use monocolor.
  -i --interval <s>   refresh interval(second) [default: 1.0].
  -T --no-tmux        don't use tmux mode.
"""

from . import __author__, __version__, __license__
from . import __doc__ as __description__

import sys
import curses
from multiprocessing import Process

from docopt import docopt

import core
import color
import view
import tmux

#=======================================
# Config
#=======================================

EXIT_KEYS = (ord("q"), ord("Q"), 27) # 27:ESC

#=======================================
# Functions
#=======================================

def init_curses():
    """must be called in hook_curses function."""

    ## use terminal color.
    if curses.has_colors():
        curses.use_default_colors()
    ## hide cursor
    curses.curs_set(0)

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
    return color.MonoColorTheme(color_table) if arguments.no_color else color.DefaultColorTheme(color_table)

def select_layout_class(arguments):
    layout_class = None

    if arguments.normal and arguments.horizontal:
        layout_class = view.HorizontalDefaultLayout
    elif arguments.minimal and arguments.horizontal:
        layout_class = view.HorizontalMinimalLayout
    elif arguments.stack and arguments.horizontal:
        pass
    elif arguments.normal and arguments.vertical:
        layout_class = view.VerticalDefaultLayout
    elif arguments.minimal and arguments.vertical:
        layout_class = view.VerticalMinimalLayout
    elif arguments.stack and arguments.vertical:
        pass
    else:
        pass

    return layout_class


def start_process(scr, arguments):
    p = Process(target=update_handler, args=(scr, arguments))
    p.daemon = True
    p.start()

def update_handler(scr, arguments):
    ss = core.SystemStatus()
    theme = select_color_theme(arguments)
    layout_class = select_layout_class(arguments)

    if layout_class is None:
        scr.addstr("not yet implements.")
        scr.refresh()
        return

    layout = layout_class(scr, theme, ss)

    interval = arguments.interval

    while True:
        ss.update(interval)
        scr.erase()
        layout.draw()
        scr.refresh()

def wait_key_and_exit(scr):
    while True:
        c = scr.getch()

        if c in EXIT_KEYS:
            sys.exit()

def hook_curses(scr, arguments):
    init_curses()
    start_process(scr, arguments)
    wait_key_and_exit(scr)

def main():
    arg_dict = docopt(__doc__, version=__version__)
    arguments = core.Arguments(arg_dict)

    if tmux.in_tmux() and not arguments.no_tmux:
        new_pane_and_exec_process(arguments)
        sys.exit()

    curses.wrapper(hook_curses, arguments)

if __name__ == "__main__":
    main()
