EXTRA_DIST = __init__.py \
             profile.ui \
             profile.py

MAINTAINERCLEANFILES = $(top_srcdir)/src/python/qdiskfit/dialogs/profile.py

%.py: %.ui
	$(PYUIC5) -o $@ $<

all-local: $(MAINTAINERCLEANFILES)
