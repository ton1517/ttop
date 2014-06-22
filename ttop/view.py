import curses

from . import core

#=======================================
# View components
#=======================================

#--------------------
# ViewBase
#--------------------


class ViewBase(object):

    # The bottom 8 bits are the character proper, and upper bits are the attributes in curses.
    _STRIP_STR_BIT = int('11100000000', 2)

    def __init__(self, scr, color_theme, resource):
        self.scr = scr
        self.color_theme = color_theme
        self.resource = resource

    def draw(self, y, x, length):
        pass

    def addstr(self, y, x, str, attr=0):
        try:
            self.scr.addstr(y, x, str, attr)
        except curses.error:
            pass

    def addstr_with_existing_attr(self, y, x, str, attr=0):
        try:
            for i, s in enumerate(str):
                at = self.scr.inch(y, x + i) & ViewBase._STRIP_STR_BIT
                at = at or attr

                self.scr.addch(y, x + i, s, at)

        except curses.error:
            pass

#--------------------
# ResourceView
#--------------------


class ResourceView(ViewBase):

    def __init__(self, scr, color_theme, label, resource):
        ViewBase.__init__(self, scr, color_theme, resource)
        self.label = label

    def draw(self, y, x, length):
        self._draw_label(y, x, length)
        self._draw_frame(y, x, length)

        start_position, resource_length = self._calc_resource_area(y, x, length)
        self._draw_resource(y, x, length, start_position, resource_length)

        self._draw_info(y, x, length, self._get_info_str())

    def _draw_label(self, y, x, length):
        pass

    def _draw_frame(self, y, x, length):
        pass

    def _calc_resource_area(self, y, x, length):
        pass

    def _draw_resource(self, y, x, length, start_position, resource_length):
        pass

    def _get_info_str(self):
        pass

    def _draw_info(self, y, x, length, info_str):
        pass

#--------------------
# HorizontalLineGauge
#--------------------


class HorizontalLineGauge(ResourceView):

    """horizontal 1 line gauge.
    example:
        CPU [||||||||||       50%]
    """

    GAUGE_LEFT = "["
    GAUGE_RIGHT = "]"
    GAUGE = "|"
    GAUGE_BLANK = " "

    LABEL_WIDTH = 3

    def _draw_label(self, y, x, width):
        llabel = self.label.ljust(self.LABEL_WIDTH)
        self.addstr(y, x, llabel, self.color_theme.LABEL)

    def _draw_frame(self, y, x, width):
        self.addstr(y, x + self.LABEL_WIDTH, self.GAUGE_LEFT, self.color_theme.FRAME)
        self.addstr(y, x + width - len(self.GAUGE_RIGHT), self.GAUGE_RIGHT, self.color_theme.FRAME)

    def _calc_resource_area(self, y, x, width):
        now_x = x + self.LABEL_WIDTH + len(self.GAUGE_LEFT)
        resource_width = width - (now_x - x) - (len(self.GAUGE_RIGHT))
        return now_x, resource_width

    def _draw_resource(self, y, x, width, start_x, resource_width):
        pass

    def _get_info_str(self):
        pass

    def _draw_info(self, y, x, width, info_str):
        start_x = x + width - len(self.GAUGE_RIGHT) - len(info_str)
        self.addstr_with_existing_attr(y, start_x, info_str, self.color_theme.PERCENT)

#--------------------
# CPUHorizontalLineGauge
#--------------------


class CPUHorizontalLineGauge(HorizontalLineGauge):

    def _draw_resource(self, y, x, width, start_x, resource_width):
        user_n = int(self.resource.userPercent * resource_width)
        system_n = int(self.resource.systemPercent * resource_width)

        self.addstr(y, start_x, self.GAUGE * user_n, self.color_theme.CPU_GAUGE_USER)
        self.addstr(y, start_x + user_n, self.GAUGE * system_n, self.color_theme.CPU_GAUGE_SYSTEM)
        self.addstr(y, start_x + user_n + system_n, self.GAUGE_BLANK * (resource_width - (user_n + system_n)))

    def _get_info_str(self):
        return str(self.resource.usedPercent)

#--------------------
# MemoryHorizontalLineGauge
#--------------------


class MemoryHorizontalLineGauge(HorizontalLineGauge):

    def _draw_resource(self, y, x, width, start_x, resource_width):
        used_n = int(round(self.resource.percent * resource_width))
        self.addstr(y, start_x, self.GAUGE * used_n, self.color_theme.MEM_GAUGE_USED)
        self.addstr(y, start_x + used_n, self.GAUGE_BLANK * (resource_width - used_n))

    def _get_info_str(self):
        return str(self.resource)

