/* a tokenizer with end-of-sentence detection 

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2, or (at your option)
   any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 51 Franklin Street - Fifth Floor, Boston, MA
   02110-1301, USA.

   Written 2004-2007
   by Sebastian Nagel, CIS Uni M,b|(Bnchen */



#if HAVE_CONFIG_H
#include <config.h>
#endif

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

/* definitions used by tokenizer.c and the language-specific lexers */
#include "Tokenizer.h"

/* all this variables will be overwritten according to language settings */
FILE* yyin;
FILE* yyout;
char** yytext_ptr;
int (*yylex)(void);
int* yyleng_ptr;

/* language specific definitions, functions for selecting language are in: */
#include "TokenizerLang.h"


void
usage ()
{
  fprintf(stderr,
	  "\n"
	  "tokenizer  --  a tokenizer with end-of-sentence detection\n"
	  "\n"
	  "   tokenizer OPTIONS [FILES]\n"
	  "\n"
	  "As minimal option you have to set -L <language>.\n"
	  "For which languages are available and other options type \"tokenizer -h\"\n"
	  "\n");
  exit(1);
}

void
help ()
{
  fprintf(stdout,
	  "\n"
	  "tokenizer  --  a tokenizer with end-of-sentence detection\n"
	  "\n"
	  "   tokenizer OPTIONS [FILES]\n"
	  "\n"
	  "   options:\n"
	  "     -o <filen>   output filename\n"
	  "     -L <lang>    language in a specific charset, actually supported:\n"
	  "                    de german   (iso-8859-1)\n"
	  "                    de-win german-win-cp1252 (cp1252)\n"
	  "                    de-u8 german-utf8 (rudimentary support for utf-8)\n"
	  "                    en english  (iso-8859-1)\n"
	  "                    en-win english-win-cp1252 (cp1252)\n"
	  "                    en-u8 english-utf8 (rudimentary support for utf-8)\n"
	  "                    ru russian  (iso-8859-5)\n"
	  "                    ru-win russian-win-cp1251 (cp1251)\n"
	  "                    ru-u8 russian-utf8 (rudimentary support for utf-8)\n"
	  "     -S           enable end-of-sentence detection\n"
	  "     -E <str>     specify EOS-mark (default: \"<EOS />\")\n"
	  "     -n           treat a new line as EOS\n"
	  "     -N           treat two or more new lines (paragraph break) as EOS\n"
	  "     -c           combine continuation I: hyphenated words on line breaks\n"
	  "                    will be put together. The hyphen is skipped.\n"
	  "     -C           combine continuation II: same as above, but the hyphen is\n"
	  "                    preserved. This may be a good option if you know that\n"
	  "                    there are no hyphenated words, but `bindestrichwoerter'\n"
	  "                    (like end-of-sentence) in your text.\n"
	  "     -W           detect www-adresses and treat them as one token\n"
	  "     -i | -l      convert all tokens to lowercase\n"
          "                    (according to language settings, not for utf-8)\n"
	  "     -s           single line mode: each token on a separate line\n"
	  "     -X <chr>     use <chr> as separator in single line mode instead <newline>.\n"
	  "                    Original newlines are preserved because putting the whole\n"
	  "                    input in one line isn't a good idea\n"
	  "     -p           paragraph mode:\n"
          "                    two or more newlines are interpreted as a paragraph\n"
          "                    break, a single newline will not. All lines\n"
          "                    of one paragraph are collected in one line\n"
	  "     -P           prints each sentence in a separate line\n"
	  "     -x           print spaces:\n"
	  "                    In single line mode horizontal spaces will be printed\n"
	  "                    as one space in a single line, vertikal spaces as\n"
	  "                    two line breaks.\n"
	  "                    In paragraph mode (including combination with -P)\n"
	  "                    an additional newline is inserted between paragraphs\n"
/* 	  "     -q           quiet: don't report errors\n" */
	  "     -h | -?      print this help and exit\n"
	  "\n"
	  "   Other arguments will be read as input filenames.\n"
	  "   If no input files are given, input is read from stdin.\n"
	  "   If no output file is given, the tokenized text is written to stdout\n"
	  "\n"
	  "WARNING: When the input contains long words or many following newlines\n"
          "   tokenizer stops with \"input buffer overflow\". To avoid this use putzer\n"
	  "   (included in your package) with option -m <max-word-length> as filter!\n"
	  "\n");
  printf("%s, v%s, %s (%s)\n",
	 PACKAGE_NAME, PACKAGE_VERSION, PACKAGE_AUTHOR, PACKAGE_BUGREPORT);
  exit(0);
}

