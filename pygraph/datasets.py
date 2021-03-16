from copy import deepcopy
from numpy import *
from pygraph.common import debug_print
import pygraph.common as common
import scidata.carpet.ascii as asc
import scidata.carpet.hdf5 as h5
import scidata.monodataset as md
import scidata.pygraph as pyg
import scidata.xgraph as xg
from scidata.utils import FileTypeError
import re

def D(x):
    q = diff(x)
    return array([q[0]] + list(q))

class DataSetType:
    D0 = 0
    D1 = 1

    @staticmethod
    def guess_from_name(fname):
        if re.match(r".+\.(\w+)$", fname).group(1) == "asc" and \
                re.match(r".+\.[xyzd]\.asc$", fname) is None:
            return DataSetType.D0
        return DataSetType.D1

class DataSet:
    """
    Class storing a dataset

    Members
    * name            : DataSet name
    * dset_type       : type of dataset (DataSetType.D0 or DataSetType.D1)
    * data            : transformed data (could be a pointer to rawdata)
    * std_data_files  : list of tuples: (filename, type, col), type/col could be None
    * map_data_files  : list of typles: (filename, type, col), type/col could be None
    * rawdata         : scidata.monodataset with the raw data
    * reflevel        : read a particular refinement level of the data (optional)
    * transform       : data transformation
    """
    def __init__(self, name, dset_type=None, reflevel=None):
        assert(dset_type == DataSetType.D0 or dset_type == DataSetType.D1)
        self.name           = name
        self.dset_type      = dset_type
        self.data           = None
        self.std_data_files = []
        self.map_data_files = None
        self.rawdata        = None
        self.reflevel       = reflevel
        self.index          = 0
        self.transform      = ('x', 'y')     # Identity transformation

    def add_datafile(self, fname, ftype=None, col=None):
        """
        Add another datafile to the list of files to read
        """
        self.std_data_files.append((fname, ftype, col))

    def add_mapfile(self, fname, ftype=None, col=None):
        """
        Add another map datafile to the list of map datafiles
        """
        if self.map_data_files is None:
            self.map_data_files = []
        self.map_data_files.append((fname, ftype, col))

    def get_frame(self, time):
        """
        Gets a frame at the given time
        """
        if common.settings['Animation/Smooth']:
            return self.data.time_interp(time)
        else:
            return self.data.find_frame(time)

    def read_file(self, fname, ftype=None, col=None):
        """
        Reads a single file and returns a scidata.monodataset
        """
        debug_print("R " + fname)

        # There is only one 0D dataformat supported
        if self.dset_type == DataSetType.D0:
            return asc.parse_scalar_file(fname)

        # Guess from the file extension
        if ftype is None:
            # Check if it is a 1D Carpet ASCII file
            if re.match(r".+\.[xyzd]\.asc$", fname) is not None:
                ftype = "CarpetIOASCII"
            # Check file extension
            else:
                ext = re.match(r".+\.(\w+)$", fname).group(1)
                if ext == "pyg":
                    ftype = "pygraph"
                elif ext == "xg" or ext == "yg":
                    ftype = "xg"
                elif ext == "h5":
                    if pyg.validate(fname):
                        ftype = "pygraph"
                    else:
                        ftype = "h5"
                else:
                    raise FileTypeError(fname)

        # Read the file
        if ftype == "xg":
            return xg.parsefile(fname, col)
        elif ftype == "pygraph":
            return pyg.parsefile(fname, float64)
        elif ftype == "CarpetIOASCII":
            return asc.parse_1D_file(fname, self.reflevel, col)
        elif ftype == "h5":
            return h5.parse_1D_file(fname, self.reflevel, float64)
        else:
            raise FileTypeError(fname)

    def read_file_list(self, data_files):
        """
        Reads data from a list of (filename, filetype) tuples
        and returns a scidata.monodataset

        NOTE: D0 datasets can only read 0D data
              D1 datasets can only read 1D data
        """
        L   = [self.read_file(fname, ftype, col)
                for fname, ftype, col in data_files]
        if self.dset_type == DataSetType.D0:
            frame = L[0].frame(0)
            for f in L[1:]:
                frame.merge(f.frame(0))
            out = md.dataset()
            out.import_framelist([frame])
        else:
            out = L[0]
            out.merge(L[1:])
        out.sort()
        return out

    def read_data(self):
        """
        Read the data from the files
        """
        assert(len(self.std_data_files) > 0)
        self.rawdata = self.read_file_list(self.std_data_files)
        if self.map_data_files is not None:
            mapdset = self.read_file_list(self.map_data_files)
            assert(self.rawdata.data_x.shape[0] == mapdset.data_y.shape[0])
            self.rawdata.data_x = mapdset.data_y

    def transform_data(self):
        """
        Apply a data transformation
        """
        if self.transform != ('x', 'y'):
            self.data = deepcopy(self.rawdata)

            f = eval("lambda x, y, t: " + self.transform[0])
            g = eval("lambda x, y, t: " + self.transform[1])

            L = []
            for frame in self.rawdata:
                frame.data_x = f(frame.data_x, frame.data_y, frame.time)
                frame.data_y = g(frame.data_x, frame.data_y, frame.time)
                L.append(frame)
            self.data.import_framelist(L)
        else:
            self.data = self.rawdata
        self.data.purge_nans()