#--------------------
# VerticalLineGauge
#--------------------


class VerticalLineGauge(ResourceView):

    GAUGE_TOP = "|~|"
    GAUGE_BOTTOM = "|_|"
    GAUGE = "|=|"
    GAUGE_BLANK = "   "

    WIDTH = 3

    def _draw_label(self, y, x, height):
        llabel = self.label[:self.WIDTH].center(self.WIDTH)
        self.addstr(y, x, llabel, self.color_theme.LABEL)

    def _draw_frame(self, y, x, height):
        self.addstr(y + 1, x, self.GAUGE_TOP, self.color_theme.FRAME)
        self.addstr(y + height - 1, x, self.GAUGE_BOTTOM, self.color_theme.FRAME)

    def _calc_resource_area(self, y, x, height):
        # y + GAUGE_TOP_HEIGHT (1) + LABEL_HEIGHT (1), height - GAUGE_TOP_HEIGHT (1) - GAUGE_BOTTOM_HEIGHT (1) - LABEL_HEIGHT (1)
        return y + 2, height - 3

    def _draw_resource(self, y, x, height, start_y, resource_height):
        pass

    def _get_info_str(self):
        pass

    def _draw_info(self, y, x, height, info_str):
        per = info_str[:self.WIDTH].rjust(self.WIDTH)
        self.addstr_with_existing_attr(y + 2, x, per, self.color_theme.PERCENT)

#--------------------
# CPUVerticalLineGauge
#--------------------


class CPUVerticalLineGauge(VerticalLineGauge):

    def _draw_resource(self, y, x, height, start_y, resource_height):
        user_n = int(self.resource.userPercent * resource_height)
        system_n = int(self.resource.systemPercent * resource_height)

        for i in range(resource_height - (user_n + system_n)):
            self.addstr(start_y + i, x, self.GAUGE_BLANK)

        now_y = start_y + resource_height - (user_n + system_n)
        for i in range(system_n):
            self.addstr(now_y + i, x, self.GAUGE, self.color_theme.CPU_GAUGE_SYSTEM)

        now_y += system_n
        for i in range(user_n):
            self.addstr(now_y + i, x, self.GAUGE, self.color_theme.CPU_GAUGE_USER)

    def _get_info_str(self):
        return str(self.resource.usedPercent)

#--------------------
# MemoryVerticalLineGauge
#--------------------


class MemoryVerticalLineGauge(VerticalLineGauge):

    def _draw_resource(self, y, x, height, start_y, resource_height):
        used_n = int(round(self.resource.percent * resource_height))

        for i in range(resource_height - used_n):
            self.addstr(start_y + i, x, self.GAUGE_BLANK)

        now_y = start_y + resource_height - used_n
        for i in range(used_n):
            self.addstr(now_y + i, x, self.GAUGE, self.color_theme.MEM_GAUGE_USED)

    def _get_info_str(self):
        return str(self.resource.percent)

#--------------------
# HorizontalStackView
#--------------------


class HorizontalStackView(ResourceView):

    GAUGE_LEFT = "|"
    GAUGE_RIGHT = "|"
    GAUGE_BOTTOM = "_"
    GAUGE = "|"
    GAUGE_BLANK = " "

    LABEL_WIDTH = 3

    def __init__(self, scr, color_theme, label, resource):
        ResourceView.__init__(self, scr, color_theme, label, resource)

        self.resource_history = core.ResourceHistory(resource.__class__)
        self.resources = []

    def _draw_label(self, y, x, length):
        height = length[1]
        llabel = self.label[:self.LABEL_WIDTH].ljust(self.LABEL_WIDTH)
        self.addstr(y + int(height / 2), x, llabel, self.color_theme.LABEL)

    def _draw_frame(self, y, x, length):
        width, height = length
        for i in range(height):
            self.addstr(y + i, x + self.LABEL_WIDTH, self.GAUGE_LEFT, self.color_theme.FRAME)
            self.addstr(y + i, x + width - 1, self.GAUGE_RIGHT, self.color_theme.FRAME)

    def _calc_resource_area(self, y, x, length):
        width, height = length
        return x + 4, (width - 5, height)

    def _draw_resource(self, y, x, length, start_x, resource_length):
        resource_width, resource_height = resource_length
        self.resource_history.pack(resource_width)
        self.resource_history.push(self.resource, resource_width)

        for i in range(resource_width):
            self._draw_gauge(y, start_x + i, resource_height, self.resource_history.get(i))

    def _get_info_str(self):
        pass

    def _draw_info(self, y, x, length, info_str):
        width = length[0]
        self.addstr_with_existing_attr(y, x + width - len(info_str) - 1, info_str, self.color_theme.PERCENT)

    def _draw_gauge(self, y, x, height, resource):
        pass

