 /* 
   converter for HTML-entities 
   HTML-entities from the input stream are converted
   to characters in UTF-8 or ISO-8859-1 (see options)

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


%option caseful 8bit batch noyywrap

%{

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>

typedef unsigned int BOOL;
enum { FALSE = 0, TRUE = 1 };

enum { ISO_LATIN_1 = 1, UTF8 };

struct option {
  BOOL QUIET;
  unsigned char ENCODING;
  BOOL FORCE;
  BOOL Replace;
  unsigned int rChar;
  BOOL replace;
  char* rString;
} option
    = { FALSE, /* (QUIET) default: report errors */
	UTF8,  /* default encoding */
	FALSE, /* don't skip unrecognized/unprintable characters */
	FALSE, /* don't replace unrecognized/unprintable characters */
	0x3f,  /* question mark */
	FALSE, /* don't replace unrecognized/unprintable characters */
	"???"
    };	

unsigned int num; /* buffer for value of numerical entities */

inline static char*
num_to_utf8 (int num, char* out)
{
  int i = 0;
  if (num <= 0x7f) {
    out[i++] = (unsigned char)(num);
  } else if (num <= 0x7ff) {
    /* 00000000 00000000 00000bbb bbaaaaaa  ==>   110bbbbb 10aaaaaa */
    out[i++] = (unsigned char)(0xc0 | (num >> 6));
    out[i++] = (unsigned char)(0x80 | (num & 0x3f));
  } else if (num <= 0xffff) {
    /* 00000000 00000000 ccccbbbb bbaaaaaa  ==>   1110cccc 10bbbbbb 10aaaaaa */
    out[i++] = (unsigned char)(0xe0 | (num >> 12));
    out[i++] = (unsigned char)(0x80 | ((num >> 6) & 0x3f));
    out[i++] = (unsigned char)(0x80 | (num & 0x3f));
  } else if (num <= 0x10ffff) {
    /* 00000000 000dddcc ccccbbbb bbaaaaaa  ==>   11110ddd 10cccccc 10bbbbbb 10aaaaaa */
    out[i++] = (unsigned char)(0xf0 | (num >> 18));
    out[i++] = (unsigned char)(0x80 | ((num >> 12) & 0x3f));
    out[i++] = (unsigned char)(0x80 | ((num >> 6) & 0x3f));
    out[i++] = (unsigned char)(0x80 | (num & 0x3f));
  } else {
    /* characters > 0x10ffff are illegal in Unicode 4.0 */
    if (option.QUIET != TRUE)
      fprintf(stderr, "Char 0x%x (\"%s\") not defined in unicode!\n", num, yytext);
  }
  out[i] = '\0';
  return out;
}

inline static char* 
num_to_iso_latin_1 (int num, char* out)
{
  int i = 0;
  if (num <= 0xff)
    out[i++] = (unsigned char)(num);
  else
    if (option.QUIET != TRUE)
      fprintf(stderr, "Char 0x%x (\"%s\") doesn't exist in ISO-8859-1: use UTF-8!\n", num, yytext);
  out[i] = '\0';
  return out;
}

inline static void
out (unsigned int num)
{
  char out[8];
  if ( option.ENCODING == UTF8 )
    num_to_utf8(num, out);
  else if ( option.ENCODING == ISO_LATIN_1 )
    num_to_iso_latin_1(num, out);
  fputs(out, yyout);
}

%}

%%

