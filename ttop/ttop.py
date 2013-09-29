#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ttop
"""

import sys
import curses
from multiprocessing import Process

import psutil
from hurry.filesize import size

#=======================================
# Config
#=======================================

interval = 1 
EXIT_KEYS = (ord("q"), ord("Q"), 27) # 27:ESC

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


#=======================================
# Views
#=======================================

#--------------------
# HorizontalLineGauge
#--------------------

class HorizontalLineGauge(object):

    GAUGE_LEFT = "["
    GAUGE_RIGHT = "]"
    GAUGE = "|"
    GAUGE_BLANK = " "

    def __init__(self, scr, color_theme, label, resource):
        self.scr = scr
        self.color_theme = color_theme
        self.label = label
        self.resource = resource

    def draw(self, y, x, width):
        llabel = self.label.ljust(3)
        self.scr.addstr(y, x, llabel, self.color_theme.LABEL)
        self.scr.addstr(self.GAUGE_LEFT, self.color_theme.FRAME)

        (now_y, now_x) = self.scr.getyx()
        width_resource = width - (now_x - x) - (len(self.GAUGE_RIGHT)+1)
        self._draw_resource(now_y, now_x, width_resource)

        self.scr.addstr(self.GAUGE_RIGHT+" ", self.color_theme.FRAME)

    def _draw_resource(self, y, x, width):
        pass

class CPUHorizontalLineGauge(HorizontalLineGauge):

    def _draw_resource(self, y, x, width):
        user_n = int(round(self.resource.userPercent* width))
        system_n = int(round(self.resource.systemPercent * width))

        self.scr.addstr(y, x, self.GAUGE*user_n, self.color_theme.CPU_GAUGE_USER)
        self.scr.addstr(self.GAUGE*system_n, self.color_theme.CPU_GAUGE_SYSTEM)
        self.scr.addstr(self.GAUGE_BLANK * (width-(user_n+system_n)))

        per = str(self.resource.usedPercent)
        start_x = x + width - len(per)
        self.scr.addstr(y, start_x, per, self.color_theme.PERCENT)

class MemoryHorizontalLineGauge(HorizontalLineGauge):

    def _draw_resource(self, y, x, width):
        used_n = int(round(self.resource.percent * width))

        self.scr.addstr(y, x, self.GAUGE*used_n, self.color_theme.MEM_GAUGE_USED)
        self.scr.addstr(self.GAUGE_BLANK * (width-used_n))

        text = str(self.resource.used)+"/"+str(self.resource.total)+" "+str(self.resource.percent)
        start_x = x + width - len(text)
        self.scr.addstr(y, start_x, text, self.color_theme.PERCENT)

#=======================================
# Layout
#=======================================

class Layout(object):

    def __init__(self, scr, color_theme, system_status):
        self.scr = scr
        self.color_theme = color_theme
        self.system_status = system_status

        self._init()

    def _init(self):
        pass

    def draw(self):
        pass

class HorizontalMinimalLayout(Layout):

    def _init(self):
        self.cpu = CPUHorizontalLineGauge(self.scr, self.color_theme, "CPU", self.system_status.cpu)
        self.memory = MemoryHorizontalLineGauge(self.scr, self.color_theme, "MEM", self.system_status.memory)

    def draw(self):
        (height, width) = self.scr.getmaxyx()
        center = int(width/2)
        self.cpu.draw(0, 0, center)
        self.memory.draw(0, center, center)

class HorizontalDefaultLayout(Layout):

    def _init(self):
        self.cpu = CPUHorizontalLineGauge(self.scr, self.color_theme, "CPU", self.system_status.cpu)
        self.each_cpu = [CPUHorizontalLineGauge(self.scr, self.color_theme, str(i+1), cpu) for i, cpu in enumerate(self.system_status.each_cpu)]
        self.memory = MemoryHorizontalLineGauge(self.scr, self.color_theme, "MEM", self.system_status.memory)
        self.swap = MemoryHorizontalLineGauge(self.scr, self.color_theme, "SWP", self.system_status.swap)

    def draw(self):
        (height, width) = self.scr.getmaxyx()
        center = int(width/2)

        self.cpu.draw(0, 0, width)

        for i, cpu in enumerate(self.each_cpu):
            y, x =  (int(i/2)+1, 0 if i%2 == 0  else center)
            w = center if i%2 == 0 else width-center
            cpu.draw(y, x, w)

        y = int(len(self.each_cpu)/2)+1
        self.memory.draw(y, 0, width)
        self.swap.draw(y+1, 0, width)


#=======================================
# Core Classes
#=======================================

#--------------------
# Percent
#--------------------

class Percent(float):
    """Percent type.

    >>> p = Percent(95.1)
    >>> print(p.real)
    0.951
    >>> print(p)
    95%
    """

    def __new__(cls, value=0.0):
        value = value/100

        return float.__new__(cls, value)

    def __init__(self, percent):
        self.percent = percent

    def __str__(self):
        return str(int(round(self.percent))) + "%"

#--------------------
# Bytes
#--------------------

class Bytes(int):

    def __str__(self):
        return size(self.real)

#--------------------
# CPU
#--------------------

class CPU(object):

    NUM_CPUS = psutil.NUM_CPUS

    def __init__(self, user=0, system=0, idle=0):
        self.update(user, system, idle)

    def update(self, user, system, idle):
        self.userPercent = Percent(user)
        self.systemPercent = Percent(system)
        self.usedPercent =  Percent(user+system)
        self.idlePercent = Percent(idle)

    def __str__(self):
        return str(self.usedPercent)

#--------------------
# Memory
#--------------------

class Memory(object):

    def __init__(self, total=1, used=0):
        self.update(total, used)

    def update(self, total, used):
        self.total = Bytes(total)
        self.used = Bytes(used)
        self.percent = Percent((1.0*used/total)*100)

    def __str__(self):
        return "%s %s/%s" % (self.percent, self.used, self.total)

#--------------------
# SystemStatus
#--------------------

class SystemStatus(object):
    """this class have system status, CPU percent, Memory percent, etc."""

    def __init__(self):
        self.cpu = CPU()
        self.each_cpu = [CPU() for i in range(CPU.NUM_CPUS)]
        self.memory = Memory()
        self.swap = Memory()

        self.update(0)

    def update(self, interval = 0.1):
        """poll system status.(blocking)"""

        times_percent = psutil.cpu_times_percent(interval=interval, percpu=True)

        self.__update_cpu(times_percent)
        for i, c in enumerate(times_percent):
            self.each_cpu[i].update(c.user, c.system, c.idle)

        self.__update_memory(self.memory, psutil.virtual_memory())
        self.__update_memory(self.swap, psutil.swap_memory())

    def __update_cpu(self, cpuper):
        sum_user = 0
        sum_system = 0
        sum_idle = 0
        l = len(cpuper)
        for cpu in cpuper:
            sum_user += cpu.user
            sum_system += cpu.system
            sum_idle += cpu.idle

        self.cpu.update(sum_user/l, sum_system/l, sum_idle/l)

    def __update_memory(self, mem, tuple_mem):
        mem.update(tuple_mem.total, tuple_mem.used)

#=======================================
# Functions
#=======================================

def init_curses():
    """must be called in hook_curses function."""

    ## use terminal color.
    curses.use_default_colors()
    ## hide cursor
    curses.curs_set(0)

def start_process(scr):
    p = Process(target=update_handler, args=(scr, ))
    p.daemon = True
    p.start()

def update_handler(scr):
    ss = SystemStatus()
    color_table = ColorTable()
    theme = DefaultColorTheme(color_table)
    layout = HorizontalDefaultLayout(scr, theme, ss)

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

def hook_curses(scr):
    init_curses()
    start_process(scr)
    wait_key_and_exit(scr)

def main():
    curses.wrapper(hook_curses)

if __name__ == "__main__":
    main()
