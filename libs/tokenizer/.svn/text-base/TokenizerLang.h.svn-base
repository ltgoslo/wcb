/* TokenizerLang.h -- definitions for switching between languages */
/* outsorced from tokenizer.c: could be also there   */

#include "LC_ISOlatin1.h"
#include "LC_ISOcyrillic5.h"
#include "LC_cp1252.h"
#include "LC_cp1251.h"
#include "LC_ascii.h"

#define LC_tolower(c) LC_tolower_tab[c]
/* pseudo function for downcasing strings */

char* LC_tolower_tab; /* will be set according to language settings */

/* language resp. charset */
enum {
  GERMAN_L1 = 1,
  GERMAN_WIN,
  GERMAN_U8,
  ENGLISH_L1,
  ENGLISH_WIN,
  ENGLISH_U8,
  RUSSIAN_ISO5,
  RUSSIAN_WIN,
  RUSSIAN_U8
};

/* german / iso-latin-1  -> TokenizeDeL1.l */
extern FILE* yyDeL1in;
extern FILE* yyDeL1out;
extern int yyDeL1lex(void);
extern char* yyDeL1text;
extern int yyDeL1leng;

/* german / win-cp1252  -> TokenizeDeWin.l */
extern FILE* yyDeWinin;
extern FILE* yyDeWinout;
extern int yyDeWinlex(void);
extern char* yyDeWintext;
extern int yyDeWinleng;

/* german / utf-8  -> TokenizeDeU8.l */
extern FILE* yyDeU8in;
extern FILE* yyDeU8out;
extern int yyDeU8lex(void);
extern char* yyDeU8text;
extern int yyDeU8leng;

/* english / iso-latin-1  -> TokenizeEnL1.l */
extern FILE* yyEnL1in;
extern FILE* yyEnL1out;
extern int yyEnL1lex(void);
extern char* yyEnL1text;
extern int yyEnL1leng;

/* english / win-cp1252  -> TokenizeEnWin.l */
extern FILE* yyEnWinin;
extern FILE* yyEnWinout;
extern int yyEnWinlex(void);
extern char* yyEnWintext;
extern int yyEnWinleng;

/* english / utf-8  -> TokenizeEnU8.l */
extern FILE* yyEnU8in;
extern FILE* yyEnU8out;
extern int yyEnU8lex(void);
extern char* yyEnU8text;
extern int yyEnU8leng;

/* russian / iso-8859-5  -> TokenizeRuI5.l */
extern FILE* yyRuI5in;
extern FILE* yyRuI5out;
extern int yyRuI5lex(void);
extern char* yyRuI5text;
extern int yyRuI5leng;

/* russian / win-cp1251  -> TokenizeRuWin.l */
extern FILE* yyRuWinin;
extern FILE* yyRuWinout;
extern int yyRuWinlex(void);
extern char* yyRuWintext;
extern int yyRuWinleng;

/* russian / utf-8  -> TokenizeRuU8.l */
extern FILE* yyRuU8in;
extern FILE* yyRuU8out;
extern int yyRuU8lex(void);
extern char* yyRuU8text;
extern int yyRuU8leng;

