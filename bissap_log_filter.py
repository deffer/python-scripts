import re

def isExpectedError(line):
    # protein annotations are not sent to EBI
    if line=='Required qualifier /product associated with mod_res is missing.':
        return True
    if line=='Required qualifier /mod_base associated with modified_base is missing.':
        return True
    if line=='Qualifier /mod_base declares incorrect value.':
        return True
    if line=='Qualifier /note is not compatible with the feature mod_res.':
        return True

    if line=='The declared length of the coding part of the sequence is not divisible by 3.':
        return True
    
    if line=='Qualifier /mod_bases is not compatible with the feature modified_base.':
        return True
    if line=='Qualifier /replace is not compatible with the feature modified_base.':
        return True
    if line=='Qualifier /bound_moiety is not compatible with the feature misc_feature.':
        return True
    
    if line=='Required qualifier /bound_moiety associated with protein_bind is missing.':
        return True
    if line=='Required qualifier /bound_moiety associated with misc_binding is missing.':
        return True
    if line=='Required qualifier /replace or /note associated with variation is missing.':
        return True
    
    if line=='Artificial/Unknown sequence is not described.':
        return True
    
def isExpectedWarning(line):
    global pt_warns
    
    if line=='The amino acid sequence corresponding to this CDS feature is missing.':
        return True
    if line=='The organism name "synthetic peptide" was not found in the taxonomy database.':
        return True
    if line=='The sequence length is shorter than accepted by rules in place.':
        return True
    if line=='The amino acid sequence corresponding to this CDS feature is missing.':
        return True
    if line=='The organism name "Bacteria" was not found in the taxonomy database.':
        return True
    if line=='The organism name "Chrysanthemum" was not found in the taxonomy database.':
        return True
    if line=='The organism name "Mus" was not found in the taxonomy database.':
        return True
    if line=='The organism name "Rat" was not found in the taxonomy database.':
        return True    
    if line=='The organism name "Pinus" was not found in the taxonomy database.':
        return True    
    if line=='The organism name "Drosophila" was not found in the taxonomy database.':
        return True
    if line=='Sequence is a \'no base/residue\' sequence.':
        return True
    
    for pattern in  pt_warns:
        m = pattern.match(line)
        if m:
            return True

    #print(line)
    return False


file = open(r'G:\epbisbl\converter25\log\summaryErrorReport.txt')
pt_file = re.compile('File\:\s+([A-Z\d]+)\.st25');
pt_info = re.compile('\*\sSeverity\s\:\s+(WARNING|INFO|ERROR) at (.*)')
pt_warns ={re.compile('The organism name (.+?) is not in the list of scientific names\.'),
           re.compile('The sequence contains (.+?) at positions:(.*)')           
          }

curfile = None
curlist = None
mapp = dict()

line = file.readline()
i = 0
while line!=None and line!='':                     
    m = pt_file.match(line)

    if m:
        curfile = m.group(1)
        curlist = list()
        mapp[curfile]=curlist
    else:
        m1 = pt_info.match(line)
        if m1:
            errors=list()
            errors.append(line)
            errors.append(file.readline())
            errors.append(file.readline())
            errors.append(file.readline())            
            ertype = m1.group(1).strip()
            reason = errors[2].strip()
            if ertype=='ERROR':
                if not isExpectedError(reason):
                    curlist.extend(errors)
            if ertype=='WARNING':                
                if not isExpectedWarning(reason):
                    curlist.extend(errors)

    line = file.readline()
    i+=1
    if ((i % 10000)==0):
        print('Progressing through ', curfile)
    
print('Counted {ffile} files'.format(ffile=len(mapp)))
result = sorted(mapp)
outF = open(r'G:\epbisbl\converter25\log\_filteredErrorReport.txt', 'w')
for key in result:
    errors = mapp[key]
    if len(errors)>0:        
        outF.write('{dn}===========\n'.format(dn=key))
        for s in errors:
            outF.write(s)
        outF.write('=====================\n')
    
outF.close()


