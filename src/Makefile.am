SUBDIRS = lib

bin_PROGRAMS = diskfit
bin_SCRIPTS = mdiskfit

EXTRA_DIST = mdiskfit.in
DISTCLEANFILES = mdiskfit

diskfit_CFLAGS = $(GLIB2_CFLAGS) -fstrict-aliasing -finline-functions
diskfit_CPPFLAGS = -I$(srcdir)/lib -DSYSCONFDIR=\"$(sysconfdir)/\"
diskfit_SOURCES = diskfit.c
diskfit_LDADD = lib/libdiskfit.la $(GLIB2_LIBS)

mdiskfit: mdiskfit.in
	$(AM_V_GEN)$(SED) -e 's|@bindir[@]|$(DESTDIR)$(bindir)|g' < $< > $@