void
set_defaults ()
{
  /* default options: */
  /*   option.language = GERMAN_L1; */
  /*   you have to set it by yourself: we won't prefer one language over another */
  option.eos      = 0;        /* EOS detection disabled */
  option.eosmark  = "<EOS />";
  option.tokSep   = '\n';
  option.new_line_as_eos = 0; /* -n, -N unset */
  option.outputMode = 0;      /* unset: -s, -p, -P */
  option.printSpace = FALSE;  /* -x unset */
  option.hyphCont = FALSE;    /* -c or */
  option.printHyphen = FALSE; /* -C unset */
  option.convCase = FALSE;    /* -i, -l unset */
  option.www      = FALSE;    /* -W unset */
  option.quiet    = FALSE;    /* warnings enabled */
  yyin = stdin;
  yyout = stdout;
}

/* functions for output of different TOK_TYPEs according to options -s, -n and -i/-l */
inline static void
print_token ()
{
  if (option.convCase == TRUE) /* case conversion */
    {
      while (**yytext_ptr != '\0')
	{
	  fputc(LC_tolower((unsigned char)**yytext_ptr), yyout);
	  (*yytext_ptr)++;
	}
    }
  else
    {
      fputs(*yytext_ptr, yyout);
    }
  if (option.outputMode == 1) /* single line mode */
    fputc(option.tokSep, yyout);
}



inline static void
print_space ()
{
  if (option.outputMode != 1) /* all but -s */
    fputc(' ', yyout);
  else if (option.printSpace == TRUE) /* -sx */
    fprintf(yyout, " %c", option.tokSep);
  /* else (option -s): print no space at all */
}

inline static void
print_newline ()
{
  if (option.printSpace)       /* -x */
    fprintf(yyout, "\n%c", option.tokSep);
  else
    fputc('\n', yyout);
}

inline static void
print_marker (char *marker)
{
  fputs(marker, yyout);
  if (option.outputMode == 1)     /* -s (single line mode) */
    fputc(option.tokSep, yyout);
}

inline static int
is_paragraph ()
{
  /* checks if the newline token (TOK_NEWLINE) returned by yylex()
     consists of two or more newlines ('\n'). */
  int nls = 0;
  char *pt = *yytext_ptr;
  while ((pt = strchr(pt, '\n')) != NULL)
    nls++, pt++;
  if (nls >= 2)
    return 1;
  return 0;
}

