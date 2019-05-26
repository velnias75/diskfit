SUBDIRS = qdiskfit

EXTRA_DIST = LICENSE \
             README \
             setup.py \
             qdiskfit.pro \
             qdiskfit.svg \
             qdiskfit.desktop \
             qdiskfit_de.qm \
             qdiskfit_de.ts

all-local:
	(cd $(srcdir); $(PYTHON) setup.py build \
		--build-base $(shell readlink -f $(builddir))/build \
		--verbose)

install-exec-local:
	mkdir -p $(DESTDIR)$(pkgpythondir)
	$(PYTHON) $(srcdir)/setup.py install \
		--prefix $(DESTDIR)$(prefix) \
		--single-version-externally-managed \
		--record $(DESTDIR)$(pkgpythondir)/install_files.txt \
		--verbose

uninstall-local:
	cat $(DESTDIR)$(pkgpythondir)/install_files.txt | xargs rm -rf
	rm -rf $(DESTDIR)$(pkgpythondir)

clean-local:
	rm -rf build *.egg-info
