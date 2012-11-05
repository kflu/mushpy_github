__all__ = [
        "common",
        "trigger",
        "consts",
        "task",
        "terminal",
        ]

from consts import *
from trigger import *
from task import *
from terminal import *

def init(ax):
    """Initialize this package with necessary global variables.

    This function must be called before using it.
    """
    # inject the ax and the world objects
    import __builtin__
    __builtin__.ax = ax
    __builtin__.world = ax._scriptEngine_.globalNameSpaceModule.world
    world.note("Successfully loaded Mushpy")

    # redirect stdout and stderr
    import sys
    sys.stdout = Terminal(title='stdout', time_stamp=True)
    sys.stderr = sys.stdout

