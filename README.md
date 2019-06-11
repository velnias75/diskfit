# DiskFit
A simple disk fit calculator

----
Given a set of input files all unique combinations of files are calculated
which are less or equal in total size to a given target size. The list will
get outputted in ascending order showing the combination closest to the
target size at the end of the output.

It has been originally developed to optimize the usage of the capacity of a DVD after transcoding to MP4 movie files.

It offers two builtin presets for a single layer `DVD` (4.38 GByte) and a `CD` (700 Mbyte) as well as the ability 
to give any target size in either `Bytes`, `KBytes`, `MBytes` and `GBytes`. Additionally a config file is read.
to offer even more targets

## Usage
``diskfit (cd|dvd|target_size[G|M|K]) file_pattern...``

Set environment variable `DISKFIT_STRIPDIR` to any value to strip directories.
