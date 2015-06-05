"""
Module provides a method that executes shell commands
"""
from subprocess import Popen, PIPE


def sh(script):
    """
    Runs a bash script (provided as a string) and returns the output.
    ^not sure that it's fully functional
    """
    (out, err) = Popen(list(script.split()), stdout=PIPE).communicate()
    return str(out)