void
tokenize ()
{
  int token_type, last_token_type;
  while ((token_type = yylex()))
    {
      switch (token_type)
	{
	case TOK_WORD:
	case TOK_NUMBER:
	case TOK_WWW:
	case TOK_DATE:
	case TOK_ABBR:
	case TOK_COMPLEX:
	case TOK_OTHER:
	default:
 	print_token();
	break;
      case TOK_HSPACE:
	if ((option.outputMode == 3) /* -P: each sentence on a separate line */
	    && (last_token_type == TOK_EOS))
	  print_marker("\n");
	else
	  print_space();
	break;
      case TOK_VSPACE:
      case TOK_NEWLINE:
	if (option.eos && option.new_line_as_eos /* a newline may close the actual sentence */
	    && (last_token_type != TOK_EOS)) /* unless the sentence is already closed */
	  {
	    if (option.new_line_as_eos == 1
		|| (option.new_line_as_eos == 2 && is_paragraph()))
	      {
		print_marker(option.eosmark);
		last_token_type = TOK_EOS;
	      }
	  }
	/* whether or not a space or a newline will be printed
	   depends on the options -p or -P */
	if (option.outputMode == 3) /* option -P: each sentence on a separate line */
	  {
	    if (last_token_type == TOK_EOS)
	      print_marker("\n"); /* print a line break after EOS */
	    else
	      print_marker(" "); /* gather words of one sentence in one line */
	  }
	else if (option.outputMode == 2) /* option -p: collect all lines
					    of a paragraph in on line */
	  {
	    if (is_paragraph())
	      print_newline();
	    else
	      print_marker(" ");
	  }
	else if (option.outputMode == 1) /* -s */
	  {
	    if (option.printSpace)       /* -sx */
	      {
		/* in this case a newline is equivalent to a space */
		if (option.tokSep != '\n')
		  fputc('\n', yyout);
		else
		  fprintf(yyout, " %c", option.tokSep);
	      }
	  }
	else                             /* else */
	  {
	    if (is_paragraph())
	      {
		print_newline();
		print_newline();
	      }
	    else
	      print_newline();
	  }
	break;
      case TOK_EOS:
	print_marker(option.eosmark);
	break;
    }
    last_token_type = token_type;
  }
/*   if (option.eos) /\* end of file *\/ */
/*     print_marker(option.eosmark); */
}


int
main (int argc, char **argv)
{
  int c;

  set_defaults(); /* set default options */

  while (1) /* process options */
  {
    c = getopt(argc, argv, "L:SnNE:cCilWsX:xpPo:qh?");
    if (c == -1)
      break;
    switch (c)
    {
      case 'h':
      case '?':
	help();
	break;
      case 'q':
	option.quiet = TRUE;
	break;
      case 'S':
	option.eos = TRUE;
	break;
      case 'E':
	option.eosmark = optarg;
	break;
      case 'n':
	option.new_line_as_eos = 1;
	break;
      case 'N':
	option.new_line_as_eos = 2;
	break;
      case 'L':
	select_language(optarg);
	break;
      case 'W':
	option.www = TRUE;
	break;
      case 'c':
	option.hyphCont = TRUE;
	break;
      case 'C':
	option.hyphCont = TRUE;
	option.printHyphen = TRUE;
	break;
      case 's':
	option.outputMode = 1;
	break;
      case 'X':
	option.tokSep = optarg[0];
	break;
      case 'p':
	option.outputMode = 2;
	break;
      case 'P':
	option.outputMode = 3;
	break;
      case 'x':
	option.printSpace = TRUE;
	break;
      case 'i':
      case 'l':
	option.convCase = TRUE;
	break;
      case 'o':
	if (optarg != NULL && (yyout = fopen(optarg, "w")) == NULL)
	{
	  fprintf(stderr, "Can't open %s for writing!\n", optarg);
	  perror(optarg);
	  exit(1);
	}
	break;
    }
  }

  if (option.language)
    switch_language(); /* set language */
  else
    usage();

  if (optind < argc) /* remaing ARGVs are filenames */
  {
    while (optind < argc)
    {
      if (argv[optind] != NULL && (yyin = fopen(argv[optind], "r")) == NULL)
      {
	fprintf(stderr, "Can't read from %s", argv[optind]);
	perror(argv[optind]);
	exit(1);
      }
      switch_language(); /* must be called to reset filehandle pointers */
                         /* yy<Lang><in|out> to actual opened file */
      tokenize();
      fclose(yyin);
      optind++;
    }
  }
  else /* default: read stdin, when no input-files are given */
  {
    switch_language();
    tokenize();
  }

  return 0;

}
