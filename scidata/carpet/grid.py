import copy
import numpy

import scidata.monodataset
import scidata.utils

class basegrid(object):
    """
    A uniform grid (a Carpet component or a level)

    * delta       : grid-spacing in every direction
    * dim         : dimensions
    * directions  : list of directions in which the grid is extended
    * id          : component identification tuple (level, component)
    * iorigin     : index origin of the basegrid
    * n           : number of grid point in every direction
    * origin      : coordinates of the origin of the basegrid
    * time        : absolute time
    * timestep    : current timestep
    """

    def __init__(self):
        self.delta       = numpy.array([])
        self.dim         = 0
        self.directions  = []
        self.id          = (0, 0)
        self.iorigin     = numpy.array([])
        self.n           = numpy.array([])
        self.origin      = numpy.array([])
        self.time        = 0
        self.timestep    = 0

    def __cmp__(self, other):
        """
        Comparison operator
        """
        for d in range(self.dim):
            if self.iorigin[d] < other.iorigin[d]:
                return -1
            if self.iorigin[d] > other.iorigin[d]:
                return 1
        return 0

    def __congruent__(self, other):
        """
        Returns true if the other basegrid is congruent to the present one
        """
        outcome = []
        outcome.append(scidata.utils.makelist(self.delta == other.delta))
        outcome.append(scidata.utils.makelist(self.dim == other.dim))
        outcome.append(scidata.utils.makelist(\
                self.directions == other.directions))
        outcome.append(scidata.utils.makelist(self.iorigin == other.iorigin))
        outcome.append(scidata.utils.makelist(self.n == other.n))
        return numpy.array(outcome).all()

    def __hash__(self):
        s = ""
        for d in range(self.dim):
            s += str(self.iorigin[d]).zfill(10)
        return hash(s)

    def __lt__(self, other):
        return self.__cmp__(other) < 0
    def __gt__(self, other):
        return self.__cmp__(other) > 0
    def __eq__(self, other):
        return self.__cmp__(other) == 0
    def __le__(self, other):
        return self.__cmp__(other) <= 0
    def __ge__(self, other):
        return self.__cmp__(other) >= 0
    def __ne__(self, other):
        return self.__cmp__(other) != 0

    def __iter__(self):
        return iterator(self)

    def __str__(self):
        s = "<level:" + str(self.id[0]) + " component:" + str(self.id[1])
        s += "\n"
        for d in range(self.dim):
            s += "\t"
            s += str(self.origin[d]) + " <= x[" + str(d) + "] <= " +\
                    str(self.upperbound()[d]) + "\t\t"
            s += str(self.iorigin[d]) + " <= idx[" + str(d) + "] < " +\
                    str(self.upperindex()[d]) + "\n"
        s += ">"
        return s

    def coordinate(self, index):
        """
        Coordinates of the given index array
        """
        return self.origin + (index - self.iorigin) * self.delta

    def contains(self, index):
        """
        Returns True if the given point is inside the grid
        """
        return all(index >= self.iorigin) and all(index < self.upperindex())

    def contains_point(self, point):
        """
        Returns True if the given point is inside the grid
        """
        return all(point >= self.origin) and \
                all(point <= self.upperbound() + 0.1*self.delta)

    def dual(self, dtype=numpy.float64):
        """
        Returns the dual grid
        """
        sl = []
        for d in self.directions:
            sl.append(slice(0, self.n[d]+1))

        L = numpy.array(numpy.mgrid[sl], dtype=dtype)
        for d in self.directions:
            L[d] = self.origin[d] + self.delta[d]*(L[d] - self.iorigin[d] - 0.5)

        return tuple(L)

    def extent(self):
        """
        Returns a tuple with the extension of the grid in all directions
            (x_min, x_max, ... , y_min, y_max)
        """
        dw = self.origin
        up = self.upperbound()

        L = []
        for d in range(self.dim):
            L += [dw[d], up[d]]

        return tuple(L)

    def format(self, data):
        """
        Writes the data in a string understandable by gnuplot

        This method is only valid for 1D and 2D basegrids
        """
        assert self.dim == 1 or self.dim == 2

        s = ""
        z = self.restrict(data)

        if(self.dim == 1):
            for i in range(self.n[0]):
                s += str(self.coordinate(numpy.array([i]))) + " " +\
                    z[i] + "\n"
        else:
            for i in range(self.n[0]):
                for j in range(self.n[1]):
                    x, y = self.coordinate(numpy.array([i, j]))
                    s += str(x) + " " + str(y) + " " + str(z[i, j]) + "\n"
                s += "\n"
        return s

    def gridpoints(self, dir):
        """
        Coordinates of the grid points in the "dir" direction
        """
        return self.origin[dir] + self.delta[dir] * numpy.arange(self.n[dir])

    def index(self, point):
        """
        Index of a given point
        """
        a = numpy.array((point - self.origin) / self.delta, dtype=numpy.int64)
        return a + self.iorigin

    def local_index(self, index):
        """
        Gets the local enumeration of an index given in the global enumeration
        """
        edim = len(self.directions)
        locidx = numpy.empty(edim, dtype=numpy.int64)
        for i in range(edim):
            d = self.directions[i]
            locidx[i] = index[d] - self.iorigin[d]
        return locidx

    def map_coordinates(self, other, data):
        """
        Interpolates the data from another grid defined on the same physical
        domain

        * other : must be a basegrid object having same lower-upper bounds
        * data  : must be the data on the other grid
        """
        import scipy.ndimage
        msh = numpy.array(self.mesh())
        for d in range(self.dim):
            msh[d] = (msh[d] - other.origin[d]) / other.delta[d]
        return scipy.ndimage.map_coordinates(data, msh)

    def coordinates(self, dtype=numpy.float64):
        """
        Returns the mesh grid points.

        This returns a tuple of numpy.arrays containing the grid coordinates
        in each direction
        """
        L = [self.origin[d] + self.delta[d]*numpy.arange(self.n[d], dtype=dtype)
                for d in self.directions]
        return tuple(L)

    def mesh(self, dtype=numpy.float64):
        """
        Returns a full mesh.

        This returns a tuple of numpy.arrays containing the value of the
        coordinates in the various points of the grid
        """
        sl = []
        for d in self.directions:
            sl.append(slice(0, self.n[d]))

        L = numpy.array(numpy.mgrid[sl], dtype=dtype)
        for d in self.directions:
            L[d] = self.origin[d] + self.delta[d]*L[d]

        return tuple(L)

    def mkframe(self, data):
        """
        Create a scidata.monodataset.frame from the given data

        This method is only valid for 1D basegrids

        * data : numpy array of the data the we want to store
        """
        assert self.dim == 1

        frame = scidata.monodataset.frame()
        frame.index = self.timestep
        frame.time = self.time
        frame.data_x, = self.mesh()
        frame.data_y = self.restrict(data)

        return frame

    def restrict(self, data):
        """
        Restricts the given global data array to the local grid

        This will return a slice of the original data
        """
        return data[self.slice()]

    def scale(self, factor):
        """
        Scales the grid by a constant factor

        This is mostly useful to make a change in the system of units
        """
        self.delta  = self.delta*factor
        self.origin = self.origin*factor

    def slice(self):
        """
        Returns the index slices associated with the basegrid
        """
        sl = []
        ub = self.upperindex()
        for d in range(self.dim):
            sl.append(slice(self.iorigin[d], ub[d]))
        return tuple(sl)

    def search(self, index):
        """
        Search for an index array in the basegrid

        Returns
        * -1 : the basegrid has larger indices then the index
        * 0  : the basegrid contains the index
        * 1  : the basegrid has smaller indices than the index
        """
        upperindex = self.upperindex()
        for d in range(self.dim):
            if self.iorigin[d] > index[d]:
                return -1
            if upperindex[d] < index[d]:
                return 1
        return 0

    def upperbound(self):
        """
        Upper bound coordinate position of the basegrid as an array
        """
        return self.origin + (self.n - 1)*self.delta

    def upperindex(self):
        """
        Upper bound index of the basegrid as an array
        """
        return self.iorigin + self.n

    def write(self, data, filename):
        file = open(filename, "w")
        file.write(self.format(data))
        file.close()

