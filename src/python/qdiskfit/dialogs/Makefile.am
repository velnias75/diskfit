EXTRA_DIST = __init__.py \
             exclusive.py \
             exclusive.ui \
             exclusivewidget.py \
             profile.ui \
             profile.py

MAINTAINERCLEANFILES = $(top_srcdir)/src/python/qdiskfit/dialogs/exclusive.py \
                       $(top_srcdir)/src/python/qdiskfit/dialogs/exclusivewidget.py \
                       $(top_srcdir)/src/python/qdiskfit/dialogs/profile.py

%.py: %.ui
	$(PYUIC5) -o $@ $<

all-local: $(MAINTAINERCLEANFILES)
