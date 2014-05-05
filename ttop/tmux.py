import os
import subprocess

#=======================================
# tmux
#=======================================


def call(command):
    """call tmux subcommand."""
    (stdout, stderr) = subprocess.Popen("tmux " + command, shell=True, stdout=subprocess.PIPE).communicate()
    return stdout


def get_version():
    version = call("-V")
    import re
    result = re.search(b"[\d\.]+", version)
    return float(result.group())


def in_tmux():
    """if process is in tmux, return True."""
    return bool(os.getenv("TMUX"))


def swap_pane():
    """swap current pane for previous pane."""
    call("swap-pane -D")


def move_last_pane():
    """move focus from current pane to previous pane."""
    call("last-pane")


def resize_pane(width=None, height=None):
    """resize pane"""
    resize_option = ""

    if width:
        resize_option += " -x " + str(width)
    if height:
        resize_option += " -y " + str(height)

    call("resize-pane " + resize_option)


def split_window(vertical=True, horizontal=False, command=None):
    """new pane and exec command."""
    option = "-v" if vertical else "-h"

    if command:
        option += " \"" + command + "\""

    call("split-window " + option)
