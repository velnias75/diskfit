lib_LTLIBRARIES = libdiskfit.la

pkginclude_HEADERS = diskfit.h

noinst_HEADERS = fitem.h blocking_queue.h

libdiskfit_la_CPPFLAGS = -DHAVE_INLINE -DGSL_C99_INLINE
libdiskfit_la_CFLAGS = -fvisibility=hidden -ffast-math -fstrict-aliasing  -finline-functions
libdiskfit_la_SOURCES = libdiskfit.c blocking_queue.c
libdiskfit_la_LIBADD = $(LIBM) $(GSL_LIBS)
libdiskfit_la_LDFLAGS = -version-info 1:2 -pthread
