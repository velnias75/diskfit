#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ([2.69])
AC_INIT([DiskFit], [2.0.2.4], [heiko@rangun.de])
AC_CONFIG_SRCDIR([src/diskfit.c])
AC_CONFIG_HEADERS([config.h])

LT_INIT
AM_INIT_AUTOMAKE([foreign no-dist-gzip dist-xz])
AM_MAINTAINER_MODE
AC_CONFIG_MACRO_DIR([m4])

AC_SYS_LARGEFILE

# Checks for programs.
AC_PROG_CC_C99
AC_LANG_PUSH([C])

# Checks for libraries.
LT_LIB_M
AC_CHECK_LIB(gmp, main, , [AC_MSG_ERROR([Please install gmp - the GNU multiple precision arithmetic library])])

# Checks for header files.
AC_CHECK_HEADERS([stdlib.h string.h unistd.h stddef.h])
AC_CHECK_HEADERS([gmp.h], , [AC_MSG_ERROR([Please install gmp - the GNU multiple precision arithmetic library])])
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

PKG_CHECK_MODULES([GLIB2], [glib-2.0 >= 2.6])
PKG_CHECK_MODULES([GSL], [gsl >= 1.9])

# backwards compat with older pkg-config
# - pull in AC_DEFUN from pkg.m4
m4_ifndef([PKG_CHECK_VAR], [
# PKG_CHECK_VAR(VARIABLE, MODULE, CONFIG-VARIABLE,
# [ACTION-IF-FOUND], [ACTION-IF-NOT-FOUND])
# -------------------------------------------
# Retrieves the value of the pkg-config variable for the given module.
AC_DEFUN([PKG_CHECK_VAR],
[AC_REQUIRE([PKG_PROG_PKG_CONFIG])dnl
AC_ARG_VAR([$1], [value of $3 for $2, overriding pkg-config])dnl

_PKG_CONFIG([$1], [variable="][$3]["], [$2])
AS_VAR_COPY([$1], [pkg_cv_][$1])

AS_VAR_IF([$1], [""], [$5], [$4])dnl
])# PKG_CHECK_VAR
])

AM_CONDITIONAL([INSTALL_BASHCOMP], [ false ])

AC_ARG_WITH([bash-completion-dir], [AS_HELP_STRING([--with-bash-completion-dir=DIR],
  [directory to install bash completion files into])],
  [ if test "x$with_bash_completion_dir" != "xno"; then
      AM_CONDITIONAL([INSTALL_BASHCOMP], [ true ])
      bashcompdir="$with_bash_completion_dir"
        fi ],
  [  AM_CONDITIONAL([INSTALL_BASHCOMP], [ true ])
     PKG_CHECK_VAR(bashcompdir, [bash-completion], [completionsdir], ,
      bashcompdir="${sysconfdir}/bash_completion.d")
  ])

AC_SUBST([bashcompdir])

AC_LANG_POP([C])

AC_OUTPUT([Makefile src/Makefile src/lib/Makefile])
