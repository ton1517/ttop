ttop
==========
ttop is CLI graphical system monitor.
this tools is designed for use with `tmux <http://tmux.sourceforge.net/>`_.

.. image:: https://raw.github.com/wiki/ton1517/ttop/images/ttop.gif


requirements
-------------

python

- python >= 3.3.1 or 2.7.3

tmux

- tmux >= 1.8

python library

- docopt >= 0.6.1
- psutil >= 2.1.1

installation
------------
install from pypi

::

    easy_install ttop

or

::

    pip install ttop
    

install from github

::

    git clone https://github.com/ton1517/ttop.git
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


