/* TokenizerLexer.h -- definitions for language-specific lexers */

/* faked state for INITIAL according to options */
static unsigned int stateINITIAL;

static signed int no_eos_length; /* length of no-eos-string (abbreviation, date etc.) */

extern int* yyleng_ptr;

inline static void
test_no_eos_length ( int decrement )
{
  /* switches back to initial state (with EOS detection), 
     when end of no-eos-string reached */
  no_eos_length -= decrement;
  if ( no_eos_length <= 0 )
    BEGIN(stateINITIAL);
/*   fprintf(yyout, "<%d-%d=%d>", (no_eos_length+decrement), decrement, no_eos_length); */
}

/* for processing options fake initial state */
/* could not be a function, because it uses states defined by flex */
#define _TEST_IF_OPTIONS_SET_                                           \
  if (! option.set) {                                                   \
    if (option.hyphCont == TRUE) {                                      \
      if ((option.eos & 01) == TRUE)                                    \
        stateINITIAL = (option.www ? EOScontHyphWWW : EOScontHyph);     \
      else                                                              \
        stateINITIAL = (option.www ? contHyphWWW : contHyph);           \
    } else {                                                            \
      if ((option.eos & 01) == TRUE)                                    \
        stateINITIAL = (option.www ? EOSWWW : EOS);                     \
      else                                                              \
        stateINITIAL = (option.www ? WWW : INITIAL);                    \
    }                                                                   \
    option.set = TRUE;                                                  \
    BEGIN(stateINITIAL);                                                \
 }

/* macros for hyphenated words */
/* because there is no function to unput
   the prefix of yytext (like yyless() for
   a suffix), we must unput each character
   separately */
#define _UNPUT_WORD_WITHOUT_LAST_CHAR_           \
  /* unputs yytext without the last character */ \
  int i;                                         \
  char *yycopy = strdup(yytext_ptr);             \
  for( i = (*yyleng_ptr - 2); i >= 0; --i ) {    \
    unput( yycopy[i] );                          \
  }                                              \
  free(yycopy); 

#define _UNPUT_WORD_WITHOUT_HYPHEN_ \
  /* unputs yytext discarding all after the last (soft) hyphen */       \
  /* to be more concret: it deletes the spaces and newlines    */       \
  /* following the word. Whether the hyphen itself is removed  */       \
  /* depends on the option.printHyphen (-C).                   */       \
  int i;                                                                \
  int in_word = 0;                                                      \
  char *yycopy = strdup(yytext_ptr);                                    \
  for( i = (*yyleng_ptr - 1); i >= 0; --i ) {                           \
    if ( in_word )                                                      \
      unput( yycopy[i] );                                               \
    else if ( (option.printHyphen == TRUE) && (_EQUAL_REAL_HYPHEN_(yycopy[i])) ) \
      unput( yycopy[i] );                                               \
    if ( _EQUAL_HYPHEN_(yycopy[i]) )                                    \
      in_word = 1;                                                      \
  }                                                                     \
  free(yycopy);

#define _UNPUT_COMBINED_BS_WORD_                                        \
  /* removes all spaces from yytext and unputs it */                    \
  int i;                                                                \
  char *yycopy = strdup(yytext_ptr);                                    \
  for( i = (*yyleng_ptr - 1); i >= 0; --i ) {                           \
    /* _EQUAL_SPACE_(c) is defined for each language in the flex file */ \
    if ( ! (_EQUAL_SPACE_(yycopy[i])) ) {                               \
      unput( yycopy[i] );                                               \
    }                                                                   \
  }                                                                     \
  free(yycopy);
  