#--------------------
# CPUHorizontalStackView
#--------------------


class CPUHorizontalStackView(HorizontalStackView):

    def _get_info_str(self):
        return str(self.resource.usedPercent)

    def _draw_gauge(self, y, x, height, resource):
        user_n = int(resource.userPercent * height)
        system_n = int(resource.systemPercent * height)

        for i in range(height - (user_n + system_n)):
            self.addstr(y + i, x, self.GAUGE_BLANK)

        now_y = y + height - (user_n + system_n)
        for i in range(system_n):
            self.addstr(now_y + i, x, self.GAUGE, self.color_theme.CPU_GAUGE_SYSTEM)

        now_y += system_n
        for i in range(user_n):
            self.addstr(now_y + i, x, self.GAUGE, self.color_theme.CPU_GAUGE_USER)

#--------------------
# MemoryHorizontalStackView
#--------------------


class MemoryHorizontalStackView(HorizontalStackView):

    def _get_info_str(self):
        return str(self.resource)

    def _draw_gauge(self, y, x, height, resource):
        used_n = int(round(resource.percent * height))

        for i in range(height - used_n):
            self.addstr(y + i, x, self.GAUGE_BLANK)

        now_y = y + height - used_n
        for i in range(used_n):
            self.addstr(now_y + i, x, self.GAUGE, self.color_theme.MEM_GAUGE_USED)

#--------------------
# InfoTextLine
#--------------------


class InfoTextLine(ViewBase):

    def draw(self, y, x, width):
        uptime = str(self.resource.uptime)
        avg1 = "%.2f " % self.resource.loadavg.avg1
        avg5 = "%.2f " % self.resource.loadavg.avg5
        avg15 = "%.2f" % self.resource.loadavg.avg15
        procs = str(self.resource.procs)

        max_x = x + width

        now_x = x
        now_x = self._insstr(y, now_x, "Uptime ", self.color_theme.LABEL, max_x)
        now_x = self._insstr(y, now_x, uptime, self.color_theme.UPTIME, max_x)
        now_x = self._insstr(y, now_x, ", Load average ", self.color_theme.LABEL, max_x)
        now_x = self._insstr(y, now_x, avg1, self.color_theme.LOADAVG1, max_x)
        now_x = self._insstr(y, now_x, avg5, self.color_theme.LOADAVG5, max_x)
        now_x = self._insstr(y, now_x, avg15, self.color_theme.LOADAVG15, max_x)
        now_x = self._insstr(y, now_x, ", Processes ", self.color_theme.LABEL, max_x)
        now_x = self._insstr(y, now_x, procs, self.color_theme.PROCS, max_x)

    def _insstr(self, y, x, text, option, max_x):
        next_x = x + len(text)
        if x >= max_x:
            return next_x

        self.addstr(y, x, text, option)

        return next_x


#=======================================
# Layout
#=======================================

#--------------------
# Layout
#--------------------


class Layout(object):

    WIDTH = None
    HEIGHT = None

    def __init__(self, scr, color_theme, system_status):
        self.scr = scr
        self.color_theme = color_theme
        self.system_status = system_status

        self._init()

    def _init(self):
        pass

    def draw(self):
        height, width = self.scr.getmaxyx()
        self._draw(width, height)

    def _draw(self, width, height):
        pass

#--------------------
# HorizontalMinimalLayout
#--------------------


class HorizontalMinimalLayout(Layout):

    WIDTH = None
    HEIGHT = 3

    def _init(self):
        self.cpu = CPUHorizontalLineGauge(self.scr, self.color_theme, "CPU", self.system_status.cpu)
        self.memory = MemoryHorizontalLineGauge(self.scr, self.color_theme, "MEM", self.system_status.memory)
        self.textline = InfoTextLine(self.scr, self.color_theme, self.system_status)

    def _draw(self, width, height):
        self.cpu.draw(0, 0, width)
        self.memory.draw(1, 0, width)
        self.textline.draw(2, 0, width)

#--------------------
# HorizontalDefaultLayout
#--------------------


