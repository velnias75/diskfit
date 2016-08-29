SUBDIRS = src

ACLOCAL_AMFLAGS = -Im4

AM_DISTCHECK_CONFIGURE_FLAGS = --with-bash-completion-dir=no

completionsdir = $(bashcompdir)

doc_DATA = README.md
completions_DATA = diskfit
sysconf_DATA = diskfitrc

EXTRA_DIST = $(doc_DATA) $(sysconf_DATA) diskfit.bc.in

DISTCLEANFILES = $(completions_DATA)

diskfit: $(top_srcdir)/diskfit.bc.in
	$(AM_V_GEN)$(SED) -e 's|@bindir[@]|$(bindir)|g' < $< > $@
