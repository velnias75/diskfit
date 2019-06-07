# QDiskFit
A simple disk fit calculator (GUI)

----
This crude tool calculates the optimal file selection to a given target size.

It has been originally developed to optimize the usage of the capacity of a DVD after transcoding to MP4 movie files.

It offers two presets for a single layer `DVD` (4.38 GByte) and a `CD` (700 Mbyte) as well as the ability 
to give any target size in either `Bytes`, `KBytes`, `MBytes` and `GBytes`. Additionally a config file is read.
to offer even more targets

It outputs in ascending order all combinations of files which will fit within the target size.

## Exclusive calculation

_QDiskFit_ offers an exclusive calculation: the selected input files are subtracted from the current target size 
and the resulting size is set as *custom target size*. Further the selected items are removed from the input files.

This option is only available if the resulting *custom target size* is larger or equal to 1 byte.

This is useful - for example - if you want to have the selection in any case on the target medium and to fill up the 
remaining space.
