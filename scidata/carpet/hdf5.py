import h5py
import numpy
import os
import re

import scidata.carpet.grid
import scidata.monodataset
import scidata.utils

class dataset:
    """
    A class representing a CarpetHDF5 dataset

    We store a dictionary { key : [file] } to be able to track the location
    of the data within the multiple files

    The metadata is storead a list and accessed using an SQL-like select
    mechanism

    For convenience we also store a list of all the iterations

    * dtype      : datatype
    * haveidx    : True if idx files are available

    * ofobjs     : dict of currently open file objects
    * oflist     : list of names of currently open files
    * maxnfiles  : maximum number of files to keep open at any given time

    * contents   : dict of file names

    * itdata     : dict of (iteration, list), where list is a list of tuples
                   (var, it, tl, rl, c) where it == iteration
    * itlist     : list of available iterations
    * iterations : alias of itlist

    * metadata   : list of tuples in the form (var, it, tl, rl, c)
    """

    def __init__(self, filenames=None, maxnfiles=128):
        """
        Initialize the dataset

        * filenames : can either be a list of filenames or a single filename
        * maxnfiles : maximum number of files to keep open at any given time
        """
        self.haveidx    = True

        self.ofobjs     = {}
        self.oflist     = []
        self.maxnfiles  = maxnfiles

        self.contents   = {}

        self.itdata     = {}
        self.itlist     = []

        self.metadata   = []

        # In the initialization stage we convert dictionaries to lists
        self.contents = []
        self.itlist   = set()

        rawdata = {}

        if filenames is None:
            filenames = []
        if isinstance(filenames, str):
            filenames = [filenames]

        for filename in filenames:
            if re.match(r".*\.idx\.h5", filename) is not None:
                continue

            index = filename[:-3] + ".idx.h5"
            if os.path.isfile(index):
                dfile = h5py.File(index, mode='r')
            else:
                dfile = h5py.File(filename, mode='r')
                self.haveidx = False

            file_keys = []
            dfile.visit(file_keys.append)
            dfile.close()

            for name in file_keys:
                metadata = self.parse_dset_name(name)
                if metadata is not None:
                    self.contents.append((name, filename))

                    it = metadata[1]
                    if it in self.itdata:
                        self.itdata[it].append(metadata)
                    else:
                        self.itdata[it] = [metadata]

                    self.contents.append((name, filename))
                    self.itlist.add(it)
                    self.metadata.append(metadata)

        self.contents   = dict(self.contents)
        self.itlist     = sorted(list(self.itlist))
        self.iterations = self.itlist

        self.dtype  = self.get_dataset().dtype
        self.close_files()

    def reset(self, filenames=None, maxnfiles=128):
        return self.__init__(filenames, maxnfiles)

    def close_files(self):
        """
        Close any open files so that the dataset can be serialized
        """
        for fname in self.oflist:
            self.ofobjs[fname].close()
            del self.ofobjs[fname]
        self.ofobjs = {}
        self.oflist = []

    def parse_dset_name(self, string):
        """
        Parse a dataset name

        This returns a tuple:
                (variable, iteration, timelevel, reflevel, component)
        or None if the given name does not match any known pattern.
        """
        dset_re = r"(\w+:?:?\w*\[?\d*\]?) it=(\d+) tl=(\d+) rl=(\d+) c=(\d+)$"
        name_re = re.match(dset_re, string)
        if name_re is not None:
            variable  = name_re.group(1)
            iteration = int(name_re.group(2))
            timelevel = int(name_re.group(3))
            reflevel  = int(name_re.group(4))
            component = int(name_re.group(5))
            return variable, iteration, timelevel, reflevel, component

        dset_re = r"(\w+:?:?\w*\[?\d*\]?) it=(\d+) tl=(\d+) rl=(\d+)$"
        name_re = re.match(dset_re, string)
        if name_re is not None:
            variable  = name_re.group(1)
            iteration = int(name_re.group(2))
            timelevel = int(name_re.group(3))
            reflevel  = int(name_re.group(4))
            component = None
            return variable, iteration, timelevel, reflevel, component

        dset_re = r"(\w+:?:?\w*\[?\d*\]?) it=(\d+) tl=(\d+) c=(\d+)$"
        name_re = re.match(dset_re, string)
        if name_re is not None:
            variable  = name_re.group(1)
            iteration = int(name_re.group(2))
            timelevel = int(name_re.group(3))
            reflevel  = None
            component = int(name_re.group(4))
            return variable, iteration, timelevel, reflevel, component

        dset_re = r"(\w+:?:?\w*\[?\d*\]?) it=(\d+) tl=(\d+)$"
        name_re = re.match(dset_re, string)
        if name_re is not None:
            variable  = name_re.group(1)
            iteration = int(name_re.group(2))
            timelevel = int(name_re.group(3))
            reflevel  = None
            component = None
            return variable, iteration, timelevel, reflevel, component

        return None

    def make_dset_name(self, variable, iteration, timelevel,\
            reflevel = None, component = None):
        """
        Generates a dataset name
        """
        s = str(variable) + " it=" + str(iteration) + " tl=" + str(timelevel)
        if reflevel is not None:
            s += " rl=" + str(reflevel)
        if component is not None:
            s += " c=" + str(component)
        return s

    def select(self, variable = None, iteration = None, timelevel = None,\
            reflevel = None, component = None):
        """
        Returns an iterator to all the matching keys
        """
        if None not in (variable, iteration, timelevel, reflevel, component):
            key = self.make_dset_name(variable, iteration, timelevel,
                    reflevel, component)
            if key in self.contents:
                return iter([(variable, iteration, timelevel,
                    reflevel, component)])
            else:
                return iter([])
        elif iteration is not None:
            return (t for t in self.itdata[iteration] if
                    (variable  is None or t[0] == variable)  and
                    (timelevel is None or t[2] == timelevel) and
                    (reflevel  is None or t[3] == reflevel)  and
                    (component is None or t[4] == component))
        else:
            return (t for t in self.metadata if
                    (variable  is None or t[0] == variable)  and
                    (iteration is None or t[1] == iteration) and
                    (timelevel is None or t[2] == timelevel) and
                    (reflevel  is None or t[3] == reflevel)  and
                    (component is None or t[4] == component))

    def __select_idx__(self, idx, variable = None, iteration = None,
            timelevel = None, reflevel = None, component = None):
        if None not in (variable, iteration, timelevel, reflevel, component):
            key = self.make_dset_name(variable, iteration, timelevel,
                    reflevel, component)
            if key in self.contents:
                return iter([(variable, iteration, timelevel,
                    reflevel, component)[idx]])
            else:
                return iter([])
        elif iteration is not None:
            return (t[idx] for t in self.itdata[iteration] if
                    (variable  is None or t[0] == variable)  and
                    (timelevel is None or t[2] == timelevel) and
                    (reflevel  is None or t[3] == reflevel)  and
                    (component is None or t[4] == component))
        else:
            return (t[idx] for t in self.metadata if
                    (variable  is None or t[0] == variable)  and
                    (iteration is None or t[1] == iteration) and
                    (timelevel is None or t[2] == timelevel) and
                    (reflevel  is None or t[3] == reflevel)  and
                    (component is None or t[4] == component))

    def select_variables(self, variable = None, iteration = None,
            timelevel = None, reflevel = None, component = None):
        """
        Returns an iterator to all the matching keys
        """
        return self.__select_idx__(0, variable, iteration, timelevel,
                reflevel, component)

    def select_iterations(self, variable = None, iteration = None,
            timelevel = None, reflevel = None, component = None):
        """
        Returns an iterator to all the matching keys
        """
        return self.__select_idx__(1, variable, iteration, timelevel,
                reflevel, component)

    def select_reflevels(self, variable = None, iteration = None,
            timelevel = None, reflevel = None, component = None):
        """
        Returns an iterator to all the matching keys
        """
        return self.__select_idx__(3, variable, iteration, timelevel,
                reflevel, component)

    def select_components(self, variable = None, iteration = None,
            timelevel = None, reflevel = None, component = None):
        """
        Returns an iterator to all the matching keys
        """
        return self.__select_idx__(4, variable, iteration, timelevel,
                reflevel, component)

    def choose_var_it_tl(self, variable = None, iteration = None,
            timelevel = None):
        """
        Selects variable, iteration and timelevel
        """
        # We assume all variables, timelevel, iterations to be always
        # (or never) available
        if None in (variable, iteration, timelevel):
            var, it, tl, rl, c = next(self.select(None, iteration, None,
                    None, None))
            if variable is None:
                variable = var
            if iteration is None:
                iteration = it
            if timelevel is None:
                timelevel = tl
        return variable, iteration, timelevel

    def exists(self, variable = None, iteration = None, timelevel = None,\
            reflevel = None, component = None):
        """
        Returns True if the given dataset is available, otherwise False
        """
        selection = self.select(variable, iteration, timelevel,
                reflevel, component)
        try:
            x = next(selection)
            return True
        except StopIteration:
            return False

    def get_file_obj(self, key, get_index_file = False):
        """
        Returns an h5py.dataset containing the wanted data

        * key       : dataset name
        * use_index : use index files if available (only metadata)

        NOTE: This is a low level routine. The final user should use
        "get_dataset" or "get_component" instead
        """
        fname = self.contents[key]
        if self.haveidx and get_index_file:
            fname = fname[:-3] + ".idx.h5"
        if fname in self.ofobjs:
            return self.ofobjs[fname]
        else:
            if len(self.ofobjs) < self.maxnfiles:
                self.ofobjs[fname] = h5py.File(fname, 'r')
                self.oflist.append(fname)
            else:
                old_fname = self.oflist.pop(0)
                self.ofobjs[old_fname].close()
                del self.ofobjs[old_fname]

                self.ofobjs[fname] = h5py.File(fname, 'r')
                self.oflist.append(fname)
            return self.ofobjs[fname]

    def get_metadata_dataset(self):
        """
        Returns an h5py.dataset containing the Carpet metadata group
        """
        if not self.oflist:
            # Get any file name
            fname = next(iter(list(self.contents.values())))
            # Open file
            self.ofobjs[fname] = h5py.File(fname, 'r')
            self.oflist.append(fname)
        # Get any open file
        fobj = next(iter(list(self.ofobjs.values())))
        return fobj['Parameters and Global Attributes']

    def get_dataset(self, variable = None, iteration = None, timelevel = None,\
            reflevel = None, component = None, only_metadata = False):
        """
        Returns an h5py.dataset containing the wanted data

        If some of the parameters are not specified this returns the first
        available dataset
        """
        try:
            var, it, tl, rl, c = next(self.select(variable, iteration, timelevel,\
                    reflevel, component))
        except StopIteration:
            raise KeyError(self.make_dset_name(variable, iteration, timelevel,
                reflevel, component) + ' not found!')
        key = self.make_dset_name(var, it, tl, rl, c)

        return self.get_file_obj(key, only_metadata)[key]

    def get_time(self, iteration):
        """
        Get the simulation time at a given iteration
        """
        return float(self.get_dataset(iteration=iteration).attrs['time'])

    def get_component(self, variable = None, iteration = None, timelevel = None,
            reflevel = None, component = None):
        """
        Returns a scidata.carpet.grid.basegrid object containing the metadata
        of the wanted component
        """
        if reflevel is None:
            reflevel = next(self.select_reflevels(variable, iteration, timelevel,
                    reflevel, component))
        dset = self.get_dataset(variable, iteration, timelevel,
                reflevel, component, True)

        comp = scidata.carpet.grid.basegrid()

        comp.iorigin = dset.attrs['iorigin']
        comp.dim = len(comp.iorigin)
        comp.directions = list(range(comp.dim))
        comp.id = (reflevel, component)

        comp.n = list(dset.shape)
        comp.n.reverse()
        comp.n = numpy.array(comp.n)

        try:
            comp.delta = dset.attrs['delta']
            comp.origin = dset.attrs['origin']
        except KeyError:
            comp.delta = numpy.ones(comp.dim)
            comp.origin = comp.iorigin
            comp.id = (None, component)

        comp.time = float(dset.attrs['time'])
        comp.timestep = int(dset.attrs['timestep'])

        return comp

    def get_reflevel(self, variable = None, iteration = None,
            timelevel = None, reflevel = None):
        """
        Returns a scidata.carpet.grid.level object containing the metadata
        of the wanted refinement level
        """
        if reflevel is None:
            reflevel = next(self.select_reflevels(variable, iteration,
                    None, None, None))
        components = set(self.select_components(variable, iteration,
            timelevel, reflevel, None))

        L = []
        for c in components:
            L.append(self.get_component(variable, iteration, timelevel,
                reflevel, c))

        if len(L) == 0:
            return None
        return scidata.carpet.grid.level(L, reflevel)

    def get_grid(self, variable = None, iteration = None, timelevel = None):
        """
        Returns a scidata.carpet.grid.grid object containing the metadata
        of the grid at the wanted iteration
        """
        reflevels = set(self.select_reflevels(variable, iteration,
            timelevel, None, None))

        L = []
        for rl in reflevels:
            L.append(self.get_reflevel(variable, iteration, timelevel, rl))

        return scidata.carpet.grid.grid(L)

    def get_component_data(self, variable = None, iteration = None,
            timelevel = None, reflevel = None, component = None):
        """
        Returns a numpy.array containing the data of the wanted component
        """
        dset = self.get_dataset(variable, iteration, timelevel,
                reflevel, component, False)

        return numpy.array(dset).transpose()

    def get_reflevel_data(self, reflevel, variable = None, iteration = None,
            timelevel = None, dtype=None):
        """
        Returns a numpy.array containing the data of the wanted reflevel

        * dtype : convert data to a given datatype
                  (if None no conversion is performed)
        """
        variable, iteration, timelevel = self.choose_var_it_tl(variable,
                iteration, timelevel)

        if dtype is None:
            dtype = self.dtype
        data    = numpy.empty(reflevel.n, dtype=dtype)
        data[:] = numpy.NAN

        for component in reflevel.components:
            component.restrict(data)[:] = self.get_component_data(variable,
                    iteration, timelevel, component.id[0], component.id[1])

        return numpy.ma.masked_invalid(data)

    def get_grid_data(self, grid, variable = None, iteration = None,\
            timelevel = None, dtype=None):
        """
        Returns a list of numpy.array containing the data on the reflevels of
        the given grid

        * dtype : convert data to a given datatype
                  (if None no conversion is performed)
        """
        variable, iteration, timelevel = self.choose_var_it_tl(variable,
                iteration, timelevel)

        data = []
        for level in grid.levels:
            data.append(self.get_reflevel_data(level, variable, iteration,\
                    timelevel, dtype))
        return data

def parse_1D_file(filename, reflevel=None, dtype=None):
    """
    Parse a 1D CarpetHDF5 file and retun a scidata.monodataset.dataset
    """
    fre = re.match(r"(.+)\.([xyzd])\.(\w+)", filename)
    ext  = fre.group(3)
    if ext != "h5":
        raise scidata.utils.FileTypeError(filename)

    dset = scidata.monodataset.dataset()
    framelist = []

    dfile = dataset(filename)
    for it in dfile.iterations:
        if reflevel is None:
            frame = []
            grid  = dfile.get_grid(iteration=it)
            data  = dfile.get_grid_data(grid, iteration=it, dtype=dtype)
            for i in range(len(grid.levels)):
                rlevel = grid.levels[i]
                frame.append(rlevel.mkframe(data[i]))

            frm = frame[0]
            for f in frame[1:]:
                frm.merge(f)

            framelist.append(frm)
        else:
            if dfile.exists(iteration=it, reflevel=reflevel):
                grid = dfile.get_reflevel(reflevel=reflevel, iteration=it)
                data = dfile.get_reflevel_data(grid, iteration=it, dtype=dtype)
                framelist.append(grid.mkframe(data))

    dset.import_framelist(framelist)

    return dset
