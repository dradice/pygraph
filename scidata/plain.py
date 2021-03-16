import numpy

def parse(liter, indexed=False):
    """
    Imports the data from a given iterator and returns a 2D numpy.array

    If indexed is True then this returns a list of 2D numpy.array each
    containing a chunk of the data. Data chunks in the input have to be
    separed by a double empty line.
    """
    if indexed:
        out = []
        block = 0
        data = []
        for line in liter:
            if line == '\n':
                block = block + 1
                if block == 2:
                    block = 0
                    out.append(numpy.array(data))
                    data = []
            else:
                if line[0] != '#':
                    data.append([float(x) for x in line.split()])
        out.append(numpy.array(data))
        return out
    else:
        return numpy.loadtxt(liter)

def parsefile(filename, indexed=False):
    """
    Imports the data from a given file and returns a 2D numpy.array
    """
    return parse(open(filename, 'r'), indexed)
