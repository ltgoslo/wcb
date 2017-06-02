/*  -*- coding: utf-8; -*- */

/* TokenizeDe.l -- definitions for German */
/*                 iso-8859-1             */
/*                 cp1252                 */
/* run through a filter to discriminate charsets */

%{
#include <string.h>
#include "Tokenizer.h"
#include "TokenizerLexer.h"
%}

%option 8bit batch noyywrap

  /**** character classes for iso-8859-1 (latin-1) ****/
  /**** and cp1252 (Windows) ****/
  /**** and utf-8 ****/
LETTER_UC [A-ZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ]      /* ####filter: iso-8859-1#### */
LETTER_UC [A-ZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞŠŒŽŸ]  /* ####filter: cp1252#### */
LETTER_UC ([A-Z]|À|Á|Â|Ã|Ä|Å|Æ|Ç|È|É|Ê|Ë|Ì|Í|Î|Ï|Ð|Ñ|Ò|Ó|Ô|Õ|Ö|Ø|Ù|Ú|Û|Ü|Ý|Þ|Ě|Š|Č|Ř|Ž|Ů|Ł) /* ####filter: utf-8#### */
LETTER_LC [a-zßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ]    /* ####filter: iso-8859-1#### */
LETTER_LC [a-zßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿšœž] /* ####filter: cp1252#### */
LETTER_LC ([a-z]|ß|à|á|â|ã|ä|å|æ|ç|è|é|ê|ë|ì|í|î|ï|ð|ñ|ò|ó|ô|õ|ö|ø|ù|ú|û|ü|ý|þ|ÿ|ě|š|č|ř|ž|ů|ł) /* ####filter: utf-8#### */
LETTER    ({LETTER_UC}|{LETTER_LC})

CHAR   .    /* ####filter: iso-8859-1#### */
CHAR   .    /* ####filter: cp1252#### */
CHAR   ([\xc0-\xdf].|[\xe0-\xef]..|[\xf0-\xf7]...|[\xf8-\xfb]....|[\xfc-\xfd].....|.)  /* ####filter: utf-8#### */

DIGIT     [0-9]

HSPACE    [\x20\x09\xa0]  /* ####filter: iso-8859-1#### */
HSPACE    [\x20\x09\xa0]  /* ####filter: cp1252#### */
HSPACE    ([\x20\x09]|\xc2\xa0)  /* ####filter: utf-8#### */
          /* normalize also non-breaking space */
VSPACE    [\x0a-\x0d]
NEWLINE   [\x0a\x0c\x0d]
SPACE     ({HSPACE}|{VSPACE})

 #define _EQUAL_SPACE_(c) (c=='\x20'||(c>='\x0a'&&c<='\x0d')||c=='\x09'||c=='\xa0')
 /* o.k. for iso-8859-1, cp1252 */

CONTR     [\x00-\x1f\x7f-\x9f] /* ####filter: iso-8859-1#### */
CONTR     [\x00-\x1f]          /* ####filter: cp1252#### */
CONTR     [\x00-\x1f]          /* ####filter: utf-8#### */
NO_SPACECONTR [^\x20\x09\xa0\x0a-\x0d\x00-\x1f\x7f-\x9f] /* ####filter: iso-8859-1#### */
NO_SPACECONTR [^\x20\x09\xa0\x0a-\x0d\x00-\x1f]          /* ####filter: cp1252#### */
NO_SPACECONTR [^\x20\x09\x0a-\x0d\x00-\x1f]              /* ####filter: utf-8#### */

