/*  -*- coding: utf-8; -*- */

/* TokenizeRu.l -- definitions for Russian */
/*                 iso-8859-5             */
/*                 cp1251                 */
/* run through a filter to discriminate charsets */

%{
#include <string.h>
#include "Tokenizer.h"
#include "TokenizerLexer.h"
%}

%option 8bit batch noyywrap

  /**** character classes ****/
LETTER_LAT_LC	([a-z]|ß|à|á|â|ã|ä|å|æ|ç|è|é|ê|ë|ì|í|î|ï|ð|ñ|ò|ó|ô|õ|ö|ø|ù|ú|û|ü|ý|þ|ÿ|ā|ă|ą|ć|ĉ|ċ|č|ď|đ|ē|ĕ|ė|ę|ě|ĝ|ğ|ġ|ģ|ĥ|ħ|ĩ|ī|ĭ|į|ı|ĵ|ķ|ĸ|ĺ|ļ|ľ|ł|ń|ņ|ň|ŋ|ō|ŏ|ő|ŕ|ŗ|ř|ś|ŝ|ş|š|ţ|ť|ŧ|ũ|ū|ŭ|ů|ű|ų|ŵ|ŷ|ź|ż|ž|ǆ|ǉ|ǌ|ǟ|ǡ|ǣ|ǥ|ǧ|ǩ|ǫ|ǭ|ǯ|ǰ|ǳ)
LETTER_LAT_UC	([A-Z]|À|Á|Â|Ã|Ä|Å|Æ|Ç|È|É|Ê|Ë|Ì|Í|Î|Ï|Ð|Ñ|Ò|Ó|Ô|Õ|Ö|Ø|Ù|Ú|Û|Ü|Ý|Þ|Ā|Ă|Ą|Ć|Ĉ|Ċ|Č|Ď|Đ|Ē|Ĕ|Ė|Ę|Ě|Ĝ|Ğ|Ġ|Ģ|Ĥ|Ħ|Ĩ|Ī|Ĭ|Į|İ|Ĵ|Ķ|Ĺ|Ļ|Ľ|Ł|Ń|Ņ|Ň|Ŋ|Ō|Ŏ|Ő|Ŕ|Ŗ|Ř|Ś|Ŝ|Ş|Š|Ţ|Ť|Ŧ|Ũ|Ū|Ŭ|Ů|Ű|Ų|Ŵ|Ŷ|Ÿ|Ź|Ż|Ž|Ǆ|Ǉ|Ǌ|Ǟ|Ǡ|Ǣ|Ǥ|Ǧ|Ǩ|Ǫ|Ǭ|Ǯ|Ǳ)
 /* iso-8859-5 and cp1251 have the same repertoire of cyrillic letters */
 /*LETTER_LAT    [A-Za-z]
LETTER_LAT    ({LETTER_LAT_LC}|{LETTER_LAT_UC})
LETTER_CYR_UC	(Ѐ|Ё|Ђ|Ѓ|Є|Ѕ|І|Ї|Ј|Љ|Њ|Ћ|Ќ|Ѝ|Ў|Џ|А|Б|В|Г|Д|Е|Ж|З|И|Й|К|Л|М|Н|О|П|Р|С|Т|У|Ф|Х|Ц|Ч|Ш|Щ|Ъ|Ы|Ь|Э|Ю|Я|Ѡ|Ѣ|Ѥ|Ѧ|Ѩ|Ѫ|Ѭ|Ѯ|Ѱ|Ѳ|Ѵ|Ѷ|Ѹ|Ѻ|Ѽ|Ѿ|Ҁ|Ҋ|Ҍ|Ҏ|Ґ|Ғ|Ҕ|Җ|Ҙ|Қ|Ҝ|Ҟ|Ҡ|Ң|Ҧ|Ҩ|Ҫ|Ҭ|Ү|Ұ|Ҳ|Ҷ|Ҹ|Һ|Ҽ|Ҿ|Ӏ|Ӂ|Ӄ|Ӆ|Ӈ|Ӊ|Ӌ|Ӎ|Ӑ|Ӓ|Ӗ|Ә|Ӛ|Ӝ|Ӟ|Ӡ|Ӣ|Ӥ|Ӧ|Ө|Ӫ|Ӭ|Ӯ|Ӱ|Ӳ|Ӵ|Ӷ|Ӹ|Ԁ|Ԃ|Ԅ|Ԇ|Ԉ|Ԋ|Ԍ|Ԏ)
LETTER_CYR_LC	(а|б|в|г|д|е|ж|з|и|й|к|л|м|н|о|п|р|с|т|у|ф|х|ц|ч|ш|щ|ъ|ы|ь|э|ю|я|ѐ|ё|ђ|ѓ|є|ѕ|і|ї|ј|љ|њ|ћ|ќ|ѝ|ў|џ|ѡ|ѣ|ѥ|ѧ|ѩ|ѫ|ѭ|ѯ|ѱ|ѳ|ѵ|ѷ|ѹ|ѻ|ѽ|ѿ|ҁ|ҋ|ҍ|ҏ|ґ|ғ|ҕ|җ|ҙ|қ|ҝ|ҟ|ҡ|ң|ҧ|ҩ|ҫ|ҭ|ү|ұ|ҳ|ҷ|ҹ|һ|ҽ|ҿ|ӂ|ӄ|ӆ|ӈ|ӊ|ӌ|ӎ|ӑ|ӓ|ӗ|ә|ӛ|ӝ|ӟ|ӡ|ӣ|ӥ|ӧ|ө|ӫ|ӭ|ӯ|ӱ|ӳ|ӵ|ӷ|ӹ|ԁ|ԃ|ԅ|ԇ|ԉ|ԋ|ԍ|ԏ|ᴫ)
LETTER_CYR    ({LETTER_CYR_LC}|{LETTER_CYR_UC})
LETTER    ({LETTER_LAT}|{LETTER_CYR})
LETTER_UC ({LETTER_LAT_UC}|{LETTER_CYR_UC})
LETTER_LC ({LETTER_LAT_LC}|{LETTER_CYR_LC})

CHAR   ([\xc0-\xdf].|[\xe0-\xef]..|[\xf0-\xf7]...|[\xf8-\xfb]....|[\xfc-\xfd].....|.)

DIGIT     [0-9]

HSPACE    [\x20\x09\xa0]
          /* normalize also non-breaking space */
