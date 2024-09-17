import glob
import math
import numpy
import re

import scidata.monodataset
import scidata.plain
import scidata.utils

def parse_1D(liter, axis, reflevel=None, column=1):
    """
    Parse a 1D CarpetASCII line iterator and returns a
    scidata.monodataset.dataset object

    * liter    : an iterable object containing the lines of the file to parse
    * axis     : a character, "x", "y", "z" or "d" for the direction
    * reflevel : which refinement level to parse
    """
    phi = {
            "x" : lambda x, y, z : x,
            "y" : lambda x, y, z : y,
            "z" : lambda x, y, z : z,
            "d" : lambda x, y, z : math.copysign(math.sqrt((x**2 + y**2 +\
                    z**2)), x)
            }[axis]

    if column is None:
        column = 12
    else:
        column -= 1

    dataset = scidata.monodataset.dataset()

    dataset.nframes = 0
    dataset.time    = []
    dataset.data_x  = []
    dataset.data_y  = []
    dataset.ranges  = []

    old_iter = - numpy.inf
    si = 0
    ei = 0

    data_xy = []

    for line in liter:
        if line[0] != "#" and line[0] != "\n":
            ldata = line.split()

            iter = int(ldata[0])
            rlev = int(ldata[2])

            if reflevel is None or rlev == reflevel:
                if iter > old_iter:
                    old_iter = iter
                    if si != ei:
                        dataset.ranges.append((si, ei))
                    si = ei
                    dataset.time.append(float(ldata[8]))
                    dataset.metadata.append({})
                    dataset.nframes += 1

                    ei += len(data_xy)

                    for xy in data_xy:
                        dataset.data_x.append(xy[0])
                        dataset.data_y.append(xy[1])

                    data_xy = []

                data_xy.append((phi(float(ldata[9]), float(ldata[10]),\
                        float(ldata[11])), float(ldata[column])))

    dataset.ranges.append((si, ei))

    for xy in data_xy:
        dataset.data_x.append(xy[0])
        dataset.data_y.append(xy[1])

    dataset.ranges.append((ei, len(dataset.data_x)))

    dataset.data_x = numpy.array(dataset.data_x)
    dataset.data_y = numpy.array(dataset.data_y)

    return dataset

def parse_1D_file(filename, reflevel=None, column=None):
    """
    Parse a 1D CarpetASCII file and retuns a scidata.monodataset.dataset
    * filename : is the file name
    * dataset  : is the scidata.monodataset.dataset object
    """
    fre = re.match(r"(.+)\.([xyzd])\.(\w+)", filename)

    axis = fre.group(2)
    ext  = fre.group(3)

    if ext != "asc":
        raise scidata.utils.FileTypeError(filename)

    return parse_1D(open(filename, "r"), axis, reflevel, column)

def load_1D_files(filelist, reflevel=None, column=None):
    """
    Loads all the files in the list

    This function returns a dictionary {filename: dataset}, where
    * filename : is the file name
    * dataset  : is the scidata.monodataset.dataset object
    """
    return dict([(filename, parse_1D_file(filename, reflevel, column))
        for filename in filelist])

def load_1D_dir(directory, reflevel=None, column=None):
    """
    Loads all the asc files in a given directory into memory

    This functions returns a dictionary { varname: dataset }, where
    * varname : is the variable name (taken from the filename)
    * dataset : is the scidata.monodataset.dataset object
    """
    out = []

    for f in glob.glob(directory + "/*.?.asc"):
        out.append((scidata.utils.basename(f),
            parse_1D_file(f, reflevel, column)))
    return dict(out)

def parse_scalar_file(filename, column=None):
    """"
    Parse a 0D CarpetIOScalar ASCII file
    """
    rawdata = scidata.plain.parsefile(filename)

    dataset = scidata.monodataset.dataset()

    dataset.nframes  = 1
    dataset.time     = [0]
    dataset.metadata = [{}]
    if column is None:
        try:
            dataset.data_x = rawdata[:, 8]
            dataset.data_y = rawdata[:, 12]
        except IndexError:
            try:
                dataset.data_x = rawdata[:, 1]
                dataset.data_y = rawdata[:, 2]
            except IndexError:
                dataset.data_x = rawdata[:, 0]
                dataset.data_y = rawdata[:, 1]
    else:
        column -= 1
        if column == 1:
            dataset.data_x = rawdata[:, 0]
        if column == 2:
            dataset.data_x = rawdata[:, 1]
        else:
            dataset.data_x = rawdata[:, 8]
        dataset.data_y = rawdata[:, column]
    dataset.ranges   = [(0, len(dataset.data_x))]

    return dataset
