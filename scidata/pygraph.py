import h5py
import numpy
import scidata.monodataset
import scidata.utils

def validate(filename):
    """
    Check if the given file is in binary pygraph format
    """
    dfile = h5py.File(filename, "r")
    try:
        ver = dfile['/'].attrs['pyg_version']
        return ver == 1
    except:
        return False

def parsefile(filename, dtype=None):
    """
    Import data in native binary pygraph format
    """
    try:
        dfile = h5py.File(filename, 'r')
    except IOError:
        raise scidata.utils.FileTypeError(filename)

    if not scidata.utils.extension(filename) == "pyg":
        try:
            v = int(dfile['/'].attrs['pyg_version'])
            if(v != 1):
                raise scidata.utils.FileTypeError(filename)
        except:
            raise scidata.utils.FileTypeError(filename)

    dset_names = []
    dfile.visit(dset_names.append)

    itlist = sorted([int(p) for p in dset_names])

    frames = []
    for it in itlist:
        dset = dfile[str(it)]

        rawdata = numpy.array(dset, dtype=dtype)
        rawdata = rawdata.reshape((rawdata.shape[0]//2, 2))

        frames.append(scidata.monodataset.frame())
        frames[-1].time = float(dset.attrs['time'])
        frames[-1].data_x = rawdata[:, 0]
        frames[-1].data_y = rawdata[:, 1]

    out = scidata.monodataset.dataset()
    out.import_framelist(frames)
    return out
