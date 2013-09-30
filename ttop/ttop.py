#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ttop is CUI graphical system monitor.
this tools is designed for use with tmux(or screen).

Usage:
  ttop [--no-color] [--interval <s>]
  ttop -h | --help
  ttop -v | --version

Options:
  -h --help           show help.
  -v --version        show version.
  -C --no-color       use monocolor.
  -i --interval <s>   refresh interval(second) [default: 1].
"""

from . import __author__, __version__, __license__
from . import __doc__ as __description__

import sys
import curses
from multiprocessing import Process

from docopt import docopt

from core import *
from color import *
from view import *

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

def start_process(scr, arguments):
    p = Process(target=update_handler, args=(scr, arguments))
    p.daemon = True
    p.start()

def update_handler(scr, arguments):
    ss = SystemStatus()
    color_table = ColorTable()
    theme = MonoColorTheme(color_table) if arguments["--no-color"] else DefaultColorTheme(color_table)
    layout = HorizontalDefaultLayout(scr, theme, ss)

    interval = float(arguments["--interval"])

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
    arguments = docopt(__doc__, version=__version__)
    curses.wrapper(hook_curses, arguments)

if __name__ == "__main__":
    main()
