from hurry.filesize import size
import psutil
import copy
import curses

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
        return "%s/%s %s" % (self.used, self.total, self.percent)

#--------------------
# LoadAverage
#--------------------
import os
class LoadAverage(object):

    def __init__(self):
        self.avg1 = 0.0
        self.avg5 = 0.0
        self.avg15 = 0.0

    def update(self):
        try:
            self.avg1, self.avg5, self.avg15 = os.getloadavg()
        except os.error:
            self.avg1, self.avg5, self.avg15 = 0.0, 0.0, 0.0

    def __str__(self):
        return "%.2f %.2f %.2f" % (self.avg1, self.avg5, self.avg15)

#--------------------
# Uptime
#--------------------
import uptime
class Uptime(object):

    def __init__(self):
        self.uptime = 0
        self.days = 0
        self.hours = 0
        self.minutes = 0
        self.seconds = 0

    def update(self):
        self.uptime = uptime.uptime()
        up = self.uptime
        self.days, up = up // 86400, up % 86400
        self.hours, up = up // 3600, up % 3600
        self.minutes, up = up // 60, up % 60
        self.seconds = up

    def __str__(self):
        times = ""
        if self.days:
            times += "%d day%s " % (self.days, 's' if self.days != 1 else '')
        times += "%d:%d:%d" % (self.hours, self.minutes, self.seconds)
        return times

#--------------------
# ResourceHistory
#--------------------

class ResourceHistory(object):

    def __init__(self, resource_class):
        self.resource_class = resource_class
        self.resources = []

    def get(self, index):
        return self.resources[index]

    def pack(self, length):
        res_len = len(self.resources)
        if length < res_len:
            del_len = res_len - length
            del self.resources[:del_len]
        elif length > res_len:
            push_len = length - res_len
            self.resources = [self.resource_class() for i in range(push_len)] + self.resources

    def push(self, resource, max_len):
        self.resources.append(copy.copy(resource))
        if len(self.resources) > max_len:
            del_len = len(self.resources) - max_len
            del self.resources[:del_len]

#--------------------
# SystemStatus
#--------------------

class SystemStatus(object):
    """this class have system status, CPU percent, Memory percent, etc."""

    def __init__(self, update_interval):
        self.update_interval = update_interval
        self.cpu = CPU()
        self.each_cpu = [CPU() for i in range(CPU.NUM_CPUS)]
        self.memory = Memory()
        self.swap = Memory()
        self.loadavg = LoadAverage()
        self.uptime = Uptime()

    def update(self):
        """poll system status.(blocking)"""
        times_percent = psutil.cpu_times_percent(interval=self.update_interval, percpu=True)

        self.__update_cpu(times_percent)
        for i, c in enumerate(times_percent):
            self.each_cpu[i].update(c.user, c.system, c.idle)

        self.__update_memory(self.memory, psutil.virtual_memory())
        self.__update_memory(self.swap, psutil.swap_memory())

        self.loadavg.update()
        self.uptime.update()

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

#--------------------
# Updater
#--------------------

class Updater(object):

    def __init__(self, scr, system_status, layout):
        self.scr = scr
        self.system_status = system_status
        self.layout = layout

    def update(self):
        try:
            self.scr.erase()
            self.layout.draw()
            self.scr.refresh()
        except curses.error as e:
            (h, w) = self.scr.getmaxyx()
            (y, x) = self.scr.getyx()
            if x == (w-1) and y == (h-1):
                self.scr.refresh()
            else:
                raise e

        self.system_status.update()


#--------------------
# Arguments
#--------------------

class Arguments(object):

    def __init__(self, arg):
        self.no_color = arg["--no-color"]
        self.interval = float(arg["--interval"])
        self.no_tmux = arg["--no-tmux"]
        self.normal = arg["normal"]
        self.minimal = arg["minimal"]
        self.stack = arg["stack"]
        self.horizontal = arg["horizontal"]
        self.vertical = arg["vertical"]

        # default view is "normal".
        if not self.normal and not self.minimal and not self.stack:
            self.normal = True

        # default style is "horizontal".
        if not self.horizontal and not self.vertical:
            self.horizontal = True

