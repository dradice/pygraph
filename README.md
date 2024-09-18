# PythonYGraph

A freely available, lightweight and easy to use visualization client for
viewing 1D data files.

PythonYGraph is a PyQt re-implementation of xGraph and yGraph:


## Requirements

* h5py
* NumPy
* Python3
* PyQt5
* PythonQwt


## Mouse shortcuts

* Left click + drag: zoom-in
* Right click: previous zoom settings
* Shift + Right click: next zoom settings
* Middle click: original zoom settings


## Data transformations

Data transformations strings are evaluated as lambda functions with
numpy expressions.

Example: shifting the data and removing a secular trend

```text
  x' = x + 0.5
  y' = y + 0.1*sin(x + 2*pi*t)*x
```

Example: computing the derivative of the data

```text
  x' = x
  y' = D(y)/D(x)
```

## Command Line Interface

PythonYGraph can be invoked from the command-line as

```sh
pygraph
```

It is possible to specify a list of files to open with

```sh
pygraph file1 file2 ...
```

One can specify which data column to read from an ASCII file with the syntax

```sh
pygraph file.xg ^5
```

If the column is not specified PythonYGraph will use a reasonable default. Note
that the column number for the coordinates is currently hard coded for each
data file format.

In the case a dataset is split over different files it is possible to make
PythonYGraph automatically merge them, by simply enclosing the relevant list of
files within curly brackets as:

```sh
pygraph { rho.1.xg rho.2.xg rho.3.h5 } { */data/vel[0].x.asc }
```

Please notice the space between the brackets and the file list.

In case you wish to combine two datasets, using the y-data of the second one
as the x-data of the first one, you can use

```sh
pygraph file1 @ file2
```

this will plot file1 using file2 y-data as its x-data.

You can also use `{}`, `^` and `@` together, as in

```sh
pygraph { file1 ^2 file2 ^3 } @ { file3 file4 ^4 }
```

Note that in the second group the 4th column is used for both files.

For more information see

```sh
pygraph --help
```

## PythonYGraph data format (.pyg)

PythonYGraph also has its own HDF5-based data format. You should consider using
this format over the old xgraph ASCII format when creating large data files as
reading PYG data does not require any (slow) string parsing.

The .PYG data format is undocumented, but a reference C implementation of a
.PYG writer is provided in the "lib" directory.


## Acknowledgements

Parts of this code has been adapted from the GPLed examples distributed
alongside the book "Summerfield - Rapid GUI Programming with Python and Qt".

The icons are from the Tango project.


## References

http://www.cactuscode.org/documentation/visualization/xGraph/
http://www.cactuscode.org/documentation/visualization/yGraph/
http://tango.freedesktop.org