&quot;         out(0x22); /* quotation mark = APL quote */
&amp;          out(0x26); /* ampersand */
&lt;           out(0x3c); /* less-than sign */
&gt;           out(0x3e); /* greater-than sign */
&nbsp;         out(0xa0); /* no-break space = non-breaking space */
&iexcl;        out(0xa1); /* inverted exclamation mark */
&cent;         out(0xa2); /* cent sign */
&pound;        out(0xa3); /* pound sign */
&curren;       out(0xa4); /* currency sign */
&yen;          out(0xa5); /* yen sign = yuan sign */
&brvbar;       out(0xa6); /* broken bar = broken vertical bar */
&sect;         out(0xa7); /* section sign */
&uml;          out(0xa8); /* diaeresis = spacing diaeresis */
&copy;         out(0xa9); /* copyright sign */
&ordf;         out(0xaa); /* feminine ordinal indicator */
&laquo;        out(0xab); /* left-pointing double angle quotation mark */
&not;          out(0xac); /* not sign */
&shy;          out(0xad); /* soft hyphen = discretionary hyphen */
&reg;          out(0xae); /* registered sign = registered trade mark sign */
&macr;         out(0xaf); /* macron = spacing macron = overline */
&deg;          out(0xb0); /* degree sign */
&plusmn;       out(0xb1); /* plus-minus sign = plus-or-minus sign */
&sup2;         out(0xb2); /* superscript two = superscript digit two */
&sup3;         out(0xb3); /* superscript three = superscript digit three */
&acute;        out(0xb4); /* acute accent = spacing acute */
&micro;        out(0xb5); /* micro sign */
&para;         out(0xb6); /* pilcrow sign = paragraph sign */
&middot;       out(0xb7); /* middle dot = Georgian comma */
&cedil;        out(0xb8); /* cedilla = spacing cedilla */
&sup1;         out(0xb9); /* superscript one = superscript digit one */
&ordm;         out(0xba); /* masculine ordinal indicator */
&raquo;        out(0xbb); /* right-pointing double angle quotation mark */
&frac14;       out(0xbc); /* vulgar fraction one quarter */
&frac12;       out(0xbd); /* vulgar fraction one half */
&frac34;       out(0xbe); /* vulgar fraction three quarters */
&iquest;       out(0xbf); /* inverted question mark */
&Agrave;       out(0xc0); /* latin capital letter A with grave */
&Aacute;       out(0xc1); /* latin capital letter A with acute */
&Acirc;        out(0xc2); /* latin capital letter A with circumflex */
&Atilde;       out(0xc3); /* latin capital letter A with tilde */
&Auml;         out(0xc4); /* latin capital letter A with diaeresis */
&Aring;        out(0xc5); /* latin capital letter A with ring above */
&AElig;        out(0xc6); /* latin capital letter AE */
&Ccedil;       out(0xc7); /* latin capital letter C with cedilla */
&Egrave;       out(0xc8); /* latin capital letter E with grave */
&Eacute;       out(0xc9); /* latin capital letter E with acute */
&Ecirc;        out(0xca); /* latin capital letter E with circumflex */
&Euml;         out(0xcb); /* latin capital letter E with diaeresis */
&Igrave;       out(0xcc); /* latin capital letter I with grave */
&Iacute;       out(0xcd); /* latin capital letter I with acute */
&Icirc;        out(0xce); /* latin capital letter I with circumflex */
&Iuml;         out(0xcf); /* latin capital letter I with diaeresis */
&ETH;          out(0xd0); /* latin capital letter ETH */
&Ntilde;       out(0xd1); /* latin capital letter N with tilde */
&Ograve;       out(0xd2); /* latin capital letter O with grave */
&Oacute;       out(0xd3); /* latin capital letter O with acute */
&Ocirc;        out(0xd4); /* latin capital letter O with circumflex */
&Otilde;       out(0xd5); /* latin capital letter O with tilde */
&Ouml;         out(0xd6); /* latin capital letter O with diaeresis */
&times;        out(0xd7); /* multiplication sign */
&Oslash;       out(0xd8); /* latin capital letter O with stroke */
&Ugrave;       out(0xd9); /* latin capital letter U with grave */
&Uacute;       out(0xda); /* latin capital letter U with acute */
&Ucirc;        out(0xdb); /* latin capital letter U with circumflex */
&Uuml;         out(0xdc); /* latin capital letter U with diaeresis */
&Yacute;       out(0xdd); /* latin capital letter Y with acute */
&THORN;        out(0xde); /* latin capital letter THORN */
&szlig;        out(0xdf); /* latin small letter sharp s = ess-zed */
&agrave;       out(0xe0); /* latin small letter a with grave */
&aacute;       out(0xe1); /* latin small letter a with acute */
&acirc;        out(0xe2); /* latin small letter a with circumflex */
&atilde;       out(0xe3); /* latin small letter a with tilde */
&auml;         out(0xe4); /* latin small letter a with diaeresis */
&aring;        out(0xe5); /* latin small letter a with ring above */
&aelig;        out(0xe6); /* latin small letter ae */
&ccedil;       out(0xe7); /* latin small letter c with cedilla */
&egrave;       out(0xe8); /* latin small letter e with grave */
&eacute;       out(0xe9); /* latin small letter e with acute */
&ecirc;        out(0xea); /* latin small letter e with circumflex */
&euml;         out(0xeb); /* latin small letter e with diaeresis */
&igrave;       out(0xec); /* latin small letter i with grave */
&iacute;       out(0xed); /* latin small letter i with acute */
&icirc;        out(0xee); /* latin small letter i with circumflex */
&iuml;         out(0xef); /* latin small letter i with diaeresis */
&eth;          out(0xf0); /* latin small letter eth */
&ntilde;       out(0xf1); /* latin small letter n with tilde */
&ograve;       out(0xf2); /* latin small letter o with grave */
&oacute;       out(0xf3); /* latin small letter o with acute */
&ocirc;        out(0xf4); /* latin small letter o with circumflex */
&otilde;       out(0xf5); /* latin small letter o with tilde */
&ouml;         out(0xf6); /* latin small letter o with diaeresis */
&divide;       out(0xf7); /* division sign */
&oslash;       out(0xf8); /* latin small letter o with stroke */
&ugrave;       out(0xf9); /* latin small letter u with grave */
&uacute;       out(0xfa); /* latin small letter u with acute */
&ucirc;        out(0xfb); /* latin small letter u with circumflex */
&uuml;         out(0xfc); /* latin small letter u with diaeresis */
&yacute;       out(0xfd); /* latin small letter y with acute */
&thorn;        out(0xfe); /* latin small letter thorn */
&yuml;         out(0xff); /* latin small letter y with diaeresis */
&fnof;         out(0x192); /* latin small f with hook = function */
&Alpha;        out(0x391); /* greek capital letter alpha */
&Beta;         out(0x392); /* greek capital letter beta */
&Gamma;        out(0x393); /* greek capital letter gamma */
&Delta;        out(0x394); /* greek capital letter delta */
&Epsilon;      out(0x395); /* greek capital letter epsilon */
&Zeta;         out(0x396); /* greek capital letter zeta */
&Eta;          out(0x397); /* greek capital letter eta */
&Theta;        out(0x398); /* greek capital letter theta */
&Iota;         out(0x399); /* greek capital letter iota */
&Kappa;        out(0x39a); /* greek capital letter kappa */
&Lambda;       out(0x39b); /* greek capital letter lambda */
&Mu;           out(0x39c); /* greek capital letter mu */
&Nu;           out(0x39d); /* greek capital letter nu */
&Xi;           out(0x39e); /* greek capital letter xi */
&Omicron;      out(0x39f); /* greek capital letter omicron */
&Pi;           out(0x3a0); /* greek capital letter pi */
&Rho;          out(0x3a1); /* greek capital letter rho */
&Sigma;        out(0x3a3); /* greek capital letter sigma */
&Tau;          out(0x3a4); /* greek capital letter tau */
&Upsilon;      out(0x3a5); /* greek capital letter upsilon */
&Phi;          out(0x3a6); /* greek capital letter phi */
&Chi;          out(0x3a7); /* greek capital letter chi */
&Psi;          out(0x3a8); /* greek capital letter psi */
&Omega;        out(0x3a9); /* greek capital letter omega */
&alpha;        out(0x3b1); /* greek small letter alpha */
&beta;         out(0x3b2); /* greek small letter beta */
&gamma;        out(0x3b3); /* greek small letter gamma */
&delta;        out(0x3b4); /* greek small letter delta */
&epsilon;      out(0x3b5); /* greek small letter epsilon */
&zeta;         out(0x3b6); /* greek small letter zeta */
&eta;          out(0x3b7); /* greek small letter eta */
&theta;        out(0x3b8); /* greek small letter theta */
&iota;         out(0x3b9); /* greek small letter iota */
&kappa;        out(0x3ba); /* greek small letter kappa */
&lambda;       out(0x3bb); /* greek small letter lambda */
&mu;           out(0x3bc); /* greek small letter mu */
&nu;           out(0x3bd); /* greek small letter nu */
&xi;           out(0x3be); /* greek small letter xi */
&omicron;      out(0x3bf); /* greek small letter omicron */
&pi;           out(0x3c0); /* greek small letter pi */
&rho;          out(0x3c1); /* greek small letter rho */
&sigmaf;       out(0x3c2); /* greek small letter final sigma */
&sigma;        out(0x3c3); /* greek small letter sigma */
&tau;          out(0x3c4); /* greek small letter tau */
&upsilon;      out(0x3c5); /* greek small letter upsilon */
&phi;          out(0x3c6); /* greek small letter phi */
&chi;          out(0x3c7); /* greek small letter chi */
&psi;          out(0x3c8); /* greek small letter psi */
&omega;        out(0x3c9); /* greek small letter omega */
&thetasym;     out(0x3d1); /* greek small letter theta symbol */
&upsih;        out(0x3d2); /* greek upsilon with hook symbol */
&piv;          out(0x3d6); /* greek pi symbol */
&bull;         out(0x2022); /* bullet = black small circle */
&hellip;       out(0x2026); /* horizontal ellipsis = three dot leader */
&prime;        out(0x2032); /* prime = minutes = feet */
&Prime;        out(0x2033); /* double prime = seconds = inches */
&oline;        out(0x203e); /* overline = spacing overscore */
&frasl;        out(0x2044); /* fraction slash */
&weierp;       out(0x2118); /* script capital P = power set */
&image;        out(0x2111); /* blackletter capital I = imaginary part */
&real;         out(0x211c); /* blackletter capital R = real part symbol */
&trade;        out(0x2122); /* trade mark sign */
&alefsym;      out(0x2135); /* alef symbol = first transfinite cardinal */
&larr;         out(0x2190); /* leftwards arrow */
&uarr;         out(0x2191); /* upwards arrow */
&rarr;         out(0x2192); /* rightwards arrow */
&darr;         out(0x2193); /* downwards arrow */
&harr;         out(0x2194); /* left right arrow */
&crarr;        out(0x21b5); /* downwards arrow with corner leftwards */
&lArr;         out(0x21d0); /* leftwards double arrow */
&uArr;         out(0x21d1); /* upwards double arrow */
&rArr;         out(0x21d2); /* rightwards double arrow */
&dArr;         out(0x21d3); /* downwards double arrow */
&hArr;         out(0x21d4); /* left right double arrow */
&forall;       out(0x2200); /* for all */
&part;         out(0x2202); /* partial differential */
&exist;        out(0x2203); /* there exists */
&empty;        out(0x2205); /* empty set = null set = diameter */
&nabla;        out(0x2207); /* nabla = backward difference */
&isin;         out(0x2208); /* element of */
&notin;        out(0x2209); /* not an element of */
&ni;           out(0x220b); /* contains as member */
&prod;         out(0x220f); /* n-ary product = product sign */
&sum;          out(0x2211); /* n-ary sumation */
&minus;        out(0x2212); /* minus sign */
&lowast;       out(0x2217); /* asterisk operator */
&radic;        out(0x221a); /* square root = radical sign */
&prop;         out(0x221d); /* proportional to */
&infin;        out(0x221e); /* infinity */
&ang;          out(0x2220); /* angle */
&and;          out(0x2227); /* logical and = wedge */
&or;           out(0x2228); /* logical or = vee */
&cap;          out(0x2229); /* intersection = cap */
&cup;          out(0x222a); /* union = cup */
&int;          out(0x222b); /* integral */
&there4;       out(0x2234); /* therefore */
&sim;          out(0x223c); /* tilde operator = varies with = similar to */
&cong;         out(0x2245); /* approximately equal to */
&asymp;        out(0x2248); /* almost equal to = asymptotic to */
&ne;           out(0x2260); /* not equal to */
&equiv;        out(0x2261); /* identical to */
&le;           out(0x2264); /* less-than or equal to */
&ge;           out(0x2265); /* greater-than or equal to */
&sub;          out(0x2282); /* subset of */
&sup;          out(0x2283); /* superset of */
&nsub;         out(0x2284); /* not a subset of */
&sube;         out(0x2286); /* subset of or equal to */
&supe;         out(0x2287); /* superset of or equal to */
&oplus;        out(0x2295); /* circled plus = direct sum */
&otimes;       out(0x2297); /* circled times = vector product */
&perp;         out(0x22a5); /* up tack = orthogonal to = perpendicular */
&sdot;         out(0x22c5); /* dot operator */
&lceil;        out(0x2308); /* left ceiling = apl upstile */
&rceil;        out(0x2309); /* right ceiling */
&lfloor;       out(0x230a); /* left floor = apl downstile */
&rfloor;       out(0x230b); /* right floor */
&lang;         out(0x2329); /* left-pointing angle bracket = bra */
&rang;         out(0x232a); /* right-pointing angle bracket = ket */
&loz;          out(0x25ca); /* lozenge */
&spades;       out(0x2660); /* black spade suit */
&clubs;        out(0x2663); /* black club suit = shamrock */
&hearts;       out(0x2665); /* black heart suit = valentine */
&diams;        out(0x2666); /* black diamond suit */
&OElig;        out(0x152); /* latin capital ligature OE */
&oelig;        out(0x153); /* latin small ligature oe */
&Scaron;       out(0x160); /* latin capital letter S with caron */
&scaron;       out(0x161); /* latin small letter s with caron */
&Yuml;         out(0x178); /* latin capital letter Y with diaeresis */
&circ;         out(0x2c6); /* modifier letter circumflex accent */
&tilde;        out(0x2dc); /* small tilde */
&ensp;         out(0x2002); /* en space */
&emsp;         out(0x2003); /* em space */
&thinsp;       out(0x2009); /* thin space */
&zwnj;         out(0x200c); /* zero width non-joiner */
&zwj;          out(0x200d); /* zero width joiner */
&lrm;          out(0x200e); /* left-to-right mark */
&rlm;          out(0x200f); /* right-to-left mark */
&ndash;        out(0x2013); /* en dash */
&mdash;        out(0x2014); /* em dash */
&lsquo;        out(0x2018); /* left single quotation mark */
&rsquo;        out(0x2019); /* right single quotation mark */
&sbquo;        out(0x201a); /* single low-9 quotation mark */
&ldquo;        out(0x201c); /* left double quotation mark */
&rdquo;        out(0x201d); /* right double quotation mark */
&bdquo;        out(0x201e); /* double low-9 quotation mark */
&dagger;       out(0x2020); /* dagger */
&Dagger;       out(0x2021); /* double dagger */
&permil;       out(0x2030); /* per mille sign */
&lsaquo;       out(0x2039); /* single left-pointing angle quotation mark */
&rsaquo;       out(0x203a); /* single right-pointing angle quotation mark */
&euro;         out(0x20ac); /* euro sign */

