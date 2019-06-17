EXTRA_DIST = __init__.py \
             mainwindow.py \
             mainwindow.ui \
             progress.py \
             progress.ui

MAINTAINERCLEANFILES = $(top_srcdir)/src/python/qdiskfit/mainwindow/mainwindow.py \
                       $(top_srcdir)/src/python/qdiskfit/mainwindow/progress.py

%.py: %.ui
	$(PYUIC5) -o $@ $<

all-local: $(MAINTAINERCLEANFILES)