class HorizontalDefaultLayout(Layout):

    WIDTH = None
    HEIGHT = 4 + int((1 + core.CPU.NUM_CPUS) / 2) - int(not bool(core.CPU.NUM_CPUS - 1)) # int(not bool(core.CPU.NUM_CPUS - 1)) means 1 if NUM_CPUS == 1 else 0

    def _init(self):
        self.cpu = CPUHorizontalLineGauge(self.scr, self.color_theme, "CPU", self.system_status.cpu)
        self.each_cpu = [CPUHorizontalLineGauge(self.scr, self.color_theme, str(i + 1), cpu) for i, cpu in enumerate(self.system_status.each_cpu)] if core.CPU.NUM_CPUS > 1 else []
        self.memory = MemoryHorizontalLineGauge(self.scr, self.color_theme, "MEM", self.system_status.memory)
        self.swap = MemoryHorizontalLineGauge(self.scr, self.color_theme, "SWP", self.system_status.swap)
        self.textline = InfoTextLine(self.scr, self.color_theme, self.system_status)

    def _draw(self, width, height):
        center = int(width / 2)

        self.cpu.draw(0, 0, width)

        for i, cpu in enumerate(self.each_cpu):
            y, x = (int(i / 2) + 1, 0 if i % 2 == 0 else center)
            w = center if i % 2 == 0 else width - center
            cpu.draw(y, x, w)

        y = int(len(self.each_cpu) / 2) + 1
        self.memory.draw(y, 0, width)
        self.swap.draw(y + 1, 0, width)
        self.textline.draw(y + 2, 0, width)


#--------------------
# VerticalMinimalLayout
#--------------------

class VerticalMinimalLayout(Layout):

    WIDTH = 3 * 2
    HEIGHT = None

    def _init(self):
        self.cpu = CPUVerticalLineGauge(self.scr, self.color_theme, "CPU", self.system_status.cpu)
        self.memory = MemoryVerticalLineGauge(self.scr, self.color_theme, "MEM", self.system_status.memory)

    def _draw(self, width, height):
        self.cpu.draw(0, 0, height)
        self.memory.draw(0, self.cpu.WIDTH, height)

#--------------------
# VerticalDefaultLayout
#--------------------


class VerticalDefaultLayout(Layout):

    WIDTH = 9 + 3 * (int((1 + core.CPU.NUM_CPUS) / 2) - int(not bool(core.CPU.NUM_CPUS - 1))) # int(not bool(core.CPU.NUM_CPUS - 1)) means 1 if NUM_CPUS == 1 else 0
    HEIGHT = None

    def _init(self):
        self.cpu = CPUVerticalLineGauge(self.scr, self.color_theme, "CPU", self.system_status.cpu)
        self.each_cpu = [CPUVerticalLineGauge(self.scr, self.color_theme, str(i + 1), cpu) for i, cpu in enumerate(self.system_status.each_cpu)] if core.CPU.NUM_CPUS > 1 else []
        self.memory = MemoryVerticalLineGauge(self.scr, self.color_theme, "MEM", self.system_status.memory)
        self.swap = MemoryVerticalLineGauge(self.scr, self.color_theme, "SWP", self.system_status.swap)

    def _draw(self, width, height):
        gauge_w = self.cpu.WIDTH
        center = int(height / 2)

        self.cpu.draw(0, 0, height)

        for i, cpu in enumerate(self.each_cpu):
            y, x = (0 if i % 2 == 0 else center, (int(i / 2) + 1) * gauge_w)
            h = center if i % 2 == 0 else height - center
            cpu.draw(y, x, h)

        x = int((len(self.each_cpu) + 1) / 2 + 1) * gauge_w
        self.memory.draw(0, x, height)
        self.swap.draw(0, x + gauge_w, height)

#--------------------
# HorizontalStackLayout
#--------------------


class HorizontalStackLayout(Layout):

    WIDTH = None
    HEIGHT = 11

    def _init(self):
        self.cpu = CPUHorizontalStackView(self.scr, self.color_theme, "CPU", self.system_status.cpu)
        self.memory = MemoryHorizontalStackView(self.scr, self.color_theme, "MEM", self.system_status.memory)
        self.textline = InfoTextLine(self.scr, self.color_theme, self.system_status)

    def _draw(self, width, height):
        center = int(width / 2)
        self.cpu.draw(0, 0, (center, height - 1))
        self.memory.draw(0, center, (center, height - 1))
        self.textline.draw(height - 1, 0, width)

#--------------------
# VerticalStackLayout
#--------------------


class VerticalStackLayout(Layout):

    WIDTH = 25
    HEIGHT = None

    def _init(self):
        self.cpu = CPUHorizontalStackView(self.scr, self.color_theme, "CPU", self.system_status.cpu)
        self.memory = MemoryHorizontalStackView(self.scr, self.color_theme, "MEM", self.system_status.memory)

    def _draw(self, width, height):
        center = int(height / 2)
        self.cpu.draw(0, 0, (width, center))
        self.memory.draw(center, 0, (width, height - center))