SOFTHYPHEN \xad
HYPHEN    [-{SOFTHYPHEN]
 #define _EQUAL_HYPHEN_(c) (c == '-' || c == '\xad')
 #define _EQUAL_REAL_HYPHEN_(c) (c == '-')


  /**** DEFINITIONS FOR END-OF-SENTENCE DETECTION ****/

EOS_PUNCT [.!?]
 #define _IS_EOS_PUNCT_(c) (c == '.' || c == '!' || c == '?')
ALL_EXCEPT_EOS_PUNCT  [^.!?]
EOS_ADD   [\'\"\)\]\}>«»]         /* ####filter: iso-8859-1#### */
EOS_ADD   [\'\"\)\]\}>«»‹›“”‘’]  /* ####filter: cp1252#### */
EOS_ADD   ([\'\"\)\]\}>]|«|»|‹|›|“|”|‘|’)  /* ####filter: utf-8#### */
          /* \xbb = '»' ; cp1252 only: '›' and [“”‘’]*/
BOS_ADD   [\(\[\{<\"\'`»«¡¿]          /* ####filter: iso-8859-1#### */
BOS_ADD   [\(\[\{<\"\'`»«›‹„‚“”‘’¡¿] /* ####filter: cp1252#### */
BOS_ADD   ([\(\[\{<\"\'`]|»|«|›|‹|„|‚|“|”|‘|’|¡|¿) /* ####filter: utf-8#### */
          /* \xa1 = '¡', \xbf = '¿' */
          /* \xab = '«' ; cp1252 only: [„‚“”‘’] */
BOS_MARK  ({BOS_ADD}*({LETTER_UC}|{DIGIT}))
BOS_INDIC ({BOS_ADD}*((D(as|e[mnrs]|ie(se[mnrs]?|[s])?)|(Jene|Welche)[mnrs]?)|(A(ls|n(hand|s)|u(fs|ßer|[fs])|[bmn])|B(eim?|is)|D(a(mit|ss|ß)|e(nn|ren)|urchs?)|E(ntweder|s)|Für|Gegen|H(i(er|nter))|Ins?|Je|Mit|N(ach|eben)|O(b(wohl)?|der|hne)|S(eit|owohl|tatt)|U(m|nd)|Vo[mnr]|We(gen|il)|Zu[mr]|Über|À)){SPACE})
 /* Words which are typically at the beginning of a sentence (capitalized, of course): */
 /* der den das des die dem der deren den das des die dem dies dieses diese diesen diesem dieser dies dieses diese diesen diesem dieser es jenes jene jenen jenem jener welches welchem welche welchen welcher */
 /* à ab als am an anhand ans auf aufs aus außer bei beim bis damit dass daß denn durch durchs entweder für gegen hier hinter in ins je mit nach neben ob obwohl der ohne seit sowohl statt über um und vom von vor wegen weil zum zur */
 /* Make sure that BOS_INDIC is not recognized as prefix of another word!  */

OTHER_PUNCT [,;·]         /* ####filter: iso-8859-1#### */
OTHER_PUNCT [,;·…†‡¶–—] /* ####filter: cp1252#### */
OTHER_PUNCT [,;]          /* ####filter: utf-8#### */
          /* \xb7 = '·' (middle dot) ; other: cp1252 only */
PUNCT     ({EOS_PUNCT}|{EOS_ADD}|{BOS_ADD}|{OTHER_PUNCT})

  /**** and exceptions: points or other BOS_MARKs that (usually) are not EOS marks ****/

PS        (\.{SPACE}*)

ROMAN_NUMBER_UC_M (M{1,2})
ROMAN_NUMBER_UC_C (C{1,3}|CD|DC{1,3}|CM)
ROMAN_NUMBER_UC_X (X{1,3}|XL|LX{1,3}|XC)
ROMAN_NUMBER_UC_I (I{1,3}|IV|VI{1,3}|IX)
ROMAN_NUMBER_UC ({ROMAN_NUMBER_UC_M}({ROMAN_NUMBER_UC_C})?({ROMAN_NUMBER_UC_X})?({ROMAN_NUMBER_UC_I})?|{ROMAN_NUMBER_UC_C}({ROMAN_NUMBER_UC_X})?({ROMAN_NUMBER_UC_I})?|{ROMAN_NUMBER_UC_X}({ROMAN_NUMBER_UC_I})?|{ROMAN_NUMBER_UC_I})
ROMAN_NUMBER_LC_M (m{1,2})
ROMAN_NUMBER_LC_C (c{1,3}|cd|dc{1,3}|cm)
ROMAN_NUMBER_LC_X (x{1,3}|xl|lx{1,3}|xc)
ROMAN_NUMBER_LC_I (i{1,3}|iv|vi{1,3}|ix)
ROMAN_NUMBER_LC ({ROMAN_NUMBER_LC_M}({ROMAN_NUMBER_LC_C})?({ROMAN_NUMBER_LC_X})?({ROMAN_NUMBER_LC_I})?|{ROMAN_NUMBER_LC_C}({ROMAN_NUMBER_LC_X})?({ROMAN_NUMBER_LC_I})?|{ROMAN_NUMBER_LC_X}({ROMAN_NUMBER_LC_I})?|{ROMAN_NUMBER_LC_I})
ROMAN_NUMBER ({ROMAN_NUMBER_UC}|{ROMAN_NUMBER_LC})

ORDINAL   (({DIGIT}{1,3}|{ROMAN_NUMBER})\.)

DATE_DAY  (([012]?[0-9]|3[01]))
WORD_MONTH (Jan(\.?|uar)|Feb(r?\.?|ruar)|Mär(\.?|z)|Apr(\.?|il)|Mai|Jun(\.?|i)|Jul(\.?|i)|Aug(\.?|ust)|Sep(t?\.?|tember)|Okt(\.?|ober)|Nov(\.?|ember)|Dez(\.?|ember))
DATE_MONTH_ROMAN (i{1,3}|iv|vi{0,3}|ix|xi{0,2}|I{1,3}|IV|VI{0,3}|IX|XI{0,2})
DATE_MONTH_NUM (0?[1-9]|1[012])
DATE_MONTH ({WORD_MONTH}|{DATE_MONTH_NUM}\.|{DATE_MONTH_ROMAN}\.)
DATE_YEAR ([1-9][0-9]{0,3}|0[0-9]|{ROMAN_NUMBER})
DATE_YEAR_POSTCLASS (([vn]{PS}(Chr|u{PS}Z)|B{PS}P)\.)
DATE_QUART ([1-4]{PS}Quar(t?\.|tal)({SPACE}*{DATE_YEAR})?)
DATE_CENT  ({ORDINAL}{SPACE}*(Jahr(hundert|tausend)[s]?|(Jh|Jt)\.))
DATE  (({DATE_DAY}{PS}{DATE_MONTH}{SPACE}*{DATE_YEAR}({SPACE}*{DATE_YEAR_POSTCLASS})?)|({DATE_DAY}{PS}{DATE_MONTH})|({DATE_YEAR}{SPACE}*{DATE_YEAR_POSTCLASS})|{DATE_QUART}|{DATE_CENT})

ABBR_WITH_POINT      (A(b(zgl|[bst])|llg(em)?|m(er(ikan)?|tl)|n(schl|[hklm])|pp|r(ab|t)|ufl|[dz])|B(de|e(il|s({PS}G|t{PS}-{SPACE}*N|G)r|tr|[sz])|osn|rit|sd|ulgar|z(gl|w)|[dw])|Ca(nd)?|D(gl|i(p({PS}-{SPACE}*In[fg]|l{PS}(In[fg]|-{SPACE}*In[fg])|l)|[pr])|oz|r{PS}([Jj]ur|med|phil|rer{PS}nat|theol)|än|[rt])|E(hem|i(dg|gtl|nschl)|n(gl|tspr)|rb|stn|vtl|x[kp]l|[dv])|F(am|i(nn|g)|o(lg|rts)|r(anz|[lz])|[afr])|G(e(br|gr|s(ch|t)|[bkswz])|gfs?|riech|r)|H(ann|ebr|ins|oll(änd)?|r(sg|n)|[gr])|I(n(cl|kl|[cfgh])|sländ|tal)|J(hrl|ur)|K(a(th|ufm|p)|f[mz]|roat|to|l)|L(f(rg|[dg])|t[dg]|uth|t)|M(ax|dl|ech|i(ll|tw|[no])|od|r[ds]|tl|öbl|[rs])|N(orweg|äml|[or])|O(bb|ffiz|rth|d)|P(ers|fd|kt|o(ln|rtug)|pa|r(iv{PS}(-{SPACE}*)?Doz|o[fv])|[lp])|Qualif|R(e(g{PS}-{SPACE}*Bez|sp|[lp])|uss|öm|[dk])|S(chwed|erb|lowen|pan|t(ud|ädt|[er])|t)|T(ab|el|gl|schech|ägl|ürk)|Ungar|V(er(g({PS})?Gr|[fhlw])|glb?|o(r[ms]|l))|W(dh(lg)?|hg|z)|Z({PS}B|eitgen|t(schr|g)|u(zgl|[rs])|zgl|[iw])|a({PS}[do]|bzgl|llg(em)?|m(er(ikan)?|tl)|nschl|rab|d)|b(e(il|s)|osn|rit|sd|ulgar|z(gl|w))|ca(nd)?|d({PS}[hi]|gl|än|t)|e({PS}[Vh]|hem|i(dg|gtl|nschl)|n(gl|tspr)|rb|stn|vtl|xkl|[dv])|f(i(nn|g)|olg|r(an)?z|[fr])|g(e(gr|s(ch|t)|[bksz])|gfs?|riech|r)|h({PS}c|ebr|ins|oll(änd)?|rsg|g)|i({PS}(allg|[ADVbd])|n[ck]l|sländ|tal)|j(hrl|ur)|k(a(th|ufm)|fm|roat)|l(fd|td|uth|t)|m({PS}[EW]|ax|dl|ech|in|od|tl|öbl)|n(orweg|äml)|o({PS}[dgä]|ffiz|rth|d)|p({PS}A(dr)?|ers|o(ln|rtug)|pa|p)|qualif|r({PS}-{SPACE}*k|e(r{PS}nat|sp)|uss|öm|[dk])|s({PS}u|chwed|erb|lowen|pan|t(ud|ädt))|t(ab|gl|schech|ägl|ürk)|u({PS}[ad]|ngar)|v(er[hw]|glb?|orm)|z({PS}(Hd|Zt|[BHTZb])|eitgen|u(zgl|[rs])|zgl|w)|(Ö|ö)sterr|{LETTER})
ABBR_WITHOUT_POINT      (C[oO]{PS}KG|Y(ahoo)?\!)
 /* the abbreviations are literally:
  a.      an/am
  Abb.	Abbildung
  Abs.	Absatz
  Abt.          Abteilung
  abzgl.	abzüglich
  a.d.   an der: Freising an der Isar
  ad.   an der: Freising an der Isar
  allg.  allgemein
  allgem.  allgemein
  amer.	amerikanisch
  amerikan.	amerikanisch
  amtl.	amtlich
  Anh.	Anhang
  Ank.	Ankunft
  Anl.	Anlage
  Anm.	Anmerkung
  anschl.	anschließend
  a.o.	außerordentlicher
  App.	Apparat
  arab.	arabisch
  Art.	Artikel
  Aufl.	Auflage
  Az.	Aktenzeichen
  b.	bei
  Bd.	Band
  Bde.	Bände
  beil.	beiliegend
  bes.	besonders
  Bes.Gr.        Besoldungsgruppe
  BesGr.        Besoldungsgruppe
  Best.-Nr.	Bestellnummer
  Betr.	Betreff
  Bez.	Bezeichnung
  Bez.	Bezirk
  bosn.	bosnisch
  brit.	britisch
  bsd.	besonders
  bulgar.	bulgarisch
  Bw.	Bundeswehr
  bzgl.	bezüglich
  bzw.	beziehungsweise
  ca.	circa
  cand.	Kandidat
  C[oO].KG	Co. KG
  dän.	dänisch
  d.      der/die/das
  dgl.	dergleichen, desgleichen
  d.h.	das heißt
  d.i.	das ist
  Dip.	Diplom
  Dip.-Inf.	Diplominformatiker
  Dip.-Ing.	Diplomingenieur
  Dipl.	Diplom
  Dipl.-Inf.	Diplominformatiker
  Dipl.Inf.	Diplominformatiker
  Dipl.-Ing.	Diplomingenieur
  Dipl.Ing.	Diplomingenieur
  Dir.	Direktion
  Dir.	Direktor
  Doz.	Dozent
  Dr.	Doktor
  Dr.[Jj]ur.	Doktor der Rechte
  Dr.med.	Doktor der Medizin
  Dr.phil.	Doktor der Philosophie
  Dr.rer.nat.	Doktor der Naturwissenschaften
  Dr.theol.	Doktor der Theologie
  dt.	deutsch
  Ed.	Edition, Ausgabe
  ed.	hat herausgegeben
  e.h.	ehrenhalber
  ehem.	ehemals
  eidg.	eidgenössisch
  eigtl.	eigentlich
  einschl.	einschließlich/einschlägig
  engl.	englisch
  entspr.	entsprechend
  erb.	erbaut
  estn.	estnisch
  e.V.          eingetragener Verein
  ev.	Evangelisch
  evtl.	Eventuell
  exkl.	Exklusive
  Expl.	Exemplar
  Fa.	Firma
  Fam.	Familie
  ff.	folgende
  f.	folgend
  Fig.	Figur
  fig.	figurativ
  finn.	finnisch
  folg.	Folgend
  Forts.	Fortsetzung
  franz.	französisch
  fr.	französisch
  Fr.	Frau
  Frl.	Fräulein
  frz.	französisch
  frz.	Französisch
  geb.	geboren, geborene
  geb.	gebunden
  Gebr.	Gebrüder
  gegr.	Gegründet
  gek.	Gekürzt
  gesch.	geschieden/geschützt
  Ges.	Gesellschaft/Gesetz
  ges.	gesetzlich
  gest.	gestorben
  Gew.	Gewicht
  gez.	Gezeichnet
  ggf.	gegebenenfalls
  ggfs.	gegebenenfalls
  gr.	griechisch
  griech.	griechisch
  Hann. Münden	Hannoversch Münden
  h.c.	ehrenhalber
  hebr.	hebräisch
  Hg.	Herausgeber
  hg.	herausgegeben
  hins.	Hinsichtlich
  holländ.	holländisch
  holl.	holländisch
  Hr.	Herr
  Hrn.	Herrn
  Hrsg.	Herausgeber
  hrsg.	herausgegeben
  i.A.	im Auftrag
  i.allg.	im allgemeinen
  i.b.	im besonderen
  i.D.	im Dienst/im Durchschnitt
  i.d.   in der
  i.      in/im
  Inc.    Incorporated
  incl.	Inklusive
  Inf.	Informatiker
  Ing.	Ingenieur
  Inh.	Inhaber
  Inh.	Inhalt
  inkl.	Inklusive
  isländ.	isländisch
  ital.	italienisch
  i.V.	in Vertretung/in Vorbereitung
  jhrl.	Jährlich
  jur.	juristisch
  Kap.	Kapitel
  kath.	Katholisch
  kaufm.        kaufmännisch
  Kfm.	Kaufmann
  kfm.        kaufmännisch
  kfm.	Kaufmännisch
  Kfz.	Kraftfahrzeug
  Kl.	Klasse
  kroat.	kroatisch
  Kto.	Konto
  lfd.	laufend
  Lfg.	Lieferung
  Lfrg.	Lieferung
  l.	links
  ltd.	leitend
  Ltg.	Leitung
  lt.	laut
  Lt.	laut
  luth.	lutherisch
  max.	maximal
  mdl.	mündlich
  mech.   mechanisch
  m.E.	meines Erachtens
  Mill.	Million
  Min.	Minute
  min.	Minute/minimal
  Mio.	Million
  Mitw.	Mitwirkung
  möbl.	möbliert
  mod.	modern
  Mrd.	Milliarde
  Mr.	Mister
  Mrs.	Mistress
  Ms.	Misses
  mtl.	monatlich
  m.W.	meines Wissens
  näml.	nämlich
  n.	nach
  No.	Nummer
  norweg.	norwegisch
  Nr.	Nummer
  o.ä.    oder ähnliche
  o.d.   ob der
  Obb.  Oberbayern
  od.	oder
  offiz.	offiziell
  o.g.          oben genannt
  o.      ob/oben/oder/ohne
  orth.	orthodox
  österr.	österreichisch
  p.Adr.	per Adresse
  p.A.	per Adresse
  pers.	persönlich
  Pfd.	Pfund
  Pkt.	Punkt
  Pl.	Platz
  poln.	polnisch
  portug.	portugiesisch
  ppa.	per Prokura
  pp.	per Prokura
  Priv.-Doz.	Privatdozent
  Priv.Doz.	Privatdozent
  Prof.	Professor
  Prov.   Provinz
  qualif.       qualifiziert
  rd.	rund
  Reg.-Bez.	Regierungsbezirk
  Rel.	Religion
  Rep.	Republik
  rer.nat.	Naturwissenschaften	
  resp.	respektive
  r.-k.	römisch-katholisch
  rk.	römisch-katholisch
  röm.	römisch
  r.	rechts
  russ.	russisch
  schwed.	schwedisch
  serb.	serbisch
  slowen.	slowenisch
  span.	spanisch
  s.	siehe
  städt.  städtisch
  Ste.     Sainte
  Str.	Straße
  St.     Sankt
  stud.	Student
  s.u.	siehe unten
  tab.    tabellarisch
  tägl.	täglich
  Tel.	Telefon
  tgl.	täglich
  tschech.	tschechisch
  türk.	türkisch
  u.a.	und andere/unter anderem
  u.d.   unter der
  ungar.	ungarisch
  u.	und
  u.      unter
  ü.      über
  Verf.	Verfasser
  Verg.Gr.        Vergütungsgruppe
  VergGr.        Vergütungsgruppe
  verh.	verheiratet
  Verl.	Verlag
  verw.	verwitwet
  vglb.   vergleichbar
  vgl.	vergleiche
  Vol.    volume/Band
  vorm.	vormittags/vormals
  Vors.	Vorsitzende
  V.	Vers
  Wdhlg.	Wiederholung
  Wdh.	Wiederholung
  Whg.	Wohnung
  Wz.	Warenzeichen/Wasserzeichen
  Yahoo!  Yahoo (Firmenname)
  Y!  Yahoo (Firmenname)
  z.b.	zum Beispiel
  z.B.	zum Beispiel
  Z.B.	zum Beispiel
  zeitgen.	zeitgenössisch
  z.Hd.	zu Händen
  z.H.	zu Händen
  Zi.	Zimmer/Ziffer
  Ztg.	Zeitung
  Ztschr.	Zeitschrift
  z.T.	zum Teil
  zur.	zurück
  zus.	zusammen
  zuzgl.	zuzüglich
  zw.	zwischen
  Z.	Zeile/Zahl
  zzgl.
  zzgl.	zuzüglich
  z.Zt.	zur Zeit
  z.	zu, zum, zur
  z.Z.	zur Zeit
 */ 
DOCTOR_ADD (agr|des|disc{PS}pol|e{PS}h|em|emer|habil|h{PS}c|iur|iur{PS}can|iur{PS}utr|med|med{PS}dent|med{PS}univ|med{PS}vet|mont|mult|nat{PS}techn|oec|oec{PS}publ|oec{PS}troph|paed|pharm|phil|phil{PS}fac{PS}theol|phil{PS}nat|rer{PS}agr|rer{PS}biol{PS}hum|rer{PS}biol{PS}vet|rer{PS}cam|rer{PS}comm|rer{PS}cult|rer{PS}cur|rer{PS}forest|rer{PS}hort|rer{PS}medic|rer{PS}merc|rer{PS}mil|rer{PS}mont|rer{PS}nat|rer{PS}oec|rer{PS}physiol|rer{PS}pol|rer{PS}publ|rer{PS}sec|rer{PS}silv|rer{PS}soc|rer{PS}soc{PS}oec|rer{PS}techn|sc|scient{PS}med|sc{PS}agr|sc{PS}hum|sc{PS}math|sc{PS}nat|sc{PS}pol|sc{PS}rer{PS}omn|techn|theol|troph)
DOCTORES   ((Dr|DDr|Dres|Dr-Ing|Dr{PS}-Ing|Ph{PS}?D)({PS}{DOCTOR_ADD})*)
SUFFIX_WITH_POINT    (-?([Ss]tr|[Pp]l))
ABBR  ({ABBR_WITHOUT_POINT}|({LETTER_UC}|{WORD}{SUFFIX_WITH_POINT}|{DOCTORES}|{ABBR_WITH_POINT})\.)




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
HYPH_LEX1 B{HP}to{HP}B|Mund{HP}zu{HP}Mund{HP}Propaganda|Stand{HP}by{HP}Betrieb|Ad{HP}hoc|vhs{HP}ed|Park{HP}and|Wohn{HP}und|Turn{HP}around|Fast{HP}food|halbe{HP}halbe|Aix{HP}en{HP}Provence|Port{HP}au{HP}Prince|[Ee]{HP}commerce|Park{HP}and{HP}Ride|Park{HP}and{HP}ride|Play{HP}off{HP}Runde|Podbielski{HP}allee|Duty{HP}free|Park{HP}and{HP}Ride{HP}Anlage|Park{HP}and{HP}ride{HP}Anlage|Geld{HP}zurück{HP}Garantie|Call{HP}a{HP}bike|Play{HP}off{HP}Viertelfinale|Just{HP}in{HP}time|schwarz{HP}rot{HP}goldene|t{HP}online|Varennes{HP}en{HP}Argonne|Laisser{HP}faire|Laissez{HP}faire|Joint{HP}venture|[Ee]{HP}mail{HP}Adresse|Dun{HP}sur{HP}Meuse|Musica{HP}viva{HP}Konzerte|Open{HP}air{HP}Konzerte|Fast{HP}food{HP}Kette|Tête{HP}à{HP}tête|Shareholder{HP}value|liberal{HP}konservative|HIV{HP}positive|Park{HP}and{HP}ride{HP}Plätze|Spin{HP}off|Play{HP}off|Masar{HP}i{HP}Scharif|Do{HP}it{HP}yourself|Best{HP}of|Kopf{HP}an{HP}Kopf|Rechts{HP}vor{HP}Links{HP}Regelung|Rechts{HP}vor{HP}links{HP}Regelung|Ad{HP}hoc{HP}Mitteilung|Mund{HP}zu{HP}Mund{HP}Beatmung|Tse{HP}tung|High{HP}tech|B{HP}to{HP}B{HP}Bereich|Business{HP}to{HP}Business{HP}Bereich|römisch{HP}katholisch|griechisch{HP}römisch|Sowohl{HP}als{HP}auch|BSE{HP}frei|Hesb{HP}i{HP}Islami|Tie{HP}break|Nacht{HP}a{HP}Rock|ruck{HP}zuck|x{HP}mal|heute{HP}journal|Open{HP}air{HP}Festival|Katz{HP}und{HP}Maus{HP}Spiel|Frage{HP}und{HP}Antwort{HP}Spiel|[Ee]{HP}mail|Call{HP}by{HP}Call|[acdefgh]{HP}moll|a{HP}moll|c{HP}moll|d{HP}moll|e{HP}moll|f{HP}moll|g{HP}moll|h{HP}moll|Swimming{HP}pool|Berg{HP}am{HP}Laim
HYPH_LEX2 Science{HP}fiction{HP}Film|Best{HP}of{HP}Programm|Shui{HP}bian|Unser{HP}aller{HP}Welt{HP}Laden|Einsendun{HP}gen|Park{HP}and{HP}Ride{HP}Anlagen|Ad{HP}hoc{HP}Mitteilungen|Au{HP}pair{HP}Mädchen|PS{HP}starken|Start{HP}up{HP}Unternehmen|Start{HP}up{HP}Firmen|schwarz{HP}rot{HP}goldenen|Kopf{HP}an{HP}Kopf{HP}Rennen|SPD{HP}internen|Sie{HP}und{HP}Er{HP}Turnen|Break{HP}even|bürgerlich{HP}konservativen|liberal{HP}konservativen|HIV{HP}positiven|Check{HP}in|sz{HP}magazin|Motoren{HP}und{HP}Turbinen{HP}Union|Science{HP}fiction|Nacht{HP}und{HP}Nebel{HP}Aktion|Taekwon{HP}do|Open{HP}air{HP}Kino|i{HP}camp|Shop{HP}in{HP}Shop|second{HP}hand{HP}shop|non{HP}stop|Make{HP}up|Check{HP}up|Pick{HP}up|Park{HP}up|Warm{HP}up|Start{HP}up|gegen{HP}über|Know{HP}how{HP}Transfer|Tour{HP}de{HP}France{HP}Sieger|Check{HP}in{HP}Schalter|Prêt{HP}à{HP}porter|süß{HP}sauer|Stop{HP}and{HP}go{HP}Verkehr|Open{HP}air|Au{HP}pair|sixty{HP}four|Rush{HP}hour|Chaux{HP}de{HP}Fonds|Joint{HP}ventures|Spin{HP}offs|Play{HP}offs|Déjà{HP}vu{HP}Erlebnis|Midlife{HP}crisis|vis{HP}a{HP}vis|[Vv]is{HP}à{HP}vis|[Ee]{HP}mails|Dot{HP}coms|Pick{HP}ups|Pin{HP}ups|Start{HP}ups|Internet{HP}Start{HP}ups|co{HP}stars|Open{HP}airs|Au{HP}pairs|Business{HP}to{HP}Business|vario{HP}press|RTL{HP}plus|[Ee]{HP}plus|Rendez{HP}vous|Know{HP}hows|Give{HP}aways|Arbeiter{HP}und{HP}Bauern{HP}Staat|Unser{HP}aller{HP}Welt|Pop{HP}art|Open{HP}air{HP}Konzert|mega{HP}out|Coming{HP}out|Ad{HP}hoc{HP}Publizität|Peter{HP}u|Port{HP}au|Déjà{HP}vu|Hann{HP}v|HIV{HP}positiv|n{HP}tv|Pay{HP}per{HP}View|Pay{HP}per{HP}view|Know{HP}how|Cash{HP}flow|d{HP}box|Stand{HP}by|[Ff]ifty{HP}fifty|bonn{HP}sequenz|Park{HP}and{HP}Ride{HP}Platz|Park{HP}and{HP}ride{HP}Platz
HYPH_LEX3 (rot{HP}gelb|blau{HP}gelb|schwarz{HP}gelb|neblig{HP}trüb|x{HP}beliebig|spanisch{HP}sprachig|L{HP}förmig|IRA{HP}nah|SPD{HP}nah|CDU{HP}nah|CSU{HP}nah|feucht{HP}fröhlich|politisch{HP}gesellschaftlich|technisch{HP}wissenschaftlich|mathematisch{HP}naturwissenschaftlich|[Öö]ffentlich{HP}rechtlich|nicht{HP}öffentlich|jüdisch{HP}christlich|west{HP}östlich|israelisch{HP}arabisch|saudi{HP}arabisch|bosnisch{HP}serbisch|schwul{HP}lesbisch|britisch{HP}indisch|christlich{HP}abendländisch|britisch{HP}niederländisch|deutsch{HP}niederländisch|türkisch{HP}kurdisch|christlich{HP}jüdisch|deutsch{HP}jüdisch|nicht{HP}jüdisch|asiatisch{HP}pazifisch|medizinisch{HP}psychologisch|mechanisch{HP}biologisch|baden{HP}württembergisch|bayerisch{HP}tschechisch|deutsch{HP}tschechisch|bayerisch{HP}österreichisch|deutsch{HP}österreichisch|türkisch{HP}irakisch|iranisch{HP}irakisch|deutsch{HP}tschechoslowakisch|deutsch{HP}türkisch|rhythmisch{HP}musikalisch|[Ll]iterarisch{HP}musikalisch|geistig{HP}moralisch|politisch{HP}moralisch|arabisch{HP}israelisch|palästinensisch{HP}israelisch|deutsch{HP}israelisch|anti{HP}israelisch|pro{HP}israelisch|deutsch{HP}englisch|römisch{HP}katholisch|nordrhein{HP}westfälisch|arabisch{HP}islamisch|radikal{HP}islamisch|biologisch{HP}dynamisch|tänzerisch{HP}rhythmisch|bosnisch{HP}muslimisch|sozio{HP}ökonomisch|griechisch{HP}römisch|kosovo{HP}albanisch|israelisch{HP}jordanisch|russisch{HP}aserbaidschanisch|tadschikisch{HP}afghanisch|US{HP}amerikanisch|australisch{HP}amerikanisch|japanisch{HP}amerikanisch|chinesisch{HP}amerikanisch|russisch{HP}amerikanisch|britisch{HP}amerikanisch|europäisch{HP}amerikanisch|deutsch{HP}amerikanisch|anti{HP}amerikanisch|anglo{HP}amerikanisch|afro{HP}amerikanisch|deutsch{HP}japanisch|irakisch{HP}iranisch|deutsch{HP}iranisch|pro{HP}iranisch|französisch{HP}italienisch|deutsch{HP}italienisch|gewerblich{HP}technisch)(e[rsnm]?)?
HYPH_LEX4 (wissenschaftlich{HP}technisch|naturwissenschaftlich{HP}technisch|medizinisch{HP}technisch|multi{HP}ethnisch|schleswig{HP}holsteinisch|serbisch{HP}montenegrinisch|sachsen{HP}anhaltinisch|[Dd]eutsch{HP}polnisch|slawisch{HP}mazedonisch|deutsch{HP}dänisch|nicht{HP}olympisch|österreichisch{HP}ungarisch|deutsch{HP}ungarisch|[Ee]vangelisch{HP}lutherisch|königlich{HP}bayerisch|schwedisch{HP}schweizerisch|deutsch{HP}schweizerisch|pro{HP}irisch|[Pp]olitisch{HP}historisch|israelisch{HP}syrisch|deutsch{HP}chinesisch|pro{HP}indonesisch|israelisch{HP}palästinensisch|jordanisch{HP}palästinensisch|amerikanisch{HP}russisch|deutsch{HP}russisch|pro{HP}russisch|britisch{HP}französisch|[Dd]eutsch{HP}französisch|serbisch{HP}kroatisch|muslimisch{HP}kroatisch|bosnisch{HP}kroatisch|freiheitlich{HP}demokratisch|christlich{HP}demokratisch|deutsch{HP}sowjetisch|historisch{HP}politisch|niederländisch{HP}britisch|amerikanisch{HP}britisch|deutsch{HP}britisch|pro{HP}britisch|historisch{HP}kritisch|euro{HP}atlantisch|klassisch{HP}romantisch|islamisch{HP}fundamentalistisch|marxistisch{HP}leninistisch|ex{HP}kommunistisch|rheinland{HP}pfälzisch|mecklenburg{HP}vorpommersch|französisch{HP}deutsch|[Dd]eutsch{HP}deutsch|christlich{HP}sozial|ökologisch{HP}sozial|psycho{HP}sozial|bürgerlich{HP}liberal|christlich{HP}liberal|sozial{HP}liberal|konservativ{HP}liberal|militärisch{HP}industriell|schaurig{HP}schön|Rot{HP}grün|[Rr]ot{HP}grün|rot{HP}grün|schwarz{HP}grün|x{HP}t|berühmt{HP}berüchtigt|EG{HP}weit|EU{HP}weit|[Gg]elb{HP}rot|grün{HP}rot|rot{HP}rot|schwarz{HP}rot|nicht{HP}behindert|SPD{HP}regiert|CDU{HP}regiert|CSU{HP}regiert|SPD{HP}dominiert|HIV{HP}infiziert|SPD{HP}geführt|US{HP}geführt|CDU{HP}geführt|CSU{HP}geführt|EDV{HP}gestützt|gelb{HP}blau|rot{HP}blau|[Ww]eiß{HP}blau|ultra{HP}orthodox|serbisch{HP}orthodox|griechisch{HP}orthodox|syrisch{HP}orthodox|russisch{HP}orthodox|gelb{HP}schwarz|rot{HP}schwarz|grün{HP}weiß|rot{HP}weiß|blau{HP}weiß|[Ss]chwarz{HP}weiß|schwarz{HP}weiß)(e[rsnm]?)?
HYPH_LEX ({HYPH_LEX1}|{HYPH_LEX2}|{HYPH_LEX3}|{HYPH_LEX4})
HYPH_WORDS  ({LETTER_UC}{LETTER}+({HP}{LETTER}+)*{HP}(Straße|Str.|Pl.|Ring|(S|(Musik|Haupt|Real|Sonder)s)chule|Gymnasiums?|Uni(versität)?|Kaserne|Museum))
  /** yes it works, having a exclude-lexicon: the lines should not be too long **/
  /** but the scanners becomes very big (4 times) and about 3% slower with the lexicon abow **/
 /* HYPH_WORD ({HYPH_WORDS}|{HYPH_LEX}) */
  /** so we don't use it **/
HYPH_WORD {HYPH_WORDS}

  /* STATES used */
%s  contHyph  EOScontHyph  EOS  WWW  contHyphWWW  EOScontHyphWWW  EOSWWW
%x  testEOS noEOS tokenizeOneToken

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
 /* exclude short snippets in parenthesis, esp. "(!)" or "(?)" */
 /* (an expensive rule)                                        */
({WORD}|{NUMBER}){SPACE}+"("({ALL_EXCEPT_EOS_PUNCT}{1,40}{EOS_PUNCT}.{0,40}|[!?]+)")" |
 /* exclude dates, ordinal numbers, and selected abbreviations */
{DATE}                     |
{ORDINAL}                  |
{ABBR}                     { no_eos_length = (yyleng);
                           /* fprintf(stderr,"noeos: %s\n", yytext); */
                             yyless(0);
			     BEGIN(noEOS);
                           }

 /* EOS only if EOS_PUNCT followed by space and uppercase letter */
 /* {EOS_PUNCT}/{EOS_PUNCT}    return TOK_OTHER; */
{EOS_PUNCT}+/{EOS_ADD}*{SPACE}+{BOS_MARK} {
                           /* fprintf(stderr,"eos: %s\n", yytext); */
                           yyless(0); BEGIN(testEOS); }

 /* if there is an abbreviation followed by things like 
    capitalized articles, prepositions and conjunctions, there is
    usually an EOS, e.g. „… 23 n. Chr. In diesem Jahr …“ */
({DATE}|{ORDINAL}|{ABBR})/{EOS_ADD}*{SPACE}+{BOS_INDIC}({SPACE}|[,]) {
                           /* test if last matched character is EOS-char: 
                              if yes: stop immediately before it. So it
                              (usually the period) will be treated as EOS-punctuation */
                           /* fprintf(stderr,"yes (%i): %s\n", yyleng, yytext); */
                           if (_IS_EOS_PUNCT_(yytext[(yyleng-1)]))
                              no_eos_length = (yyleng-1);
                           else
                              no_eos_length = (yyleng);
                           yyless(0);
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
{NUMBER}|{FNUMBER}         test_no_eos_length(yyleng); return TOK_NUMBER;
 /* noEOS are actually dates, ordinals, and abbreviations, but no floating point numbers */
{HSPACE}*{VSPACE}+{SPACE}* test_no_eos_length(yyleng); return TOK_VSPACE;
{SPACE}+                   test_no_eos_length(yyleng); return TOK_HSPACE;
{CHAR}                     test_no_eos_length(yyleng); return TOK_OTHER;
}

<tokenizeOneToken>{
{WORD}                     BEGIN(stateINITIAL); return TOK_WORD; 
{NUMBER}|{FNUMBER}         BEGIN(stateINITIAL); return TOK_NUMBER;
{CHAR}                     BEGIN(stateINITIAL); return TOK_OTHER;
}



 /**** general rules: ****/
{WORD}                     return TOK_WORD;

{NUMBER}|{FNUMBER}         return TOK_NUMBER;

{HSPACE}*{VSPACE}+{SPACE}* return TOK_VSPACE; /* skip horizontal spaces         */
^{HSPACE}+                 ;                  /* at the begining or end of line */
{HSPACE}+                  return TOK_HSPACE;

{CONTR}+                   ;

{CHAR}                     return TOK_OTHER;

