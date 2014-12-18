import re


emblFile = open('c:/Dowload/checks/US/embl_rel5.txt')
usaFile = open('c:/Dowload/checks/US/US-A-PN-PNFP-PSIPS.txt')
usbFile = open('c:/Dowload/checks/US/US-B-PN-PNFP-PSIPS.txt')
outF=open('c:/Dowload/checks/US/output.xls', 'w')

pat = re.compile('([^\s]+)\s+([^\s]+)');
pat1 = re.compile('([^-]+)(-(.*))?');

emblNumbers = dict();

i=0;
for line in emblFile:
    i=i+1
    m = pat.match(line);
    if not m:
        print('EMBL file error', line)
    else:        
        s = m.group(1)
        m1 = pat1.match(s)        
        s=m1.group(1)
        skc=m1.group(3);
        if skc==None:
            skc='none'
        #if (i % 10000)==0:
            #print(s);
        if s.startswith('US'):                   
            emblNumbers[s]=skc
            
i=0

pnsfound=0
pnfpsfound=0
furtherfpfound=0
allfound=0
dubl = 0
processed=set()

outF.write('Num\tPN\tPN present\tEPOQ/EMBL kindcodes\tPNFP\tPNFP present\tEPOQ/EMBL kindcodes\tFurther\tfurther present\tEPOQ/EMBL kindcodes\tAny Present\n')
class PNum:
    # pass
    pn = ''
    inEmbl='-'
    kcs=''
def clearPNum(num):
    num.pn='-'
    num.inEmbl='-'
    num.kcs='-'
def fillPNum(num, fsnum, fskc, fsEmblKc, finEmbl):
    num.pn=fsnum
    num.kcs=fskc
    if finEmbl=='+':
       num.kcs=num.kcs+'/'+fsEmblKc
    num.inEmbl=finEmbl


def processLine(opn, opnfp, opnfpfp, oanyInEmbl):
    global i
    global pnsfound
    global pnfpsfound
    global furtherfpfound
    global allfound
    global processed
    global dubl
    global outF
    global processed

    if not opn.pn in processed:        
        if oanyInEmbl=='present':            
            allfound=allfound+1
        if opn.inEmbl=='+':                            
            pnsfound=pnsfound+1
        if opnfp.inEmbl=='+':
            pnfpsfound=pnfpsfound+1
        if opnfpfp.inEmbl=='+':
            furtherfpfound=furtherfpfound+1
        i=i+1                        
        processed.add(opn.pn)                    
        so=str(i)+'\t'+ opn.pn+'\t'+opn.inEmbl+'\t'+opn.kcs+'\t'+opnfp.pn+'\t'+opnfp.inEmbl+'\t'+opnfp.kcs+'\t'+opnfpfp.pn+'\t'+opnfpfp.inEmbl+'\t'+opnfpfp.kcs+'\t'+oanyInEmbl
        outF.write(so+'\n')
    else:
        dubl=dubl+1


def processFile(file):    
    pat = re.compile('([^-]+)-\s+([^\s]+)\s+([^\s]+)\s(.*)')
    eob=False
    
    pn=PNum()
    pnfp=PNum()
    pnfpfp=PNum()
    
    anyInEmbl = False
    for line in file:
        if not line.strip() == '':
            #print('new block')            
            so=''

            clearPNum(pn)
            clearPNum(pnfp)
            clearPNum(pnfpfp)
            
            anyInEmbl = '-'

            eob=False
            for line in file:
                if not line.strip()=='':
                    m=pat.match(line);            
                    if m:
                        spn=m.group(1).strip();
                        snum=m.group(2)
                        skc=m.group(3)
                        sEmblKc=''
                        inEmbl='-'
                        if (snum in emblNumbers.keys()):
                            inEmbl='+'
                            anyInEmbl = 'present'
                            sEmblKc=emblNumbers[snum];

                            
                        if spn=='PN':
                            fillPNum(pn, snum, skc, sEmblKc, inEmbl)
                            
                        if spn=='PNFP':
                            if not pnfp.pn=='-':
                                print('OMG')
                            fillPNum(pnfp, snum, skc, sEmblKc, inEmbl)                            

                        if spn=='':
                            if not pnfpfp.pn=='-':
                                print('OMG3')
                            fillPNum(pnfpfp, snum, skc, sEmblKc, inEmbl)                            
                            
                            #print('{num:<5}'.format(num=i), m.group(1),snum, sEmblKc);
                    else:
                        print('------', line.strip());
                else:
                    eob=True
                    processLine(pn, pnfp, pnfpfp, anyInEmbl)
                    break
                                
                
    if eob==False:
        processLine(pn, pnfp, pnfpfp, anyInEmbl)

            
processFile(usaFile)
processFile(usbFile)

outF.write('PNs found - '+str(pnsfound)+'\nPNFPs found - '+str(pnfpsfound)+'\nFurther found - '
           +str(furtherfpfound)+ '\nDuplicated PNs - '+str(dubl)+'\nTOTAL - '+str(allfound)+' found out of '+str(i))
outF.close()
print('{num}'.format(num=i))
print(len(emblNumbers))
