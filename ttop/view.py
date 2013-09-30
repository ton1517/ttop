import curses

#=======================================
# View components
#=======================================

#--------------------
# HorizontalLineGauge
#--------------------

class HorizontalLineGauge(object):
    """horizontal 1 line gauge.
    example:
        CPU [||||||||||       50%]
    """

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

#--------------------
# CPUHorizontalLineGauge
#--------------------

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

#--------------------
# MemoryHorizontalLineGauge
#--------------------

class MemoryHorizontalLineGauge(HorizontalLineGauge):

    def _draw_resource(self, y, x, width):
        used_n = int(round(self.resource.percent * width))

        self.scr.addstr(y, x, self.GAUGE*used_n, self.color_theme.MEM_GAUGE_USED)
        self.scr.addstr(self.GAUGE_BLANK * (width-used_n))

        text = str(self.resource.used)+"/"+str(self.resource.total)+" "+str(self.resource.percent)
        start_x = x + width - len(text)
        self.scr.addstr(y, start_x, text, self.color_theme.PERCENT)

#--------------------
# VerticalLineGauge
#--------------------

class VerticalLineGauge(object):

    GAUGE_TOP = "/=\\"
    GAUGE_BOTTOM = "\\=/"
    GAUGE = "|=|"
    GAUGE_BLANK = "   "

    def __init__(self, scr, color_theme, label, resource):
        self.scr = scr
        self.color_theme = color_theme
        self.label = label
        self.resource = resource
        self.width = 3

    def draw(self, y, x, height):
        llabel = self.label[:self.width].center(self.width)
        self.scr.addstr(y, x, llabel, self.color_theme.LABEL)
        self.scr.addstr(y+1, x, self.GAUGE_TOP, self.color_theme.FRAME)

        height_resource = height - 3
        self._draw_resource(y+2, x, height_resource)

        self.scr.addstr(y + height-1, x, self.GAUGE_BOTTOM, self.color_theme.FRAME)

    def _draw_resource(self, y, x, height):
        pass

#--------------------
# CPUVerticalLineGauge
#--------------------

class CPUVerticalLineGauge(VerticalLineGauge):

    def _draw_resource(self, y, x, height):
        user_n = int(round(self.resource.userPercent* height))
        system_n = int(round(self.resource.systemPercent * height))

        for i in range(height-(user_n+system_n)):
            self.scr.addstr(y + i, x, self.GAUGE_BLANK)

        now_y = self.scr.getyx()[0] + 1
        for i in range(system_n):
            self.scr.addstr(now_y + i, x, self.GAUGE, self.color_theme.CPU_GAUGE_SYSTEM)

        now_y = self.scr.getyx()[0] + 1
        for i in range(user_n):
            self.scr.addstr(now_y + i, x, self.GAUGE, self.color_theme.CPU_GAUGE_USER)

        last_y = self.scr.getyx()[0] + 1

        per = str(self.resource.usedPercent)[:self.width].rjust(self.width)
        self.scr.addstr(y, x, per, self.color_theme.PERCENT)

        self.scr.move(y+height, x)

#--------------------
# MemoryVerticalLineGauge
#--------------------

class MemoryVerticalLineGauge(VerticalLineGauge):

    def _draw_resource(self, y, x, height):
        used_n = int(round(self.resource.percent * height))

        for i in range(height-used_n):
            self.scr.addstr(y + i, x, self.GAUGE_BLANK)

        now_y = self.scr.getyx()[0] + 1
        for i in range(used_n):
            self.scr.addstr(now_y + i, x, self.GAUGE, self.color_theme.MEM_GAUGE_USED)

        per = str(self.resource.percent)[:self.width].rjust(self.width)
        self.scr.addstr(y, x, per, self.color_theme.PERCENT)

        self.scr.move(y+height, x)

#=======================================
# Layout
#=======================================

#--------------------
# Layout
#--------------------

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

#--------------------
# HorizontalMinimalLayout
#--------------------

class HorizontalMinimalLayout(Layout):

    def _init(self):
        self.cpu = CPUHorizontalLineGauge(self.scr, self.color_theme, "CPU", self.system_status.cpu)
        self.memory = MemoryHorizontalLineGauge(self.scr, self.color_theme, "MEM", self.system_status.memory)

    def draw(self):
        (height, width) = self.scr.getmaxyx()
        center = int(width/2)
        self.cpu.draw(0, 0, center)
        self.memory.draw(0, center, center)

#--------------------
# HorizontalDefaultLayout
#--------------------

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

#--------------------
# VerticalMinimalLayout
#--------------------

class VerticalMinimalLayout(Layout):

    def _init(self):
        self.cpu = CPUVerticalLineGauge(self.scr, self.color_theme, "CPU", self.system_status.cpu)
        self.memory = MemoryVerticalLineGauge(self.scr, self.color_theme, "MEM", self.system_status.memory)

    def draw(self):
        (height, width) = self.scr.getmaxyx()
        center = int(height/2)
        self.cpu.draw(0, 0, center)
        self.memory.draw(center, 0, center)

