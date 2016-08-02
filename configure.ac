#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ([2.69])
AC_INIT([DiskFit], [0.0], [heiko@rangun.de])
AC_CONFIG_SRCDIR([src/diskfit.c])
AC_CONFIG_HEADERS([config.h])

LT_INIT
AM_INIT_AUTOMAKE([foreign])
AC_CONFIG_MACRO_DIR([m4])

# Checks for programs.
AC_PROG_CC

# Checks for libraries.

# Checks for header files.
AC_CHECK_HEADERS([stdlib.h string.h unistd.h])

# Checks for typedefs, structures, and compiler characteristics.
AC_TYPE_OFF_T
AC_TYPE_SIZE_T

# Checks for library functions.
AC_CHECK_FUNCS([memset])
AC_FUNC_MALLOC
AC_CHECK_LIB([m],[log], [], [AC_MSG_ERROR([Could not find log in 'm'])])

AC_OUTPUT([Makefile src/Makefile])
