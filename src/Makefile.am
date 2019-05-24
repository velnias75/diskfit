SUBDIRS = lib

if INSTALL_GUI
SUBDIRS += python
endif

bin_PROGRAMS = diskfit

diskfit_CFLAGS = $(GLIB2_CFLAGS) -fstrict-aliasing -finline-functions
diskfit_CPPFLAGS = -I$(srcdir)/lib -DSYSCONFDIR=\"$(sysconfdir)/\"
diskfit_SOURCES = diskfit.c
diskfit_LDADD = lib/libdiskfit.la $(GLIB2_LIBS)
