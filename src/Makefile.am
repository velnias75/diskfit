SUBDIRS = lib

bin_PROGRAMS = diskfit

diskfit_CFLAGS = $(GLIB2_CFLAGS)
diskfit_CPPFLAGS = -Ilib
diskfit_SOURCES = diskfit.c
diskfit_LDADD = lib/libdiskfit.la $(GLIB2_LIBS)