class sublevel:
    """
    A rectangular patch of a refinement level

    * grid   : a basegrid object containing the present subgrid
    * n      : list of slices specifying the subgrid
    * shape  : shape of the grid
    """
    def __init__(self, grid, slices):
        """
        * grid   : a basegrid object containing the present subgrid
        * slices : list of slices specifying the subgrid
        """
        assert(grid.dim == len(slices))
        for i, sl in enumerate(slices):
            assert(sl.start >= grid.iorigin[i])
            assert(sl.stop  <= grid.upperindex()[i])
        self.grid   = grid
        self.slices = slices
        self.n      = tuple([sl.stop - sl.start for sl in self.slices])
    def interesection(self, component):
        """
        Computes the intersection of the sublevel with a given component

        Returns a tuple sls, slc with the slices to be used to access the data
        in the intersection region for arrays defined in the sublevel index
        space (sls) and in the component index space (slc).  sls and slc are
        set to None if the intersection region is empty.

        WARNING: component must be a component of self.grid!
        """
        component_upperindex = component.upperindex()
        sls  = []
        slc  = []
        for d in range(component.dim):
            start = max(self.slices[d].start, component.iorigin[d])
            stop  = min(self.slices[d].stop, component_upperindex[d])
            if end > start:
                sls.append(slice(start - self.slices[d].start,
                    stop - self.slices[d].start))
                slc.append(slice(start - component.iorigin[d],
                    stop - component.iorigin[d]))
            else:
                return None, None
        return tuple(sls), tuple(slc)

