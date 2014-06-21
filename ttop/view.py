import curses

from . import core

#=======================================
# View components
#=======================================

#--------------------
# ViewBase
#--------------------


class ViewBase(object):

    def __init__(self, scr, color_theme, resource):
        self.scr = scr
        self.color_theme = color_theme
        self.resource = resource

    def draw(self, y, x, length):
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
        self.scr.addstr(y, x, llabel, self.color_theme.LABEL)

    def _draw_frame(self, y, x, width):
        self.scr.addstr(y, x + self.LABEL_WIDTH, self.GAUGE_LEFT, self.color_theme.FRAME)
        self.scr.addstr(y, x + width - len(self.GAUGE_RIGHT), self.GAUGE_RIGHT, self.color_theme.FRAME)

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
        self.scr.addstr(y, start_x, info_str, self.color_theme.PERCENT)

#--------------------
# CPUHorizontalLineGauge
#--------------------


class CPUHorizontalLineGauge(HorizontalLineGauge):

    def _draw_resource(self, y, x, width, start_x, resource_width):
        user_n = int(self.resource.userPercent * resource_width)
        system_n = int(self.resource.systemPercent * resource_width)

        self.scr.addstr(y, start_x, self.GAUGE * user_n, self.color_theme.CPU_GAUGE_USER)
        self.scr.addstr(y, start_x + user_n, self.GAUGE * system_n, self.color_theme.CPU_GAUGE_SYSTEM)
        self.scr.addstr(y, start_x + user_n + system_n, self.GAUGE_BLANK * (resource_width - (user_n + system_n)))

    def _get_info_str(self):
        return str(self.resource.usedPercent)

#--------------------
# MemoryHorizontalLineGauge
#--------------------


class MemoryHorizontalLineGauge(HorizontalLineGauge):

    def _draw_resource(self, y, x, width, start_x, resource_width):
        used_n = int(round(self.resource.percent * resource_width))
        self.scr.addstr(y, start_x, self.GAUGE * used_n, self.color_theme.MEM_GAUGE_USED)
        self.scr.addstr(y, start_x + used_n, self.GAUGE_BLANK * (resource_width - used_n))

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
        self.scr.insstr(y, x, llabel, self.color_theme.LABEL)

    def _draw_frame(self, y, x, height):
        self.scr.insstr(y + 1, x, self.GAUGE_TOP, self.color_theme.FRAME)
        self.scr.insstr(y + height - 1, x, self.GAUGE_BOTTOM, self.color_theme.FRAME)

    def _calc_resource_area(self, y, x, height):
        # y + GAUGE_TOP_HEIGHT (1) + LABEL_HEIGHT (1), height - GAUGE_TOP_HEIGHT (1) - GAUGE_BOTTOM_HEIGHT (1) - LABEL_HEIGHT (1)
        return y + 2, height - 3

    def _draw_resource(self, y, x, height, start_y, resource_height):
        pass

    def _get_info_str(self):
        pass

    def _draw_info(self, y, x, height, info_str):
        per = info_str[:self.WIDTH].rjust(self.WIDTH)
        self.scr.addstr(y + 2, x, per, self.color_theme.PERCENT)

#--------------------
# CPUVerticalLineGauge
#--------------------


class CPUVerticalLineGauge(VerticalLineGauge):

    def _draw_resource(self, y, x, height, start_y, resource_height):
        user_n = int(self.resource.userPercent * resource_height)
        system_n = int(self.resource.systemPercent * resource_height)

        for i in range(resource_height - (user_n + system_n)):
            self.scr.insstr(start_y + i, x, self.GAUGE_BLANK)

        now_y = start_y + resource_height - (user_n + system_n)
        for i in range(system_n):
            self.scr.insstr(now_y + i, x, self.GAUGE, self.color_theme.CPU_GAUGE_SYSTEM)

        now_y += system_n
        for i in range(user_n):
            self.scr.insstr(now_y + i, x, self.GAUGE, self.color_theme.CPU_GAUGE_USER)

    def _get_info_str(self):
        return str(self.resource.usedPercent)

#--------------------
# MemoryVerticalLineGauge
#--------------------


class MemoryVerticalLineGauge(VerticalLineGauge):

    def _draw_resource(self, y, x, height, start_y, resource_height):
        used_n = int(round(self.resource.percent * resource_height))

        for i in range(resource_height - used_n):
            self.scr.insstr(start_y + i, x, self.GAUGE_BLANK)

        now_y = start_y + resource_height - used_n
        for i in range(used_n):
            self.scr.insstr(now_y + i, x, self.GAUGE, self.color_theme.MEM_GAUGE_USED)

    def _get_info_str(self):
        return str(self.resource.percent)

#--------------------
# HorizontalStackView
#--------------------


