from setuptools import setup

import ttop 

def join_files(*files):
    content = ""
    for name in files:
        f = open(name)
        content += f.read() + "\n"
        f.close()
    return content

setup(
    name = 'ttop',
    version = ttop.__version__,
    description = ttop.__doc__.strip(),
    long_description = join_files("README.rst", "CHANGES.rst"),
    url = ttop.__homepage__,
    license = ttop.__license__,
    author = ttop.__author__,
    author_email = ttop.__email__,
    packages = ["ttop"],
    entry_points = {
        "console_scripts": ["ttop = ttop.ttop:main"]
    },
    install_requires = open("requirements.txt").read().splitlines(),
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Console :: Curses',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Unix',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Topic :: Utilities',
    ]
)
