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

        self.GRAY = self.BLACK | curses.A_BOLD

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
        self.color= color

        self.LABEL = color.DEFAULT
        self.FRAME = color.DEFAULT
        self.PERCENT = color.DEFAULT

        self.CPU_GAUGE_USER = color.DEFAULT
        self.CPU_GAUGE_SYSTEM = color.DEFAULT

        self.MEM_GAUGE_USED = color.DEFAULT

#--------------------
# DefaultColorTheme
#--------------------

class DefaultColorTheme(MonoColorTheme):
    """define color theme."""

    def __init__(self, color):
        MonoColorTheme.__init__(self, color)

        self.PERCENT = color.GRAY

        self.CPU_GAUGE_USER = color.GREEN
        self.CPU_GAUGE_SYSTEM = color.RED

        self.MEM_GAUGE_USED = color.GREEN


