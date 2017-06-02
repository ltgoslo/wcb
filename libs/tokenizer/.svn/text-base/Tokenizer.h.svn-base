/* Tokenizer.h -- definitions for tokenizer.c _and_ the language-specific lexers */


/* token ids */
enum { 
  NO_TOKEN = 0, /* don't use zero for tokens ! */
  TOK_HSPACE,
  TOK_VSPACE,
  TOK_NEWLINE,
  TOK_WORD,
  TOK_NUMBER,
  TOK_OTHER,
  TOK_EOS,
  TOK_DATE,
  TOK_COMPLEX,
  TOK_ABBR,
  TOK_WWW,
};

typedef unsigned int BOOL;
enum { FALSE = 0, TRUE = 1 };

struct option {
  /* don't use bit-maps: costs are 1% of time, saves almost no space */
  /* because option is frequently consulted in yylex */
  BOOL eos;                /* 0 = eos off, 1 = on (-S)*/
  unsigned int new_line_as_eos; /* 0 = off, 1 = on (-n), 2 = -N */
  BOOL parMode;            /* 0 = off, 1 = on (-p) */
  unsigned int outputMode; /* 0 = off, 1 = on (-s), 2 = -p, 3 = -P  */
  BOOL printSpace;         /* 0 = off, 1 = on (-n) */
  BOOL hyphCont;         
  BOOL printHyphen;      
  BOOL convCase;         
  BOOL www;              
  BOOL quiet;            
  BOOL set;                /* options set in Lexer (do it only once) */
  unsigned int language;
  char tokSep;
  char* eosmark;
} option;