"&#x"[0-9A-Fa-f]+";"    { sscanf(yytext, "&#x%x", &num);
                          out(num); }
"&#X"[0-9A-Fa-f]+";"    { sscanf(yytext, "&#X%x", &num);
                          out(num); }

"&#"[0-9]+";"    { sscanf(yytext, "&#%d", &num);
                   out(num); }

"&"[^;]{1,8}";"  { if (option.QUIET != TRUE)
                     fprintf(stderr, "invalid entity or unescaped ampersand: %s\n", yytext);
                   if (option.Replace == TRUE)
		     out(option.rChar);
		   else if (option.replace == TRUE)
		     fputs(option.rString, yyout);
		   else if (option.FORCE == TRUE) {}
		   else
                     fprintf(stdout, "&"); /* skip "&" */
                     yyless(1); }

[^&]+            ECHO;
.                ECHO;


%%

void
help ()
{
  fprintf(stdout,
	  "\n"
	  "htmlEnt2Char  --  replaces HTML entities\n"
	  "   options:\n"
	  "     -C <encod>   output encoding, actually supported:\n"
	  "                        l1 lat1 latin1 iso-8859-1\n"
	  "                        u8 utf-8 (default)\n"
	  "     -o <filen>   output filename\n"
	  "     -f           force: skip misspelled entities or\n"
          "                  entities not printable in given charset\n"
	  "                  (see also -r or -R)\n"
	  "     -r <string>  replace unrecognized/unprintable entities\n"
	  "                  by <string>\n"
	  "     -R <num>     replace unrecognized/unprintable entities\n"
	  "                  by a character given as <num>, a Unicode code point\n"
	  "                  Interpretation of <num> follows the C convention:\n"
	  "                  0x.... for hexadecimal numbers\n"
	  "                  0....  for octal numbers\n"
	  "                  ....   for decimal numbers\n"
	  "     -q           quiet: don't report errors, misspelled\n"
	  "                    entities etc.\n"
	  "     -h | -?      print this help and exit\n"
	  "   Other arguments will be read as input filenames.\n"
	  "   If no input files are given, input is read from stdin.\n"
	  "   If no output file is given, the text with replacements\n"
	  "   is written to stdout.\n\n");
  printf("htmlEnt2Char, Sebastian Nagel (wastl@cis.uni-muenchen.de)\n");
  exit(1);
}

