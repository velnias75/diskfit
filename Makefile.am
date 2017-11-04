SUBDIRS = src

ACLOCAL_AMFLAGS = -Im4

AM_DISTCHECK_CONFIGURE_FLAGS = --with-bash-completion-dir=no

doc_DATA = README.md
sysconf_DATA = diskfitrc

if INSTALL_BASHCOMP
completionsdir = $(bashcompdir)
dist_completions_DATA = diskfit
endif

EXTRA_DIST = $(doc_DATA) $(sysconf_DATA) diskfit.bc.in

DISTCLEANFILES = $(dist_completions_DATA)

if INSTALL_BASHCOMP
diskfit: $(top_srcdir)/diskfit.bc.in
	$(AM_V_GEN)$(SED) -e 's|@bindir[@]|$(DESTDIR)$(bindir)|g' < $< > $@
endif
