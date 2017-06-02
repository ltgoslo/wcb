/*  -*- coding: utf-8; -*- */

/* TokenizeEN.l -- definitions for English */

%{
#include <string.h>
#include "Tokenizer.h"
#include "TokenizerLexer.h"
%}

%option 8bit batch noyywrap

  /**** character classes for iso-8859-1 (latin-1) ****/
  /**** and cp1252 (Windows) ****/
LETTER_UC [A-ZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ]
LETTER_LC [a-zßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ]
LETTER    ({LETTER_UC}|{LETTER_LC})

CHAR   .

DIGIT     [0-9]

HSPACE    [\x20\x09\xa0]
          /* normalize also non-breaking space */
VSPACE    [\x0a-\x0d]
NEWLINE   [\x0a\x0c\x0d]
SPACE     ({HSPACE}|{VSPACE})

 #define _EQUAL_SPACE_(c) (c=='\x20'||(c>='\x0a'&&c<='\x0d')||c=='\x09'||c=='\xa0')
 /* o.k. for iso-8859-1, cp1252 */

CONTR     [\x00-\x1f\x7f-\x9f]
NO_SPACECONTR [^\x20\x09\xa0\x0a-\x0d\x00-\x1f\x7f-\x9f]

SOFTHYPHEN \xad
HYPHEN    [-{SOFTHYPHEN]
 #define _EQUAL_HYPHEN_(c) (c == '-' || c == '\xad')
 #define _EQUAL_REAL_HYPHEN_(c) (c == '-')


  /**** DEFINITIONS FOR END-OF-SENTENCE DETECTION ****/

EOS_PUNCT [.!?]
ALL_EXCEPT_EOS_PUNCT  [^.!?]
EOS_ADD   [\'\"\)\]\}>«»]
          /* \xbb = '»' ; cp1252 only: '' and []*/
BOS_ADD   [\(\[\{<\"\'»«¡¿`]
          /* \xa1 = '¡', \xbf = '¿' */
          /* \xab = '«' ; cp1252 only: [] */
BOS_MARK  ({BOS_ADD}*({LETTER_UC}|{DIGIT}))
BOS_INDIC ({BOS_ADD}*((A(bout|c(cording|tually)|fter|l(most|so|though|l)|mong|n(other|[dy])|re|[nst])|B(e(caus|for)e|oth|ut|[ey])|Can|D(espite|id|o(es|n\'t)|uring|o)|E(ach|ve(ry|n))|F(i(nally|rst)|or|rom|urthermore)|H(ave|e(\'s|re|r)|is|ow(ever)?|e)|I(\'(ll|ve|m)|n(dee|stea)d|t\'?s|[fnst])|Just|L(ater|et|ike)|M(a(ny|ybe)|o(re(over)?|st)|uch|y)|N(e(ither|ver(theless)?|xt)|o(thing|[tw])|o)|O(n(ce|ly|e)|thers?|ur|ver|[fnr])|Perhaps|S(everal|he|ince|ome(t(hing|imes))?|till|uch|o)|T(h(at(\'s)?|e(ir|re(\'s|fore)?|se|[ny])|is|o(se|ugh)|rough|us)|oo|wo|o)|Un(der|til)|W(ell|h(at(ever)?|e(re|ther|n)|ile|y)|ith(in|out)?|ould|e)|Y(e[st]|ou(\'ll|r)?))({SPACE}|,)|(A|I|The){SPACE}+[a-z]+))
 /* Words which are typically at the beginning of a sentence
    (capitalized, of course): */
 /* a about according actually after all almost also although among an
    and another any are as at be because before both but by can
    despite did do does don't during each even every finally first for
    from furthermore have he her here he's his how however I if I'll
    I'm in indeed instead is it its it's I've just later let like many
    maybe more moreover most much my neither never nevertheless next
    no not nothing now of on once one only or other others our over
    perhaps several she since so some something sometimes still such
    that that's the their then there therefore there's these they this
    those though through thus to too two under until we well what
    whatever when where whether while why with within without would
    yes yet you you'll your */
 /* Avoid errors on (e.g., example taken from Brown corpus): 
    Supplementing the actual art are memorabilia -- correspondence,
    diaries, books from the artist's library, etc.  All belong to  <--- HERE
    the collection being given to Wilmington over a p eriod of years
    by Mrs. Sloan, who has cherished such revelator y items ever since
    she first studied with Sloan at the Art l Students League, New
    York, in the 1920's. */
 /* !!! Be cautious with «A», «I», «The», e.g. «Dpt. I, ...» :
        accepted only in combination with space and lowercase word
        behind. 
    !!! Make sure that BOS_INDIC is not recognized as prefix of another word! */
 /* smaller version for utf-8: */
BOS_INDIC_SMALL ({BOS_ADD}*((A(bout|fter|l(though|l)|mong|n(other|[d])|[nst])|B(e(caus|for)e|oth|ut|y)|D(on\'t|uring|o)|E(ach|ve(ry|n))|F(inally|or|rom)|H(ere?|is|ow(ever)?|e)|I(\'(ll|[m])|t[\']?s|[fnst])|Just|L(et|ike)|M(a(ny|ybe)|o(re(over)?|st)|y)|No[tw]?|O(n(ce|ly|e)|ther|ur|[fnr])|Perhaps|S(he|ince|ome(times)?|uch|o)|T(h(at(\'s)?|e(ir|re|se|[ny])|is|o(se|ugh)|us)|wo|o)|Under|W(ell|h(at|e(re|n)|ile|y)|ith|e)|Y(et|ou))({SPACE}|,)|(A|I|The){SPACE}[a-z]))

OTHER_PUNCT [,;·]
          /* \xb7 = '·' (middle dot) ; other: cp1252 only */
PUNCT     ({EOS_PUNCT}|{EOS_ADD}|{BOS_ADD}|{OTHER_PUNCT})

  /**** and exceptions: points or other BOS_MARKs that (usually) are not EOS marks ****/

PS        (\.{SPACE}*)

DATE_DAY  (([012]?[0-9]|3[01])|1st|2nd|3rd|([4-9]|[12][0-9]|3[01])th)
WORD_MONTH ([Jj]an(\.?|uary)|[Ff]eb(\.?|ruary)|[Mm]ar(\.?|ch)|[Aa]pr(\.?|il)|[Mm]ay|[Jj]un(\.?|e)|[Jj]ul(\.?|y)|[Aa]ug(\.?|ust)|[Ss]ep(t?\.?|tember)|[Oo]ct(\.?|ober)|[Nn]ov(\.?|ember)|[Dd]ec(\.?|ember))
DATE_MONTH_ROMAN (i{1,3}|iv|vi{0,3}|ix|xi{0,2}|I{1,3}|IV|VI{0,3}|IX|XI{0,2})
DATE_MONTH_NUM (0?[1-9]|1[012])
DATE_MONTH ({WORD_MONTH}|{DATE_MONTH_ROMAN}(\.|{SPACE}))
DATE_YEAR ([1-9][0-9]{0,3}|0[0-9])
DATE_YEAR_POSTCLASS ([AB]{PS}[CP]{PS}(E{PS})?)
DATE (({DATE_DAY}({PS}|{SPACE}*){DATE_MONTH}{SPACE}*{DATE_YEAR}({SPACE}*{DATE_YEAR_POSTCLASS})?)|{DATE_MONTH}{SPACE}*{DATE_DAY}(,?{SPACE}*){DATE_YEAR}({SPACE}*{DATE_YEAR_POSTCLASS})?|({DATE_DAY}{PS}{DATE_MONTH})|({DATE_YEAR}{SPACE}*{DATE_YEAR_POSTCLASS}))
 /* dates 99-12-31 or 31/12/99 etc. include no EOS punctuation */

SUFFIX_WITH_POINT    (-?([Ss]tr))
ABBR_TITLES1 (Adj{PS}Assoc{PS}Prof|Adj{PS}Prof|Adm|Adms|A{PS}A|A{PS}B|A{PS}D{PS}C|A{PS}L{PS}B|A{PS}M|A{PS}Mus{PS}D|A{PS}R{PS}A|A{PS}R{PS}I{PS}B{PS}A|A{PS}R{PS}S{PS}A|Assoc{PS}Prof|Bart|B{PS}A|B{PS}Acc)
ABBR_TITLES2 (B{PS}A{PS}Econ|B{PS}A{PS}S|B{PS}A{PS}Sc|B{PS}Arch|B{PS}B{PS}A|B{PS}Ch|B{PS}Com|B{PS}Comm|B{PS}Comp|B{PS}CompSc|B{PS}C{PS}L|B{PS}CS|B{PS}D|B{PS}Des|B{PS}E|B{PS}Ec|B{PS}Ed|B{PS}Eng|B{PS}E{PS}S|B{PS}F{PS}A|B{PS}G{PS}S|B{PS}InfSci|B{PS}InfTech|B{PS}J|B{PS}Lang|B{PS}LL|B{PS}Math)
ABBR_TITLES3 (B{PS}M{PS}orM{PS}B|B{PS}Mus|B{PS}Pharm|B{PS}Phil|B{PS}P{PS}E|B{PS}P{PS}Ed|B{PS}Psych|B{PS}R{PS}E|B{PS}S|B{PS}Sc|B{PS}S{PS}B|B{PS}S{PS}E|B{PS}S{PS}E{PS}E|B{PS}S{PS}F|B{PS}S{PS}S{PS}E|B{PS}S{PS}W|B{PS}Tech|Brig|C|Capt|Capts|Cmdr|col|Col|Cols|Comdrs|Comm|Comms|C{PS}A|C{PS}A{PS}S|C{PS}B)
ABBR_TITLES4 (C{PS}E|C{PS}I{PS}E|C{PS}M|C{PS}M{PS}G|C{PS}S{PS}I|Crpl|Crpls|D{PS}A|D{PS}A{PS}|D{PS}Arts|D{PS}A{PS}S|D{PS}Arch|D{PS}B{PS}A|D{PS}C|D{PS}Chem|D{PS}C{PS}J|D{PS}C{PS}L|D{PS}C{PS}S|D{PS}Crim|D{PS}D|D{PS}D{PS}S|D{PS}Eng|D{PS}Env|D{PS}E{PS}D|D{PS}E{PS}Sc|D{PS}F|D{PS}F{PS}A|D{PS}G{PS}S|D{PS}H{PS}L|D{PS}H{PS}S|D{PS}I{PS}T|D{PS}Lit{PS}|Litt{PS}D|D{PS}Litt|D{PS}L{PS}S|D{PS}M|D{PS}Min)
ABBR_TITLES5 (D{PS}M{PS}A|D{PS}M{PS}D|D{PS}M{PS}E|D{PS}M{PS}L|D{PS}M{PS}M|D{PS}M{PS}Sc|D{PS}Mus|D{PS}N{PS}P|D{PS}N{PS}Sc|D{PS}O|D{PS}P{PS}A|D{PS}P{PS}E|D{PS}P{PS}M|D{PS}P{PS}S|D{PS}P{PS}T|D{PS}R|D{PS}Rec|D{PS}R{PS}E)
ABBR_TITLES6 (D{PS}Sc|D{PS}Sc{PS}D|D{PS}Sc{PS}H|D{PS}Sc{PS}V{PS}M|D{PS}S{PS}M|D{PS}S{PS}O|D{PS}S{PS}Sc|D{PS}S{PS}W|D{PS}Tech|D{PS}Univ|D{PS}V{PS}M|dr|Dr|Dr{PS}DES|Dr{PS}Eh|Dr{PS}h{PS}c|Dr{PS}iur|Dr{PS}med|Dr{PS}phil|Dr{PS}P{PS}H|Dr{PS}rer{PS}nat|Dr{PS}rer{PS}pol|Dr{PS}theol|Drs|Ebor|Ed{PS}D|EdS|Emer{PS}Prof|Eng{PS}D|F{PS}C{PS}S|F{PS}D|F{PS}F{PS}P{PS}S)
ABBR_TITLES7 (F{PS}G{PS}S|F{PS}K{PS}Q{PS}C{PS}P{PS}I|F{PS}L{PS}S|F{PS}M|F{PS}P{PS}S|F{PS}R{PS}C{PS}P|F{PS}R{PS}A{PS}S|F{PS}R{PS}C{PS}P{PS}E|F{PS}R{PS}C{PS}S|F{PS}R{PS}G{PS}S|F{PS}R{PS}Hist{PS}Soc|F{PS}R{PS}H{PS}S|F{PS}R{PS}I{PS}B{PS}A|F{PS}R{PS}S|F{PS}R{PS}S{PS}A|F{PS}R{PS}S{PS}E|F{PS}R{PS}S{PS}L|F{PS}S{PS}A|F{PS}S{PS}S|F{PS}Z{PS}S|gen|Gen|Gens)
ABBR_TITLES8 (gov|Gov|Govs|G{PS}C{PS}B|G{PS}C{PS}H|G{PS}C{PS}I{PS}E|G{PS}C{PS}M{PS}G|G{PS}C{PS}S{PS}I|G{PS}C{PS}V{PS}O|Hon|H{PS}H|H{PS}I{PS}H|H{PS}I{PS}M|H{PS}M|H{PS}R{PS}H|H{PS}S{PS}H|Ing|J|J{PS}C{PS}D|J{PS}D|J{PS}P|Jr|K{PS}C|K{PS}C{PS}B|K{PS}C{PS}I{PS}E|K{PS}C{PS}M{PS}G|K{PS}C{PS}S{PS}I|K{PS}C{PS}V{PS}O|K{PS}G|K{PS}P|K{PS}T)
ABBR_TITLES9 (Ll{PS}B|LL{PS}B|LL{PS}D|LL{PS}M|L{PS}A{PS}H|L{PS}C{PS}C|L{PS}C{PS}J|L{PS}J|L{PS}L{PS}A|L{PS}R{PS}C{PS}P|L{PS}R{PS}C{PS}S|L{PS}Sc{PS}D|L{PS}S{PS}A|lt|Lt|Lts|maj|Maj|Majs|messrs|Messrs|miss|Miss|M{PS}A|M{PS}A{PS}L{PS}S|M{PS}B|M{PS}C)
ABBR_TITLES10 (M{PS}D|M{PS}Div|M{PS}Inst{PS}C{PS}E|M{PS}P|M{PS}R|M{PS}R{PS}C{PS}P|M{PS}R{PS}C{PS}S|M{PS}R{PS}I{PS}A|M{PS}V{PS}O|mr|Mr|mrs|Mrs|ms|Ms|Mssrs|Mus{PS}B|Mus{PS}D|Mus{PS}Doc|N{PS}P|O{PS}D|O{PS}M|Pharm{PS}D|Ph{PS}D|P{PS}C|P{PS}P|P{PS}R{PS}A|Pres|prof|Prof|Prof{PS}h{PS}c|Psy{PS}D|R|Reg{PS}Prof|rep|Rep|reps|Reps)
ABBR_TITLES11 (Rev|Revs|Rh{PS}D|R{PS}A|R{PS}A{PS}M|R{PS}E|R{PS}\&I|R{PS}M|R{PS}N|Rtd|S|Sc{PS}D|Sc{PS}D{PS}E|Sec|Secs|sen|Sen|sens|Sens|sgt|Sgt|Sgts|S{PS}J{PS}D|S{PS}S{PS}C|S{PS}T{PS}D|S{PS}T{PS}P|Sr|St|Th{PS}D|V{PS}C|V{PS}G|V{PS}S|W{PS}S)
ABBR_TITLES ({ABBR_TITLES1}|{ABBR_TITLES2}|{ABBR_TITLES3}|{ABBR_TITLES4}|{ABBR_TITLES5}|{ABBR_TITLES6}|{ABBR_TITLES7}|{ABBR_TITLES8}|{ABBR_TITLES9}|{ABBR_TITLES10}|{ABBR_TITLES11})
ABBR_WITH_POINT1 (a|A|ac|acc|acct|act|AD|adm|admin|adv|Aeg{PS}S|aero|Aet|Aetat|Af|AH|al|Ala|Anon|App|A{PS}C|A{PS}C{PS}T|A{PS}D|A{PS}E{PS}I{PS}O{PS}U|A{PS}H|a{PS}m|A{PS}M|A{PS}M{PS}D{PS}G|A{PS}U{PS}C|A{PS}V|Ar|Arab|archip|Ariz|As|AS|Assn|astrol|Ath|Atl{PS}O|Atty|Aubr|Aug|Av|Ave|b|Babyl|bac|Bah|Bahr|Balls|ban|Bangla|bar|Barb|Bav|BC|Beds|Belg|Ber|Berks|bev|Bhut|bibl|biblio|biochem|biog|biogeog|biol|bldg|Bldg|Blvd|Bohem|Bol|boro|bot|Bots|bp|B{PS}C|B{PS}Lit|B{PS}Sc|B{PS}Sc{PS}Econ)
ABBR_WITH_POINT2 (B{PS}V{PS}M|Br|Braz|Brig|brig{PS}gen|Bros|Brun|Bucks|Bulg|Bur|Buru|bus|Byz|c|C|ca|Cal|Calif|Cap|Capt|cc|CE|Celt|cent|cf|Cf|ch|Ch|chan|chap|Ches|Chmn|Cir|climat|cm|Cmdr|co|Co|Col|colloq|Colo|Com|Conn|Corp|cp|C{PS}|c{PS}a{PS}d|c{PS}ft|c{PS}i{PS}f|C{PS}M{PS}S|C{PS}O{PS}D|c{PS}w{PS}o|Cr|Ct|cu|cub|cub{PS}ft|curt|cwt|Cyp|d|D|Dak|Dan|Dec|deg|Del|Den|dept|Dept|Derby|dia|dial|dir|Dist|Do|D{PS}C|D{PS}F|D{PS}G|D{PS}O{PS}M|d{PS}s|D{PS}V|dr|Dr|Drs|dwt)
ABBR_WITH_POINT3 (e|E|EC|ed|Ed|encyc|Eng|e{PS}g|E{PS}Ger|E{PS}\&O{PS}E|eq|Eq|eqn|eqns|Equal{PS}Guin|Est|Eth|Ex|f|F|Fahr|fam|Feb|fec|fed|fig|Fig|figs|Figs|Fin|fl|Fla|Fo|Fol|f{PS}a{PS}s|f{PS}o{PS}b|f{PS}o{PS}q|f{PS}o{PS}r|f{PS}o{PS}t|f{PS}o{PS}w|fr|Fr|ft|fur|g|G|Ga|Gab|gal|Gam|gen|Gen|geneal|genet|geog|geol|geom|geophys|Ger|Gib|Gk|Glos|gm|Goth|gov|Gov)
ABBR_WITH_POINT4 (govt|G{PS}P{PS}O|gr|Gr|gram|Gre|Green|Gren|Grev|gr{PS}wt|Gt{PS}Br|Guad|Guat|Guin|Guy|h|Hants|Haw|Heb|her|Here{PS}\&Worc|Herts|hhd|hist|HMS|Holl|Hon|Hond|hort|hp|H{PS}K|H{PS}M{PS}S|h{PS}p|h{PS}t|hr|hts|Humbs|Hung|Hwy|i|Ib|Ibid|Ice|Icel)
ABBR_WITH_POINT5 (Id|Ida|ie|iiat|Ill|illus|imp|in|Inc|incl|ind|Ind|Indon|Ind{PS}O|indus|Inf|inst|Inst|instru|internat|inv|i{PS}d|i{PS}e|I{PS}E|i{PS}h{PS}p|I{PS}H{PS}S|I{PS}M{PS}D{PS}G|I{PS}O{PS}U|i{PS}q|Irans|Ire|is|isl|isls|Isr|isth|It|j|Jam|Jan|Jas|Jor|journ|Jr|jur|k|Kamp|Kan|Kans|Kas|kc|Ken|kg|Kin|king|km|Kor|k{PS}o|k{PS}t{PS}l)
ABBR_WITH_POINT6 (Id|Ida|ie|iiat|Ill|illus|imp|in|Inc|incl|ind|Ind|Indon|Ind{PS}O|indus|Inf|inst|Inst|instru|internat|inv|i{PS}d|i{PS}e|I{PS}E|i{PS}h{PS}p|I{PS}H{PS}S|I{PS}M{PS}D{PS}G|I{PS}O{PS}U|i{PS}q|Irans|Ire|is|isl|isls|Isr|isth|It|j|Jam|Jan|Jas|Jor|journ|Jr|jur|k|Kamp|Kan|Kans|Kas|kc|Ken|kg|Kin|king|km|Kor|k{PS}o|k{PS}t{PS}l)
ABBR_WITH_POINT7 (k{PS}v|k{PS}w|Kuw|Ky|l|L|la|La|Lab|Lanes|lang|Lat|latl|Lat{PS}Am|law|lb|lbs|Leb|Lee{PS}Is|leg|Leic|Les|Lib|libn|lic{PS}cit|Liech|lieut|Lines|ling|lit|Lith|litho|LL|LL{PS}D|Lond|Long|Lon{PS}|l{PS}c|l{PS}p|L{PS}S|l{PS}t|Lt|Ltd|Lt{PS}-Col|Lt{PS}-Gen|Luxem|m|Maid{PS}Rep|Maj)
ABBR_WITH_POINT8 (Maj{PS}-Gen|Mam|Mar|Mass|mc|Md|ME|Mem|Messrs|met|Mex|Mfg|mg|MHG|mi|Mich|mil|min|minis|Minn|Miss|ml|mm|Mmes|mo|Mo|Mont|Mor|mos|m{PS}p{PS}h|Mr|mrs|Mrs|ms|MS|Msec|mss|MSS|Mt|Mts|mun|mv|myth|n|N|na|naut|nav|navig|Neb|nem{PS}con|Neth|Neth{PS}Ant|Nev|news|Nfd|nick|Nie|Nig|NL|no|No|Nor|Norf|Northants)
ABBR_WITH_POINT9 (Northum|nos|Notts|Nov|N{PS}Af|N{PS}Am|N{PS}B|N{PS}C|N{PS}Cal|n{PS}d|N{PS}D|N{PS}Dak|N{PS}G|N{PS}H|N{PS}Ire|N{PS}J|N{PS}Kor|N{PS}M|N{PS}Mex|n{PS}p|N{PS}S|N{PS}S{PS}W|N{PS}T|N{PS}Terr|N{PS}W{PS}|N{PS}Y|N{PS}Yorks|N{PS}Y{PS}C|N{PS}Z|Nt{PS}wt|nw|o|ob|obi|obs|Obs|oct|Oct|OE|of|OF|offi|OFris|OHG|Okla|okr|Olr|Ont|Op|O{PS}H{PS}M{PS}S|o{PS}r)
ABBR_WITH_POINT10 (O{PS}S|O{PS}S{PS}B|O{PS}T|Ore|org|orgs|OS|osteol|osteop|Oxon|oz|p|P|Pa|Pac{PS}O|paint|Pak|Pal|paleob|paleog|paleon|Pan|Pap{PS}N{PS}G|Par|pari|pass|path|penin|Penna|Per|perh|period|Pers|petrol|Pfc|Pg|pharm|Phil|philan|philol|philos)
ABBR_WITH_POINT11 (phot|Ph{PS}D|phys|physic|physiol|Pinx|pk|pl|plat|po|pol|Pol|pol{PS}sci|Poly|pop|Port|poss|pp|Pp|p{PS}a|p{PS}c|p{PS}d|P{PS}E{PS}I|p{PS}f{PS}c|p{PS}m|P{PS}m|P{PS}M|P{PS}O|p{PS}o{PS}d|P{PS}O{PS}O|p{PS}p|P{PS}P{PS}C|p{PS}pr|P{PS}R|P{PS}S|p{PS}t{PS}|p{PS}t{PS}o|P{PS}T{PS}O|pr|pref|preft)
ABBR_WITH_POINT12 (prelim|prep|pres|print|prob|prof|Prof|prop|Prop|Prot|pro{SPACE}tem|prov|prox|pr{PS}min|prs|pseud|psychol|pt|Pt|ptg|pub|publ|pvt|q|Q|Qld|q{PS}d|Q{PS}E{PS}D)
ABBR_WITH_POINT13 (Q{PS}E{PS}F|q{PS}s|q{PS}v|qr|qt|Qu|quant{PS}suff|Que|Queens|Qy|r|R|rd|Rd|ref|Ref|reg|reg{PS}tn|rel|rep|Rep|Reps|res|reserva|resid|rev|Rev|riv|ro|Rom|R{PS}I|R{PS}I{PS}P|r{PS}p{PS}m|r{PS}r|R{PS}R|R{PS}S{PS}V{PS}P|Rs|Rte|Rt{PS}Hon|Rul|Russ|Rw|ry|Ry|s|S|Sam|Sask|Saud{PS}Arab|sc|Scand|schol)
ABBR_WITH_POINT14 (Scot|Sc{PS}|scr|sculp|Sculp|sec|Sec|sei|sen|Sen|Sens|Sept|seq|seqq|Sey|sgt|Sha|Shak|Shrops|Sib|Sing|Skr|soc|sociol|Sol{PS}Is|Som|Somer|Sov|sp|Sp|Spec|sp{PS}gr|spr|sprs|S{PS}Af|S{PS}Am|S{PS}Austr|S{PS}C|S{PS}D|S{PS}Dak|S{PS}D{PS}U{PS}K|S{PS}F{PS}S{PS}R|S{PS}Glam|S{PS}J|S{PS}Kor)
ABBR_WITH_POINT15 (S{PS}L|S{PS}P{PS}C{PS}K|S{PS}P{PS}G|S{PS}S{PS}R|S{PS}T{PS}B|S{PS}T{PS}D|S{PS}T{PS}L|S{PS}Yorks|sq|sq{PS}ft|sqq|sqrt|Sr|ss|SS|st|St|Sta|Staffs|Stat|states|statis|Ste|StKitts|St-P{PS}\&M|St{PS}Ex|str|subj|Sud|Suff|Sum|supp|Supt|Sur|surg|Sw|Swaz|Swed|Switz|Syr|t|Tai|Tan|Tanz|Tas|tech|Tech|Tenn|Ter|terr)
ABBR_WITH_POINT16 (Tex|Thai|thea|theol|Tib|t{PS}o|trag|trib|trig|Tr{PS}and|Tun|Tur|Tuv|twp|typog|u|Ugan|UN|univ|Univ|U{PS}A{PS}E|U{PS}K|U{PS}S|U{PS}S{PS}A|U{PS}S{PS}S{PS}R|(Urug|v|Va|val|Van|var|vb{PS}n|Venez|vet|Vie|Viet|vil|Vir{PS}Is|viz|vol|Vol|v{PS}i|v{PS}t|v{PS}v|vs|Vs|Vt|w|W|Warw|Wash|Wilts|Wis|Wm|W{PS}Af|W{PS}Austr|W{PS}Ger|W{PS}Glam|W{PS}I|w{PS}l|W{PS}Mids|W{PS}Sam|W{PS}Susx|W{PS}Va)|W{PS}W|writ|Wyo|y|yd|Yem|Yok|yrs|Yugos|Zimb|zool|Zor)
ABBR_WITH_POINT ({ABBR_TITLES}|{ABBR_WITH_POINT1}|{ABBR_WITH_POINT2}|{ABBR_WITH_POINT3}|{ABBR_WITH_POINT4}|{ABBR_WITH_POINT5}|{ABBR_WITH_POINT6}|{ABBR_WITH_POINT7}|{ABBR_WITH_POINT8}|{ABBR_WITH_POINT9}|{ABBR_WITH_POINT10}|{ABBR_WITH_POINT11}|{ABBR_WITH_POINT12}|{ABBR_WITH_POINT13}|{ABBR_WITH_POINT14}|{ABBR_WITH_POINT15}|{ABBR_WITH_POINT16})
ABBR_WITHOUT_POINT      (T{PS}W{PS}A|C[oO]{PS}KG|Y(ahoo)?\!)
ABBR      ({ABBR_WITHOUT_POINT}|({LETTER_UC}|{WORD}{SUFFIX_WITH_POINT}|{ABBR_WITH_POINT})\.)
	   


  /**** DEFINITIONS OF TOKENS ****/

WORD      ({LETTER}+("-"{LETTER}+)*)
          /* includes also Binde-strich-woerter */

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
HYPH_PRFX  (self|one|high|non|well|half|three|low|anti|two|twenty|long|four|re|co|double|forty|out|thirty|ever|pre)
HYPH_SFFX  (up|class|time|year|century|day|five|hour|run|wide|haired|hand|one|out|two|four|level|long|made|old|six|state|three|war|action|conscious|dimensional|down|eyed|fifth|fold|foot|grade|in|inch|law|loving|man|minded|nine|owned) 
HYPH_WORD  ({WORD}{HP}{HYPH_SFFX}|{HYPH_PRFX}{HP}{WORD})

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
 /* exclude short snippets in parenthesis */
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

 /* if there is an abbreviation followed by things like 
    capitalized articles, prepositions and conjunctions, there is
    usually an EOS, e.g.  23 n. Chr. In diesem Jahr  */
({ABBR_WITH_POINT}\.)/{EOS_ADD}*{SPACE}+{BOS_INDIC} {
                           yyless(0);
                           no_eos_length = (yyleng-1); /* skip until the period
                                                          (stop immediately before):
                                                          it will be treated as
                                                          EOS-punctuation */
                           BEGIN(noEOS);
                           }

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
 /* noEOS are actually no floating point numbers */
{HSPACE}*{VSPACE}+{SPACE}* test_no_eos_length(yyleng); return TOK_VSPACE;
{SPACE}+                   test_no_eos_length(yyleng); return TOK_HSPACE;
{CHAR}                     test_no_eos_length(yyleng); return TOK_OTHER;
}


 /**** general rules: ****/
{WORD}                     return TOK_WORD;

{NUMBER}|{FNUMBER}         return TOK_NUMBER;

{HSPACE}*{VSPACE}+{SPACE}* return TOK_VSPACE; /* skip horizontal spaces         */
^{HSPACE}+                 ;                  /* at the begining or end of line */
{HSPACE}+                  return TOK_HSPACE;

{CONTR}+                   ;

{CHAR}                     return TOK_OTHER;