int
main (int argc, char **argv)
{
  int c;
  while (1) {
    c = getopt(argc, argv, ":C:o:fqr:R:h?");
    if (c == -1)
      break;
    switch (c) {
      case 'h':
      case '?':
	help();
      case 'q':
	option.QUIET = TRUE;
	break;
      case 'C':
	if ((! strcmp(optarg, "l1")) ||
	    (! strcmp(optarg, "ISO-8859-1")) ||
	    (! strcmp(optarg, "iso-8859-1")) ||
	    (! strcmp(optarg, "lat1")) ||
	    (! strcmp(optarg, "latin1")) ||
	    (! strcmp(optarg, "latin-1")) ||
	    (! strcmp(optarg, "Latin-1")))
	  option.ENCODING = ISO_LATIN_1;
	else if ((! strcmp(optarg, "u8")) ||
		 (! strcmp(optarg, "utf-8")) ||
		 (! strcmp(optarg, "UTF-8")))
	  option.ENCODING = UTF8;
	break;
      case 'o':
	if (optarg != NULL && (yyout = fopen(optarg, "w")) == NULL) {
	  fprintf(stderr, "Can't open %s for writing!\n", optarg);
	  exit(1);
	}
	break;
      case 'f':
	option.FORCE = TRUE;
	break;
      case 'r':
	option.replace = TRUE;
	option.rString = optarg;
	break;
      case 'R':
	option.Replace = TRUE;
	sscanf(optarg, "0x%x", &option.rChar)
	  || sscanf(optarg, "0%o", &option.rChar)
	  || sscanf(optarg, "%u", &option.rChar);
	break;
	
    }
  }
  if (option.ENCODING == ISO_LATIN_1
      && option.rChar >= 0xff)
    {
      fprintf(stderr, "Replacement character not in iso-8859-1!\n");
      exit(1);
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
