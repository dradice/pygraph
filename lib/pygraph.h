#ifndef PYGRAPH_H
#define PYGRAPH_H

/*
 * pygraph native binary data format: reference implementation
 */
/* write 1D data in binary pygraph format and returns 0 on success */
int pygwrite(
        char const * fname,     /* [in] file name */
        char mode,              /* [in] w:write a:append */
        int const ts,           /* [in] current timestep */
        float const ctime,      /* [in] current time */
        int const np,           /* [in] number of tuples */
        float const * data);    /* [in] x and y coordinates, interlaced */

#endif
