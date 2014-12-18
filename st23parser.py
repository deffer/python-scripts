import re
import os
import os.path
from collections import defaultdict

__author__ = 'IB82573'

st23dir = r'c:\dev\data\RUN_004_ST23'
st23dir1 = r'c:\dev\data\RUN_010_ST23'
pjoin = os.path.join
titlepat = re.compile(r'(?P<paragraph>\s*\(?[A-Zixvc0-9]+\)\s*)?(?P<title>.*)\:(?P<name>.*)')
subtitle = re.compile(r'(.*?)[^A-Za-z]+SEQ(?:UENCE)?[\s\.-_]*ID[\s\.-_]*NO[\s\.-_:]*(\d*)')

#SEQUENCE DESCRIPTION: ID NO: 15 -  (xi),
#SEQUENCE DESCRIPTION: M3-195.203 OR: SEQ ID NO: ? -  (xi),
#SEQUENCE DESCRIPTION: SEO ID NO -  (xi),
#SEQUENCE DESCRIPTION: SEQ ID N0: ? -  (xi),
#SEQUENCE DESCRIPTION: SEQ ID NO: ? -  (v),(iv),(ii),(vi),(ix),
#SEQUENCE DESCRIPTION: SEQ IS NO: ? -  (x),
#DESCRIPTION DE LA: SEQ ID NO: ? -  (xi),

#ANMELDETITEL -  (ii),

#INFORMATIONS POUR LA: SEQ ID NO: ? -  (2),
#INFORMATION ZU: SEQ ID NO: ? -  (2),
#INFORMATION FOR SEQUENCE IDENTIFICATION NUMBER: 42 -  (2),
#INFORMATION FOR INFORMATION FOR: SEQ ID NO: ? -  (2),
# (2 INFORMATION FOR: SEQ ID NO: ? -  <none>,
#1. INFORMATION FOR: SEQ ID NO: ?
#33(2) INFORMATION FOR: SEQ ID NO: ? -  <none>,
#ANGABEN ZU: SEQ ID NO: ? -  (2),

#FEATURE: (A) NAME/KEY -  (ix),
#FEATURE: OTHER -  (ix),
#FEATURES -  (iii),(iv),(ix),(E),<none>,

#ART DES FRAGMENTS -  (v),
#ART DES MOLEK?LS -  (ii),


#MOLECUIE TYPE -  (ii),
#MOLECULAR TYPE -  (ii),<none>,
#MOLECULE TYPE -  (ii),<none>,
#MOLECULE TYPE: -  (ii),
#MOLECULE TYPE: IL-1RA FULL LENGTH -  (ii),
#MOLECULE TYPE: OTHER NUCLEIC ACID -  (ii),
#MOLECULE TYPE: PROTEIN -  (ii),

#L?NGE

#NAME -  A),(A),<none>,
#NAME KEY -  (A),
#NAME/KEY -  (A),(C),(ix),<none>,
#NAME/KEY: CDS (B) LOCATION -  (A),
#NAME/KEY: NRP-1 -  (A),
#NAME/KEY: NRP-13 -  (A),
#NAME/KEY: RP-1 -  (A),
#NAME/SCHL?SSEL -  (A),
#: NAME -  (A),

#NOMBRE DE SEQUENCES -  (iii),
#ANZAHL DER SEQUENZEN -  (iii),
#TOTAL NUMBER OF SEQUENCES TO BE LISTED -  <none>,

#ORGANISM -  (A),<none>,
#ORGANISME -  (A),
#ORGANISMS -  (A),
#ORGANISMUS -  (A),

#SEQUENCE CHARACTERISITCS -  (1),
#SEQUENCE CHARACTERISTIQUES -  (i),
#SEQUENCE CHARACTERIZATION -  (i),
#CARACTERISTIQUES DE LA SEQUENCE -  (i),

# ???-------- OTHER INFORMATION -------- ????
#ALGEMEINE INFORMATION -  (1),
#ALLGEMEINE ANGABEN -  (1),

#POSITION IM GENOM -  (viii),
#POSITION IN GENOME -  (viii),
#SEQUENCE KIND -  (ii),

result=defaultdict(set)

def findTitles(fname: 'File name'):
    global titlepat
    with open(fname, encoding='cp850') as f:
        #print('Analyzing file: {}'.format(fname))
        for line in f:
            m = titlepat.match(line)
            if m:
               processLine(m)



def processLine(m):
    par='<none>'
    if 'paragraph' in m.groupdict() and m.group('paragraph'):
         par=m.group('paragraph').strip()

    title = m.group('title').strip().upper()
    sm = subtitle.match(title)
    if (sm):
        title=sm.group(1).strip()+': SEQ ID NO: ?'
    result[title].add(par)
    #print(title,' -  ', par)


def main():
    files = os.listdir(st23dir)
    for fname in files:
        findTitles(pjoin(st23dir, fname))

    files = os.listdir(st23dir1)
    for fname in files:
        findTitles(pjoin(st23dir1, fname))

    fo = open(r'c:\dev\data\test1.txt', 'w',encoding='cp850')
    for key in sorted(result):
        pars = list(result[key])
        sparts = ''
        for s in pars[0:5]:
            sparts += (s+',')
        #print(key,' -  ', sparts)
        fo.write(key+' -  '+ sparts+ '\n')
main()