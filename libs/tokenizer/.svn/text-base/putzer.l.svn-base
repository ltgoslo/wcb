 /* -*- coding: iso-8859-1; -*- 

   putzer.l : clean files, i.e. remove double spaces, spaces at
   beginning or end of line, double newlines, overlong words etc.

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

   Written 2004
   by Sebastian Nagel, CIS Uni München */

%{

#include <stdio.h>
#include <string.h>
#include <unistd.h>

#include "LC_ISOlatin1.h"

#define tolower(c) tolower_ISOlatin1_tab[c]

unsigned char NEWLINE = '\n';
unsigned char HSPACE  = ' ';

typedef unsigned int BOOL;
enum { FALSE = 0, TRUE = 1 };

unsigned int stateINITIAL; /* faked state for INITIAL according to options */

struct option {
  /* don't use bit-maps: costs are 1% of time, saves almost no space */
  /* because option is frequently consulted in yylex */
  BOOL hyphCont;         
  BOOL printHyphen;      
  BOOL convCase;         
  BOOL quiet;            
  BOOL set;                /* options set in Lexer (do it only once) */
  unsigned int maxWordLength;
  unsigned int language;   /* reserved */
} option;


void
echo_char (unsigned char c)
{
  if (option.convCase == TRUE) /* case conversion */
    fputc(tolower((unsigned char)c), yyout);
  else
    fputc(c, yyout);
}

void
echo_yytext ()
{
  int i;
  if (option.convCase == TRUE) /* case conversion */
    {
      for (i = 0; yytext[i] != '\0'; i++)
	{
	  fputc(tolower((unsigned char)yytext[i]), yyout);
	}
    }
  else
    {
      fputs(yytext, yyout);
    }
}

void
max_word_control ()
{

  if ( option.maxWordLength && ( yyleng > option.maxWordLength ) )
    {
      if ( ! option.quiet )
	{
	  fprintf(stderr, "Word too long, stripping: \n  ");
	  fputs(yytext, stderr);
	  fprintf(stderr, "\n  =>\n  ");
	}
      yytext[option.maxWordLength] = '\0';
      if ( ! option.quiet )
	{
	  fputs(yytext, stderr);
	  fputc('\n', stderr);
	}
      echo_yytext();
    }
  else
    {
      echo_yytext();
    }
}

%}

%option 8bit batch ecs noyywrap noreject



LETTER    [A-Za-z\xc0-\xd6\xd8-\xf6\xf7-\xff]
LETTER_UC [A-Z\xc0-\xd6\xd8-\xde]
LETTER_LC [a-z\xdf-\xf6\xf7-\xff]
DIGIT     [0-9]
HSPACE    [\x20\t\xa0]
          /* normalize also non-breaking space */
