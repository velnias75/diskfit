# DiskFit
A simple disk fit calculator

----
This crude tool calculates the optimal file selection to a given target size.

It has been originally developed to optimize the usage of the capacity of a DVD after transcoding to MP4 movie files.

It offers two presets for a single layer `DVD` (4.38 GByte) and a `CD` (700 Mbyte) as well as the ability 
to give any target size in either `Bytes`, `KBytes`, `MBytes` and `GBytes`. Additionally a config file is read.
to offer even more targets

It outputs in ascending order all combinations of files which will fit within the target size.

## Usage
``diskfit (cd|dvd|target_size[G|M|K]) file_pattern...``

Set environment variable `DISKFIT_STRIPDIR` to any value to strip directories.
