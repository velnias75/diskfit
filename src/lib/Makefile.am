lib_LTLIBRARIES = libdiskfit.la

pkginclude_HEADERS = diskfit.h

noinst_HEADERS = fitem.h

libdiskfit_la_CFLAGS = -fvisibility=hidden -ffast-math -fstrict-aliasing  -finline-functions
libdiskfit_la_SOURCES = libdiskfit.c
libdiskfit_la_LIBADD = $(LIBM)
libdiskfit_la_LDFLAGS = -version-info 3:2