VSPACE    [\n\r\f\v]
CONTR     [\x00-\x1f\x7f-\x9f]
SPACE     ({HSPACE}|{VSPACE}|{CONTR})
SOFTHYPHEN \xad
HYPHEN    [-{SOFTHYPHEN]



%s  contHyph noCaseConvMaxWords maxWords

%%


%{

  /* for processing options fake initial state */
 if (! option.set) {
   if (option.hyphCont == TRUE)
     stateINITIAL = contHyph;
   else if (option.maxWordLength != 0)
     stateINITIAL = maxWords;
   else if (option.convCase == FALSE)
     stateINITIAL = noCaseConvMaxWords;
   option.set = TRUE;
   BEGIN(stateINITIAL);
 }

%}


 /**** hyphenated words: ****/
<contHyph>{

{LETTER}+{SOFTHYPHEN}/{LETTER} {
		          /* because there is no function to unput
			     the prefix of yytext (like yyless() for
			     a suffix), we must unput each character
			     separately */
			  int i;
			  int in_word = 0;
			  char *yycopy = strdup(yytext);
			  for( i = yyleng - 1; i >= 0; --i ) {
			    if ( in_word )
			      unput( yycopy[i] );
			    if ( yycopy[i] == '\xad' )
			      in_word = 1;
			  }
			  free(yycopy);
                          }


{LETTER}+{HYPHEN}{HSPACE}*{VSPACE}{HSPACE}*/{LETTER_LC} {
		          /* because there is no function to unput
			     the prefix of yytext (like yyless() for
			     a suffix), we must unput each character
			     separately */
			  int i;
			  int in_word = 0;
			  char *yycopy = strdup(yytext);
			  for( i = yyleng - 1; i >= 0; --i ) {
			    if ( in_word )
			      unput( yycopy[i] );
			    if ( (yycopy[i] == '-') || (yycopy[i] == '\xad') )
			      in_word = 1;
			  }
			  free(yycopy);
                          }

}


 /*** spaces, newlines, control chars ***/

{HSPACE}*{VSPACE}{HSPACE}*{VSPACE}+{HSPACE}* {  /* paragraph break */
                           fputc(NEWLINE, yyout);
                           fputc(NEWLINE, yyout);
                           }
{HSPACE}*{VSPACE}{HSPACE}* {
                           fputc(NEWLINE, yyout);
                           /* skip also preceeding or following hor. spaces */
                           }
^{HSPACE}+                 ;

{HSPACE}+                  fputc(HSPACE, yyout);

{CONTR}+                   ;


 /*** letters ***/
<noCaseConvMaxWords>{
{LETTER}+                  ECHO;
}
<INITIAL>{
{LETTER_UC}                echo_char(yytext[0]);
{LETTER_LC}+               ECHO;
}
<maxWords,contHyph>{
{LETTER}+                  max_word_control();
}

 /*** other chars ***/
.                          ECHO;


%%

void
help ()
{
  fprintf(stdout,
	  "\n"
	  "putzer  --  clean files: remove double spaces, spaces at beginning or end of line,\n"
	  "               double newlines and ... (see options)\n"
	  "\n"
	  "   putzer [options] [files]\n"
	  "\n"
	  "   options:\n"
	  "     -i <filen>   input filename\n"
	  "     -o <filen>   output filename\n"
	  "     -c           combine continuation: hyphenated words on line breaks\n"
	  "                    will be put together\n"
	  "     -l           convert to lowercase (latin-1)\n"
	  "     -m <int>     maximal word length in chars:\n"
          "                  longer words will be stripped\n"
	  "     -q           quiet: don't report errors\n"
	  "     -h | -?      print this help and exit\n"
	  "   Other arguments will be read as input filenames.\n"
	  "   If no input files are given, input is read from stdin.\n"
	  "   If no output file is given, the tokenized text is written to stdout\n"
	  "\n");
  printf("putzer, Sebastian Nagel (wastl@cis.uni-muenchen.de)\n");
  exit(1);
}

int
main (int argc, char **argv)
{
  int c;
  while (1) {
    c = getopt(argc, argv, "cli:o:m:qh?");
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
      case 'c':
	option.hyphCont = TRUE;
	break;
      case 'l':
	option.convCase = TRUE;
	break;
      case 'm':
	if ( ! sscanf(optarg, "%d", &option.maxWordLength) )
	  fprintf(stderr, "Argument of -m must be an integer not \"%s\"!\n", optarg);
	break;
      case 'o':
	if (optarg != NULL && (yyout = fopen(optarg, "w")) == NULL)
	{
	  fprintf(stderr, "Can't open %s for writing!\n", optarg);
	  perror(optarg);
	  exit(1);
	}
	break;
      case 'i':
	if (optarg != NULL && (yyin = fopen(optarg, "r")) == NULL)
	  {
	    fprintf(stderr, "Can't read from %s!\n", optarg);
	    perror(optarg);
	    exit(1);
	  }
	break;
    }
  }
  if (optind < argc) /* remaing ARGVs are filenames */
  {
    while (optind < argc)
    {
      if (argv[optind] != NULL && (yyin = fopen(argv[optind], "r")) == NULL)
      {
	fprintf(stderr, "Can't read from %s!\n", argv[optind]);
	perror(argv[optind]);
	exit(1);
      }
      yylex();
      optind++;
    }
  }
  else /* default: read yyin/stdin, when no input-files are given */
  {
    yylex();
  }
  return 0;
}