class iterator:
    """
    Grid iterator (iterate over the points of a grid)

    * grid  : grid object on which we iterate (component or level)
    * index : current location
    """

    def __init__(self, grid):
        self.grid = grid
        self.index = numpy.copy(self.grid.iorigin)
        self.index[self.grid.directions[0]] -= 1

    def __iter__(self):
        return self

    def __next__(self):
        for i in range(len(self.grid.directions)):
            d1 = self.grid.directions[i]
            if self.index[d1] < self.grid.iorigin[d1] + self.grid.n[d1] - 1:
                for j in range(i):
                    d2 = self.grid.directions[j]
                    self.index[d2] = self.grid.iorigin[d2]
                self.index[d1] += 1
                return numpy.copy(self.index)
        raise StopIteration

class level(basegrid):
    """
    One refinement level of the Carpet grid

    * components  : list of components
    * id          : refinement level identification number
    * nghostzones : number of ghost zones

    NOTES: currently this class merges together all the connected
    (in the topological sense) components of the refinement level
    and creates a unique large box (the convex hull of the grid).
    """

    def __init__(self, components, id, nghostzones = 3):
        """
        Initialize a level from a list of components

        * components  : list of components
        * id          : level id
        * nghostzones : only used if the grid has only one component as
                        in this case we cannot infer the number of ghost
                        points from the grid structure
        """
        super(level, self).__init__()

        self.components  = []
        self.id          = id
        self.nghostzones = nghostzones

        self.components = copy.deepcopy(components)
        self.components = sorted(list(set(self.components)))

        self.delta = self.components[0].delta.copy()
        self.dim = copy.deepcopy(self.components[0].dim)
        self.directions = copy.deepcopy(self.components[0].directions)
        self.iorigin = self.components[0].iorigin.copy()
        self.n = numpy.empty(self.dim, dtype=numpy.int64)
        self.origin = self.components[0].origin.copy()
        self.time = self.components[0].time
        self.timestep = self.components[0].timestep

        # Note that the origin of the convex hull might be different from
        # the location of the first point of the grid in the lexicographical
        # ordering
        for d in range(self.dim):
            self.iorigin[d] = min([c.iorigin[d] for c in self.components])
            self.origin[d]  = min([c.origin[d]  for c in self.components])

        # This is a workaround to correct for the fact that the origin
        # of a refinement level is set with respect to the coordinates of
        # the parent refinement level
        for c in self.components:
            for d in range(self.dim):
                c.iorigin[d] = c.iorigin[d] - self.iorigin[d]

        for d in range(self.dim):
            self.iorigin[d] = 0

        # If we have only one component we have to guess for the number of
        # ghost regions
        if len(self.components) > 1:
            L = []
            for d in range(self.dim):
                L.append(self.components[0].n[d] - \
                        self.components[1].iorigin[d] +\
                        self.components[0].iorigin[d])
            self.nghostzones = min(L)
            self.nghostzones = self.nghostzones // 2

        self.nghostzones = self.nghostzones * numpy.ones(self.dim,\
                dtype=numpy.int64)

        for d in range(self.dim):
            self.n[d] = max([c.upperindex()[d] for c in self.components])

    def __str__(self):
        s = "<level:" + str(self.id)
        s += "\n"
        for c in self.components:
            s += scidata.utils.indent(str(c)) + "\n"
        s += ">"
        return s

    def clist(self, indexlist):
        """
        Part of the grid level containing the indices from the indexlist

        This returns an ordered list of components covering all the indices
        in the list.

        This is not particularly efficient.

        NOTE: indexlist can also be a basegrid object.
        """
        L = []
        for c in self.components:
            for i in indexlist:
                if c.contains(i):
                    L.append(c)
                    break
        return L

    def get_component(self, idx):
        """
        Gets the given component
        """
        for c in self.components:
            if c.id[1] == idx:
                return c
        return None

    def locate(self, index):
        """
        Returns a component containing a given index

        This does not check for buffer/ghost regions: the first component found
        is returned

        None is returned if the index is out-of-range
        """
        low = 0
        hi  = len(self.components)
        mid = (hi + low) // 2

        while mid != low:
            s = self.components[mid].search(index)
            if s == 0:
                return self.components[mid]
            elif s == 1:
                low = mid
                mid = (hi + low) // 2
            elif s == -1:
                hi = mid+1
                mid = (hi + low) // 2

        return None

    def scale(self, factor):
        """
        Scales the grid by a constant factor

        This is mostly useful to make a change in the system of units
        """
        super(level, self).scale(factor)
        for c in self.components:
            c.scale(factor)

