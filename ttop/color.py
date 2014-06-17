import curses

#=======================================
# Colors
#=======================================

#--------------------
# ColorTable
#--------------------


class ColorTable(object):

    """define color pair.
    must new this class in curses.wrapper hook function.
    """

    def __init__(self):
        self.pair_number = 0

        self.DEFAULT = curses.color_pair(0)
        self.BLACK = self.__define_color(curses.COLOR_BLACK, -1)
        self.WHITE = self.__define_color(curses.COLOR_WHITE, -1)
        self.BLUE = self.__define_color(curses.COLOR_BLUE, -1)
        self.CYAN = self.__define_color(curses.COLOR_CYAN, -1)
        self.GREEN = self.__define_color(curses.COLOR_GREEN, -1)
        self.MAGENTA = self.__define_color(curses.COLOR_MAGENTA, -1)
        self.RED = self.__define_color(curses.COLOR_RED, -1)
        self.YELLOW = self.__define_color(curses.COLOR_YELLOW, -1)

        self.BBLACK = self.BLACK | curses.A_BOLD
        self.BWHITE = self.WHITE | curses.A_BOLD
        self.BBLUE = self.BLUE | curses.A_BOLD
        self.BCYAN = self.CYAN | curses.A_BOLD
        self.BGREEN = self.GREEN | curses.A_BOLD
        self.BMAGENTA = self.MAGENTA | curses.A_BOLD
        self.BRED = self.RED | curses.A_BOLD
        self.BYELLOW = self.YELLOW | curses.A_BOLD

    def __define_color(self, fg, bg):
        self.pair_number += 1
        curses.init_pair(self.pair_number, fg, bg)
        return curses.color_pair(self.pair_number)

#--------------------
# MonoColorTheme
#--------------------


class MonoColorTheme(object):

    """define monocolor theme."""

    def __init__(self, color):
        self.color = color

        self.LABEL = color.DEFAULT
        self.FRAME = color.DEFAULT
        self.PERCENT = color.DEFAULT

        self.CPU_GAUGE_USER = color.DEFAULT
        self.CPU_GAUGE_SYSTEM = color.DEFAULT

        self.MEM_GAUGE_USED = color.DEFAULT

        self.UPTIME = color.DEFAULT
        self.LOADAVG1 = color.DEFAULT
        self.LOADAVG5 = color.DEFAULT
        self.LOADAVG15 = color.DEFAULT
        self.PROCS = color.DEFAULT

#--------------------
# DefaultColorTheme
#--------------------


class DefaultColorTheme(MonoColorTheme):

    """define color theme."""

    def __init__(self, color):
        MonoColorTheme.__init__(self, color)

        self.PERCENT = color.BBLACK

        self.CPU_GAUGE_USER = color.GREEN
        self.CPU_GAUGE_SYSTEM = color.RED

        self.MEM_GAUGE_USED = color.GREEN

        self.UPTIME = color.GREEN
        self.LOADAVG1 = color.BBLACK
        self.LOADAVG5 = color.WHITE
        self.LOADAVG15 = color.BWHITE
        self.PROCS = color.GREEN

#--------------------
# BrightColorTheme
#--------------------


class BrightColorTheme(MonoColorTheme):

    def __init__(self, color):
        MonoColorTheme.__init__(self, color)

        self.PERCENT = color.BWHITE

        self.CPU_GAUGE_USER = color.BGREEN
        self.CPU_GAUGE_SYSTEM = color.BRED

        self.MEM_GAUGE_USED = color.BGREEN

        self.UPTIME = color.YELLOW
        self.LOADAVG1 = color.BBLACK
        self.LOADAVG5 = color.WHITE
        self.LOADAVG15 = color.BWHITE
        self.PROCS = color.YELLOW

        self.LABEL = color.WHITE
