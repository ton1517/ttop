ttop
==========
ttop is CUI graphical system monitor.
this tools is designed for use with tmux.

.. image:: https://raw.github.com/wiki/ton1517/ttop/images/ttop.gif

installation
------------
install from github

::

    git clone git@github.com:ton1517/ttop.git
    cd ttop
    python setup.py install

usage
------
::

    Usage:
      ttop [--no-color] [--interval <s>] [--no-tmux] [normal | minimal | stack] [horizontal | vertical]
      ttop -h | --help
      ttop -v | --version

    Options:
      -h --help           show help.
      -v --version        show version.
      -C --no-color       use monocolor.
      -i --interval <s>   refresh interval(second) [default: 1.0].
      -T --no-tmux        don't use tmux mode.


