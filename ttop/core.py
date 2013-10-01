from hurry.filesize import size
import psutil

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

