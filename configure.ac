#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ([2.69])
AC_INIT([DiskFit], [1.0.2], [heiko@rangun.de])
AC_CONFIG_SRCDIR([src/diskfit.c])
AC_CONFIG_HEADERS([config.h])

LT_INIT
AM_INIT_AUTOMAKE([foreign no-dist-gzip dist-xz])
AC_CONFIG_MACRO_DIR([m4])

AC_SYS_LARGEFILE

# Checks for programs.
AC_PROG_CC_C99
AC_LANG_PUSH([C])

# Checks for libraries.
LT_LIB_M

# Checks for header files.
AC_CHECK_HEADERS([stdlib.h string.h unistd.h stddef.h])
AC_CHECK_HEADER_STDBOOL

# Checks for typedefs, structures, and compiler characteristics.
AC_TYPE_OFF_T
AC_TYPE_SIZE_T
AC_C_RESTRICT
AC_TYPE_UINT64_T
AC_C_INLINE

# Checks for library functions.
AC_CHECK_FUNCS([memset])
AC_CHECK_FUNCS([memmove])
AC_CHECK_FUNCS([strcasecmp])
AC_FUNC_ERROR_AT_LINE
AC_FUNC_MALLOC

PKG_CHECK_MODULES([GLIB2], [glib-2.0])

AC_LANG_POP([C])

AC_OUTPUT([Makefile src/Makefile src/lib/Makefile])