VSPACE    [\x0a-\x0d]
NEWLINE   [\x0a\x0c\x0d]
SPACE     ({HSPACE}|{VSPACE})

 #define _EQUAL_SPACE_(c) (c=='\x20'||(c>='\x0a'&&c<='\x0d')||c=='\x09'||c=='\xa0')
 /* o.k. for iso-8859-5, cp1251 */

CONTR     [\x00-\x1f]
NO_SPACECONTR [^\x20\x09\x0a-\x0d\x00-\x1f]

SOFTHYPHEN '­'
HYPHEN    [-{SOFTHYPHEN]
 #define _EQUAL_HYPHEN_(c) (c == '-' || c == '\xad' /*soft*/)
 #define _EQUAL_REAL_HYPHEN_(c) (c == '-')


  /**** DEFINITIONS FOR END-OF-SENTENCE DETECTION ****/

EOS_PUNCT [.!?]
ALL_EXCEPT_EOS_PUNCT  [^.!?]
EOS_ADD   [\'\"\)\]\}>»›“”‘’]
          /* \xbb = '»' ; cp1251 only: '›' and [“”‘’]*/
BOS_ADD   [\(\[\{<\"\'`«„‚“”‘’]
          /* \xab = '«' ; cp1251 only: [„‚“”‘’] */
BOS_MARK  ({BOS_ADD}*({LETTER_UC}|{DIGIT}))

OTHER_PUNCT [,;·…†‡¶–—•]
          /* \xb7 = '·' (middle dot) ; other: cp1251 only */
PUNCT     ({EOS_PUNCT}|{EOS_ADD}|{BOS_ADD}|{OTHER_PUNCT})

  /**** and exceptions: points or other BOS_MARKs that (usually) are not EOS marks ****/

PS        (\.{SPACE}*)

DATE_DAY  (([012]?[0-9]|3[01]))
WORD_MONTH (([Яя]нв\.?|ар(ь|я))|[Фф]ев(\.?|рал(ь|я))|[Мм]ар(\.?|та?)|[Аа]пр(\.?|ел(ь|я))|[Мм]а(й|я)|[Ии]ю[нл](\.?|ь|я)|[Аа]вг(\.?|уста?)|[Сс]ен(т?\.?|тябр(ь|я))|[Оо]кт(\.?|ябр(ь|я))|[Нн]оя(\.?|бр(ь|я))|[Дд]ек(\.?|абр(ь|я)))
DATE_MONTH_ROMAN (i{1,3}|iv|vi{0,3}|ix|xi{0,2}|I{1,3}|IV|VI{0,3}|IX|XI{0,2})
DATE_MONTH_NUM (0?[1-9]|1[012])
DATE_MONTH ({WORD_MONTH}|{DATE_MONTH_NUM}\.|{DATE_MONTH_ROMAN}\.)
DATE_YEAR ([1-9][0-9]{0,3}|0[0-9])
DATE_YEAR_POSTCLASS ((до|пр(\.|ед))(н{PS}э|н{PS}ст){PS})
DATE  (({DATE_DAY}{PS}{DATE_MONTH}{SPACE}*{DATE_YEAR}({SPACE}*{DATE_YEAR_POSTCLASS})?)|({DATE_DAY}{PS}{DATE_MONTH})|({DATE_YEAR}{SPACE}*{DATE_YEAR_POSTCLASS}))

ABBR_WITH_POINT1      (Андр|Вопр|Вступ|Гл|Гос|Греч|Дет|Дж|Ед|Зав|Зам|И{PS}Д{PS}К|Избр|Изд|Иностр|Кн|Кр|Лит|Мол|Моск|Н{PS}С|Науч|Обл|Отеч|Пб|Пер|Печ|Полн{PS}собр|Посл|Предисл|Прим|Примеч|Р{PS}Х|Рец|Род|Рус|СПб|Сб|Св|См|См{PS}коммент|См{PS}прим|См{PS}примеч|Собр|Собр{PS}соч|Сов|Соч|Сп|Ср|Т{PS}е|Ук|Указ|Употр|Уч|Учен|Ф{PS}И{PS}О|Худ|Худож|Цит|Ч{PS}В|а|авт|амер|анат|англ|ант|ат|б|быв|бывш|в|в{PS}н|в{PS}н{PS}э|вв|вв{PS}н|вводн|вел|вин|возвр|вступ|вступ{PS}ст|г|г{PS}г|г{PS}н|г{PS}н{PS}э|гв|гг|где-н|гл|гл{PS}обр|гос|гр|греч|губ|д|дат|долл|др|е|евр|ед|ж{PS}-д|жел|жен|з|за|зав|зам|зап|знач|знач{PS}глаг|и|и{PS}о|изд|ирл|искаж|исп|ист|итал|к|к{PS}с|какие-н|каким-н|каких-н|какого-н|какое-н|какой-н|каком-н|какому-н|какую-н|канд{PS}филол|каф|кв|кг|кем-н|кесов|кл|км|кн|книжн|кого-н|кого-чего-н|кого-что-н|ком-н|ком-чем-н|комм|коммент|кому-н|кому-чему-н|коп|кто-н|куда-н)
ABBR_WITH_POINT2      (л|л{PS}ед|ласк|лат|лев|лимф|лит|м|м{PS}б|мед|мес|мест|мил|мин|мл|млн|млн{PS}долл|млн{PS}руб|млрд|млрд{PS}долл|млрд{PS}руб|мм|мн|моск|муз|н|н{PS}ст|н{PS}э|на|наб|наз|напр|нар|наст|наст{PS}собр|науч|нач|не|неопр|несов|ни|о|обл|однокр|опубл|отд|отеч|оч|п|пер|первонач|печ|пл|пог|подг|поел|полн|пор|порядк|посл|пр|правосл|предл|преимущ|прил|прим|примеч|прост|противоп|проч|р|разг|рег|ред|род|род{PS}мн|рт|руб|рус|русск|с|с{PS}-д|с{PS}-р|с{PS}С|с{PS}г|сб|св|сев|сек|сем|син|син{PS}Т|сл|см|см{PS}коммент|см{PS}прим|см{PS}примеч|соавт|собр|сов|совм|совр|совр{PS}амер|совр{PS}нем|совр{PS}сов|сокр|соотв|соч|союзн|спец|ср|средневек|ст|стар|стр|сущ|т|т{PS}-е|т{PS}д|т{PS}е|т{PS}к|т{PS}н|т{PS}п|т{PS}ч|тел|тов|трлн|тт|тыс|тыс{PS}долл|тыс{PS}кв|тыс{PS}руб|тыс{PS}фт|у|указ|ул|ум|уменьш|уменьш{PS}-ласк|унич|употр|устар|ф|ф{PS}ст|фн|фр|франц|фщ|ц|ц{PS}н|цит|ч|чего-н|чей-н|чел|чем-н|чему-н|что-н|чье-н|чьей-н|чьи-н|чьим-н|чьих-н|чью-н|швейц|шест|шотл|шт|э|экз|эл)
ABBR      (({LETTER_UC}|{ABBR_WITH_POINT1}|{ABBR_WITH_POINT2})\.)
 /* the abbreviations are literally (spaces may appear after a
 "intra-abbr." period): Андр. | Вопр. | Вступ. | Гл. | Гос. | Греч. |
 Дет. | Дж. | Ед. | Зав. | Зам. | И.Д.К. | Избр. | Изд. | Иностр. |
 Кн. | Кр. | Лит. | Мол. | Моск. | Н.С. | Науч. | Обл. | Отеч. | Пб. |
 Пер. | Печ. | Полн.собр. | Посл. | Предисл. | Прим. | Примеч. |
 Р.Х. | Рец. | Род. | Рус. | СПб. | Сб. | Св. | См. | См.коммент. |
 См.прим. | См.примеч. | Собр. | Собр.соч. | Сов. | Соч. | Сп. | Ср. |
 Т.е. | Ук. | Указ. | Употр. | Уч. | Учен. | Ф.И.О. | Худ. | Худож. |
 Цит. | Ч.В. | а. | авт. | амер. | анат. | англ. | ант. | ат. | б. |
 быв. | бывш. | в. | в.н. | в.н.э. | вв. | вв.н. | вводн. | вел. |
 вин. | возвр. | вступ. | вступ.ст. | г. | г.г. | г.н. | г.н.э. |
 гв. | гг. | где-н. | гл. | гл.обр. | гос. | гр. | греч. | губ. | д. |
 дат. | долл. | др. | е. | евр. | ед. | ж.-д. | жел. | жен. | з. |
 за. | зав. | зам. | зап. | знал. | знач. | знач.глаг. | и. | и.о. |
 изд. | ирл. | искаж. | исп. | ист. | итал. | к. | к.с. | какие-н. |
 каким-н. | каких-н. | какого-н. | какое-н. | какой-н. | каком-н. |
 какому-н. | какую-н. | канд.филол. | каф. | кв. | кг. | кем-н. |
 кесов. | кл. | км. | кн. | книжн. | кого-н. | кого-чего-н. |
 кого-что-н. | ком-н. | ком-чем-н. | комм. | коммент. | кому-н. |
 кому-чему-н. | коп. | кто-н. | куда-н. | л. | л.ед. | ласк. | лат. |
 лев. | лимф. | лит. | м. | м.б. | мед. | мес. | мест. | мил. | мин. |
 мл. | млн. | млн.долл. | млн.руб. | млрд. | млрд.долл. | млрд.руб. |
 мм. | мн. | моск. | муз. | н. | н.ст. | н.э. | на. | наб. | наз. |
 напр. | нар. | наст. | наст.собр. | науч. | нач. | неопр. | несов. |
 ни. | о. | обл. | однокр. | опубл. | отд. | отеч. | оч. | п. | пер. |
 первонач. | печ. | пл. | пог. | подг. | поел. | полн. | пор. |
 порядк. | посл. | пр. | правосл. | предл. | преимущ. | прил. |
 прим. | примеч. | прост. | противоп. | проч. | р. | разг. | рег. |
 ред. | род. | род.мн. | рт. | руб. | рус. | русск. | с. | с.-д. |
 с.-р. | с.С. | с.г. | сб. | св. | сев. | сек. | сем. | син. |
 син.Т. | сл. | см. | см.коммент. | см.прим. | см.примеч. | соавт. |
 собр. | сов. | совм. | совр. | совр.амер. | совр.нем. | совр.сов. |
 сокр. | соотв. | соч. | союзн. | спец. | ср. | средневек. | ст. |
 стар. | стр. | сущ. | т. | т.-е. | т.д. | т.е. | т.к. | т.н. | т.п. |
 т.ч. | тел. | то. | тов. | трлн. | тт. | тыс. | тыс.долл. | тыс.кв. |
 тыс.руб. | тыс.фт. | у. | указ. | ул. | ум. | уменьш. |
 уменьш.-ласк. | унич. | употр. | устар. | ф. | ф.ст. | фн. | фр. |
 франц. | фщ. | ц. | ц.н. | цит. | ч. | чего-н. | чей-н. | чел. |
 чем-н. | чему-н. | что-н. | чье-н. | чьей-н. | чьи-н. | чьим-н. |
 чьих-н. | чью-н. | швейц. | шест. | шотл. | шт. | э. | экз. | эл.
 */

  /**** DEFINITIONS OF TOKENS ****/

WORD      ({LETTER_LAT}+|{LETTER_CYR}+("-"{LETTER_CYR}+)*|{DIGIT}+"-"{LETTER_CYR}+)
          /* includes also words containing '-' (``дефис'') */
          /* and special for Russian inflected numbers: 1-ое, 3-ье, в 4-х томах */
          /*                     and words like 16-летнего, 20-летие   */

NUMBER    ({DIGIT}+)
FNUMBER    ({DIGIT}+([,\.]{DIGIT}+)?)

  /**** internet and e-mail adresses ****/
WWW_VALID  [A-Za-z0-9_-]
WWW_HOST   ({WWW_VALID}+(\.{WWW_VALID}+)+)
WWW_PROT   ((https?|ftps?|file|news):\/\/)
WWW_ADR    ({WWW_PROT}|www\.){WWW_HOST}(\/{NO_SPACECONTR}+({WWW_VALID}|[\/]))?
EMAIL_USER ({WWW_VALID}+(\.{WWW_VALID}+)*)
EMAIL      ((mailto:)?{EMAIL_USER}@{WWW_HOST})
WWW        ({WWW_ADR}|{EMAIL})


  /**** exceptions to hyphenated words, i.e. words including a hyphen            ****/
  /**** make sure that there is a {HP} in every word, or tokenizer will hang !!! ****/
HP         {HYPHEN}{HSPACE}*{NEWLINE}{HSPACE}*
 /* actual only dummy definitions: */
HYPH_LEX   abcywфкxwec{HP}abcywфкxwec
HYPH_WORDS abcywфкxwec{HP}abcywфкxwec
  /** yes it works, having a exclude-lexicon: the lines should not be too long **/
  /** but the scanners becomes very big (4 times) and about 3% slower with the lexicon abow **/
 /* HYPH_WORD ({HYPH_WORDS}|{HYPH_LEX}) */
  /** so we don't use it **/
HYPH_WORD {HYPH_WORDS}

  /* STATES used */
%s  contHyph  EOScontHyph  EOS  WWW  contHyphWWW  EOScontHyphWWW  EOSWWW
%x  testEOS noEOS

%%


 _TEST_IF_OPTIONS_SET_


 /**** hyphenated words: ****/
<contHyph,EOScontHyph,contHyphWWW,EOScontHyphWWW>{
{HYPH_WORD}                 { _UNPUT_COMBINED_BS_WORD_ }
{WORD}{SOFTHYPHEN}/{WORD}   { _UNPUT_WORD_WITHOUT_LAST_CHAR_ }
{WORD}{HYPHEN}{HSPACE}*{NEWLINE}{HSPACE}*/{LETTER_LC}   { _UNPUT_WORD_WITHOUT_HYPHEN_ }
}

 /* www adresses */
<WWW,contHyphWWW,EOScontHyphWWW,EOSWWW>{
{WWW}/{PUNCT}              return TOK_WWW;
 /* exclude ')' etc. at the end of an www adress */
{WWW}                      return TOK_WWW;
}

 /**** rules relevant only for EOS detection: ****/
<EOS,EOScontHyph,EOSWWW,EOScontHyphWWW>{
 /* exclude short snippets in parenthesis somewhere in the middle of sentence */
 /* (an expensive rule)                                        */
({WORD}|{NUMBER}){SPACE}+"("{ALL_EXCEPT_EOS_PUNCT}{1,40}{EOS_PUNCT}.{0,40}")" |
 /* exclude dates and selected abbreviations */
{DATE}                     |
{ABBR}                     { no_eos_length = (yyleng);
                             yyless(0);
			     BEGIN(noEOS);
                           }
 /* EOS only if EOS_PUNCT followed by space and uppercase letter */
 /* {EOS_PUNCT}/{EOS_PUNCT}    return TOK_OTHER; */
{EOS_PUNCT}+/{EOS_ADD}*{SPACE}+{BOS_MARK} {
                           yyless(0); BEGIN(testEOS); }

}

<testEOS>{
{EOS_PUNCT}                |
{EOS_ADD}                  return TOK_OTHER;
{SPACE}+/{BOS_MARK}        yyless(0); BEGIN(stateINITIAL); return TOK_EOS;
{CHAR}                     yyless(0); BEGIN(stateINITIAL); return TOK_EOS;
}

<noEOS>{
{WORD}                     test_no_eos_length(yyleng); return TOK_WORD;
{NUMBER}                   test_no_eos_length(yyleng); return TOK_NUMBER;
 /* noEOS are actually dates and abbreviations, but no floating point numbers */
{HSPACE}*{VSPACE}+{SPACE}* test_no_eos_length(yyleng); return TOK_VSPACE;
{SPACE}+                   test_no_eos_length(yyleng); return TOK_HSPACE;
{CHAR}                    test_no_eos_length(yyleng); return TOK_OTHER;
}


 /**** general rules: ****/
{WORD}                     return TOK_WORD;

{NUMBER}|{FNUMBER}         return TOK_NUMBER;

{HSPACE}*{VSPACE}+{SPACE}* return TOK_VSPACE; /* skip horizontal spaces         */
^{HSPACE}+                 ;                  /* at the begining or end of line */
{HSPACE}+                  return TOK_HSPACE;

{CONTR}+                   ;

{CHAR}                     return TOK_OTHER;