class HorizontalStackView(object):

    GAUGE_LEFT = "|"
    GAUGE_RIGHT = "|"
    GAUGE_BOTTOM = "_"
    GAUGE = "|"
    GAUGE_BLANK = " "

    def __init__(self, scr, color_theme, label, resource):
        self.scr = scr
        self.color_theme = color_theme
        self.label = label
        self.resource = resource

        self.resource_history = core.ResourceHistory(resource.__class__)
        self.resources = []
        self.text = ""

    def draw(self, y, x, width, height):
        llabel = self.label[:3].ljust(3)
        self.scr.insstr(y + int(height / 2), x, llabel, self.color_theme.LABEL)
        for i in range(height):
            self.scr.insstr(y + i, x + len(llabel), self.GAUGE_LEFT, self.color_theme.FRAME)

        width_resource = width - 5

        self.resource_history.pack(width_resource)
        self.resource_history.push(self.resource, width_resource)
        self._draw_resource(y, x + 4, width_resource, height)

        for i in range(height):
            self.scr.insstr(y + i, x + width - 1, self.GAUGE_LEFT, self.color_theme.FRAME)

    def _draw_text(self, y, x, text, max_width):
        self.scr.addnstr(y, x, text, max_width, self.color_theme.PERCENT)

    def _draw_resource(self, y, x, width, height):
        for i in range(width):
            self._draw_gauge(y, x + i, height, self.resource_history.get(i))

    def _draw_gauge(self, y, x, height, resource):
        pass

#--------------------
# CPUHorizontalStackView
#--------------------


class CPUHorizontalStackView(HorizontalStackView):

    def _draw_resource(self, y, x, width, height):
        super(CPUHorizontalStackView, self)._draw_resource(y, x, width, height)
        per = str(self.resource.usedPercent)
        self._draw_text(y, x + width - len(per), per, width)

    def _draw_gauge(self, y, x, height, resource):
        user_n = int(resource.userPercent * height)
        system_n = int(resource.systemPercent * height)

        for i in range(height - (user_n + system_n)):
            self.scr.insstr(y + i, x, self.GAUGE_BLANK)

        now_y = y + height - (user_n + system_n)
        for i in range(system_n):
            self.scr.insstr(now_y + i, x, self.GAUGE, self.color_theme.CPU_GAUGE_SYSTEM)

        now_y += system_n
        for i in range(user_n):
            self.scr.insstr(now_y + i, x, self.GAUGE, self.color_theme.CPU_GAUGE_USER)

#--------------------
# MemoryHorizontalStackView
#--------------------


class MemoryHorizontalStackView(HorizontalStackView):

    def _draw_resource(self, y, x, width, height):
        super(MemoryHorizontalStackView, self)._draw_resource(y, x, width, height)
        per = str(self.resource)
        self._draw_text(y, x + width - len(per), per, width)

    def _draw_gauge(self, y, x, height, resource):
        used_n = int(round(resource.percent * height))

        for i in range(height - used_n):
            self.scr.insstr(y + i, x, self.GAUGE_BLANK)

        now_y = y + height - used_n
        for i in range(used_n):
            self.scr.insstr(now_y + i, x, self.GAUGE, self.color_theme.MEM_GAUGE_USED)

#--------------------
# InfoTextLine
#--------------------


class InfoTextLine(object):

    def __init__(self, scr, color_theme, system_status):
        self.scr = scr
        self.color_theme = color_theme
        self.system_status = system_status

    def draw(self, y, x, width):
        uptime = str(self.system_status.uptime)
        avg1 = "%.2f " % self.system_status.loadavg.avg1
        avg5 = "%.2f " % self.system_status.loadavg.avg5
        avg15 = "%.2f" % self.system_status.loadavg.avg15
        procs = str(self.system_status.procs)

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

        self.scr.insstr(y, x, text, option)

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
    HEIGHT = 4 + int((1 + core.CPU.NUM_CPUS) / 2)

    def _init(self):
        self.cpu = CPUHorizontalLineGauge(self.scr, self.color_theme, "CPU", self.system_status.cpu)
        self.each_cpu = [CPUHorizontalLineGauge(self.scr, self.color_theme, str(i + 1), cpu) for i, cpu in enumerate(self.system_status.each_cpu)]
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

    WIDTH = 9 + 3 * int((1 + core.CPU.NUM_CPUS) / 2)
    HEIGHT = None

    def _init(self):
        self.cpu = CPUVerticalLineGauge(self.scr, self.color_theme, "CPU", self.system_status.cpu)
        self.each_cpu = [CPUVerticalLineGauge(self.scr, self.color_theme, str(i + 1), cpu) for i, cpu in enumerate(self.system_status.each_cpu)]
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
        self.cpu.draw(0, 0, center, height - 1)
        self.memory.draw(0, center, center, height - 1)
        self.textline.draw(height-1, 0, width)

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
        self.cpu.draw(0, 0, width, center)
        self.memory.draw(center, 0, width, center)

