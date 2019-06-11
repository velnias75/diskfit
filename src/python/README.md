# QDiskFit
A simple disk fit calculator (GUI)

----
This GUI provides an easy way to set up a set of input files for DiskFit and
to perform a calculation of all unique combinations which are less or equal
in total size to a given target size. The list will get outputted in
ascending order showing the combination closest to the target size at the
end of the output.

The output than can get saved or dragged into another program (i.e. a CD/DVD
burning application). Further it contains tools for an easy setup of targets
as well as some predefined workflows for the most common input file selection
tasks.

It has been originally developed to optimize the usage of the capacity of a DVD after transcoding to MP4 movie files.

## Exclusive calculation

_QDiskFit_ offers an exclusive calculation: the selected input files are subtracted from the current target size 
and the resulting size is set as *custom target size*. Further the selected items are removed from the input files.

This option is only available if the resulting *custom target size* is larger or equal to 1 byte.

This is useful - for example - if you want to have the selection in any case on the target medium and to fill up the 
remaining space.
