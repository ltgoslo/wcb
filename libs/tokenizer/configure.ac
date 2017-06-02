#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ(2.59)
AC_INIT([tokenizer],[1.0],[wastl@cis.uni-muenchen.de])
AC_DEFINE([PACKAGE_AUTHOR],["Sebastian Nagel"],[Author])
AM_INIT_AUTOMAKE([foreign])
AC_CONFIG_SRCDIR([tokenizer.c])
AC_CONFIG_HEADER([config.h])

# Checks for programs.
AC_PROG_CC
AM_PROG_LEX

# Checks for libraries.
AC_CHECK_LIB([fl], [main])

# Checks for header files.
AC_HEADER_STDC
AC_CHECK_HEADERS([stdlib.h string.h unistd.h])

# Checks for typedefs, structures, and compiler characteristics.
AC_C_INLINE

# Checks for library functions.
AC_CHECK_FUNCS([strcasecmp strchr strdup])

AC_CONFIG_FILES([Makefile])
AC_OUTPUT
