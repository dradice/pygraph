#include <assert.h>
#include <stdio.h>
#include <unistd.h>

#include "pygraph.h"

int pygwrite(
        char const * fname,
        char mode,
        int const ts,
        float const ctime,
        int const np,
        float const * data) {
    int ierr = 0;
    assert(mode == 'w' || mode == 'a');
    hid_t file_id;
    if(access(fname, F_OK) == 0 && mode == 'a') {
        file_id = H5Fopen(fname, H5F_ACC_RDWR, H5P_DEFAULT);
    }
    else {
        file_id = H5Fcreate(fname, H5F_ACC_TRUNC, H5P_DEFAULT, H5P_DEFAULT);
    }
    ierr |= file_id < 0;
    hid_t group_id = H5Gopen(file_id, "/", H5P_DEFAULT);
    ierr |= group_id < 0;

    char dname[BUFSIZ];
    snprintf(dname, BUFSIZ, "%d", ts);

    hsize_t dim = 3*np;
    hid_t dspace_id = H5Screate_simple(1, &dim, NULL);
    ierr |= dspace_id < 0;
    hid_t dset_id = H5Dcreate2(group_id, dname, H5T_NATIVE_FLOAT,
            dspace_id, H5P_DEFAULT, H5P_DEFAULT, H5P_DEFAULT);
    ierr |= dset_id < 0;
    H5Dwrite(dset_id, H5T_NATIVE_FLOAT, H5S_ALL, H5S_ALL, H5P_DEFAULT, data);

    dim = 1;
    hid_t dspace2_id = H5Screate_simple(1, &dim, NULL);
    ierr |= dspace2_id < 0;
    hid_t attr_id = H5Acreate2(dset_id, "time", H5T_NATIVE_FLOAT,
            dspace2_id, H5P_DEFAULT, H5P_DEFAULT);
    ierr |= attr_id < 0;
    H5Awrite(attr_id, H5T_NATIVE_FLOAT, &ctime);
    H5Aclose(attr_id);
    H5Sclose(dspace2_id);

    H5Dclose(dset_id);
    H5Sclose(dspace_id);

    H5Gclose(group_id);
    H5Fclose(file_id);

    return ierr;
}