void
switch_language ()
{
  if (option.language == GERMAN_L1)
    {
      yyDeL1in = yyin;
      yyDeL1out = yyout;
      yylex = (int (*)(void))(yyDeL1lex);
      yytext_ptr = &yyDeL1text;
      yyleng_ptr = &yyDeL1leng;
      LC_tolower_tab = tolower_ISOlatin1_tab;
    }
  else if (option.language == GERMAN_WIN)
    {
      yyDeWinin = yyin;
      yyDeWinout = yyout;
      yylex = (int (*)(void))(yyDeWinlex);
      yytext_ptr = &yyDeWintext;
      yyleng_ptr = &yyDeWinleng;
      LC_tolower_tab = tolower_cp1252_tab;
    }
  else if (option.language == GERMAN_U8)
    {
      yyDeU8in = yyin;
      yyDeU8out = yyout;
      yylex = (int (*)(void))(yyDeU8lex);
      yytext_ptr = &yyDeU8text;
      yyleng_ptr = &yyDeU8leng;
      LC_tolower_tab = tolower_ascii_tab;
    }
  else if (option.language == ENGLISH_L1)
    {
      yyEnL1in = yyin;
      yyEnL1out = yyout;
      yylex = (int (*)(void))(yyEnL1lex);
      yytext_ptr = &yyEnL1text;
      yyleng_ptr = &yyEnL1leng;
      LC_tolower_tab = tolower_ISOlatin1_tab;
    }
  else if (option.language == ENGLISH_WIN)
    {
      yyEnWinin = yyin;
      yyEnWinout = yyout;
      yylex = (int (*)(void))(yyEnWinlex);
      yytext_ptr = &yyEnWintext;
      yyleng_ptr = &yyEnWinleng;
      LC_tolower_tab = tolower_cp1252_tab;
    }
  else if (option.language == ENGLISH_U8)
    {
      yyEnU8in = yyin;
      yyEnU8out = yyout;
      yylex = (int (*)(void))(yyEnU8lex);
      yytext_ptr = &yyEnU8text;
      yyleng_ptr = &yyEnU8leng;
      LC_tolower_tab = tolower_ascii_tab;
    }
  else if (option.language == RUSSIAN_ISO5)
    {
      yyRuI5in = yyin;
      yyRuI5out = yyout;
      yylex = (int (*)(void))(yyRuI5lex);
      yytext_ptr = &yyRuI5text;
      yyleng_ptr = &yyRuI5leng;
      LC_tolower_tab = tolower_ISO5_tab;
    }
  else if (option.language == RUSSIAN_WIN)
    {
      yyRuWinin = yyin;
      yyRuWinout = yyout;
      yylex = (int (*)(void))(yyRuWinlex);
      yytext_ptr = &yyRuWintext;
      yyleng_ptr = &yyRuWinleng;
      LC_tolower_tab = tolower_cp1251_tab;
    }
  else if (option.language == RUSSIAN_U8)
    {
      yyRuU8in = yyin;
      yyRuU8out = yyout;
      yylex = (int (*)(void))(yyRuU8lex);
      yytext_ptr = &yyRuU8text;
      yyleng_ptr = &yyRuU8leng;
      LC_tolower_tab = tolower_ascii_tab;
    }
  else
    {
      fprintf(stderr, "Wrong language!\n");
      exit(1);
    }
}

void
select_language (char *l_id)
{
  if ((! strcasecmp(l_id, "de")) ||
      (! strcasecmp(l_id, "german")))
    {
      option.language = GERMAN_L1;
    }
  else if ((! strcasecmp(l_id, "de-win")) ||
	   (! strcasecmp(l_id, "german-win-cp1252")))
    {
      option.language = GERMAN_WIN;
    }
  else if ((! strcasecmp(l_id, "de-u8")) ||
	   (! strcasecmp(l_id, "german-utf8")))
    {
      option.language = GERMAN_U8;
    }
  else if ((! strcasecmp(l_id, "en")) ||
	   (! strcasecmp(l_id, "english")))
    {
      option.language = ENGLISH_L1;
    }
  else if ((! strcasecmp(l_id, "en-win")) ||
	   (! strcasecmp(l_id, "english-win-cp1252")))
    {
      option.language = ENGLISH_WIN;
    }
  else if ((! strcasecmp(l_id, "en-u8")) ||
	   (! strcasecmp(l_id, "english-utf8")))
    {
      option.language = ENGLISH_U8;
    }
  else if ((! strcasecmp(l_id, "ru")) ||
	   (! strcasecmp(l_id, "russian")))
    {
      option.language = RUSSIAN_ISO5;
    }
  else if ((! strcasecmp(l_id, "ru-win")) ||
	   (! strcasecmp(l_id, "russian-win-cp1251")))
    {
      option.language = RUSSIAN_WIN;
    }
  else if ((! strcasecmp(l_id, "ru-u8")) ||
	   (! strcasecmp(l_id, "russian-utf8")))
    {
      option.language = RUSSIAN_U8;
    }
  else
    {
      fprintf(stderr, "Language \"%s\" not supported!\n", l_id);
      exit(1);
    }
}