class grid:
    """
    Grid structure from Carpet

    * dim        : number of dimensions
    * levels     : list of refinement levels
    * origin     : origin of the grid (coordinate position)
    * time       : current time
    * timestep   : current timestep
    * upperbound : upper bound of the grid coordinates
    """

    def __init__(self, levels):
        self.dim = levels[0].dim
        self.levels = levels
        self.origin = numpy.empty(self.dim)
        self.time = levels[0].time
        self.timestep = levels[0].timestep
        self.upperbound = numpy.empty(self.dim)
        for d in range(self.dim):
            self.origin[d] = min([l.origin[d] for l in self.levels])
            self.upperbound[d] = max([l.upperbound()[d] for l in self.levels])

    def __getitem__(self, i):
        return self.levels[i]

    def __iter__(self):
        return self.levels.__iter__()

    def __len__(self):
        return self.levels.__len__()

    def __str__(self):
        s = "<grid\n"
        for l in self.levels:
            s += scidata.utils.indent(str(l)) + "\n\n"
        s += ">"
        return s

    def coordinates(self):
        """
        Return a list of tuples each containing the coordinates generating
        a refinement level grid
        """
        out = []
        for l in self.levels:
            out.append(l.coordinates())
        return out

    def mesh(self):
        """
        Creates a full mesh

        This returns a list of numpy arrays containing all the points of the
        various levels
        """
        out = []
        for l in self.levels:
            out.append(l.mesh())
        return out

    def restrict(self, griddata):
        """
        Restricts the given griddata on the current slice
        """
        out = []
        for idx in range(len(self.levels)):
            out.append(self.levels[idx].restrict(griddata[idx]))
        return out

    def scale(self, factor):
        """
        Scales the grid by a constant factor

        This is mostly useful to make a change in the system of units
        """
        self.origin = self.origin*factor
        self.upperbound = self.upperbound*factor
        for l in self.levels:
            l.scale(factor)
