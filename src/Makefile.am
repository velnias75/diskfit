SUBDIRS = lib python

bin_PROGRAMS = diskfit

diskfit_CFLAGS = $(GLIB2_CFLAGS) $(LIBXML_CFLAGS) -fstrict-aliasing -finline-functions
diskfit_CPPFLAGS = -I$(srcdir)/lib -DSYSCONFDIR=\"$(sysconfdir)/\"
diskfit_SOURCES = diskfit.c
diskfit_LDADD = lib/libdiskfit.la $(GLIB2_LIBS) $(LIBXML_LIBS)

dist_man_MANS = diskfit.1
