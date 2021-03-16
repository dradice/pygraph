import re

class FileTypeError(Exception):
    """
    Data file type not supported
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def basename(filename):
    """
    Get the base name of the given filename
    """
    return re.match(r"(.+)\.(\w+)", filename).group(1)

def extension(filename):
    """
    Get the extension of the given filename
    """
    return re.match(r"(.+)\.(\w+)", filename).group(2)

