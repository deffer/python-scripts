import re
import os
class nn:
    pass
pat = re.compile('([^\\d]+)?(\\d+)(.+)?');
patwo = re.compile('(wo|WO)((?:\\d+)(?:[^\\d]{2})?(?:\\d+))(.+)?');
def parseNumber(file, currentPrefix):
    global pat
    strFileName = os.path.basename(file)
    strName = os.path.splitext(strFileName)[0]
    strExt = getExt(strFileName)
    m = patwo.match(strName)
    if not m:
        m = pat.match(strName)
    if not m:        
        return None
    else:
        result = nn()
        result.code = m.group(1)
        if (result.code == None or result.code=='')and ifPrefix(currentPrefix):
            result.code = currentPrefix
        if result.code == None or result.code=='':
            result.code = 'XX'
        result.number=m.group(2)
        result.suffix=m.group(3)
        result.ext = strExt
        formattedNumber = result.code+result.number
        result.formattedNumber = formattedNumber.upper()
        parentFolder = os.path.basename(os.path.split(file)[0])
        result.parentFolder = parentFolder
        result.isEpBis = isEpBis(formattedNumber)
        return result

'''
Normally should contain two DossierFileInfo objects: paths to unverified and verified files
'''
class DossierInfo:
    def __init__(self):
        self.number = '-'
        self.old = None
        self.oldVer = None
        self.new = None
        self.newVer = None
        self.isEpBis = False
        self.containsXX = False

    def setNumber(self, number):
        self.number = number
        self.isEpBis = isEpBis(number)
        
    def addDfi(self, dfi, prefix):
        if prefix.upper() == 'TAR-GZ':
            self.old = dfi
        if prefix.upper() == 'SL':
            self.oldVer = dfi
        if prefix.upper() == 'DONE':
            self.new = dfi
        if prefix.upper() == 'LIS':
            self.newVer = dfi

    def isManual(self):
        if self.old!=None and self.old.needManualCheck:
            return True
        if self.oldVer!=None and self.oldVer.needManualCheck:
            return True        
        if self.new!=None and self.new.needManualCheck:
            return True
        if self.newVer!=None and self.newVer.needManualCheck:
            return True
        return False

    ''' check for just having only path-file per each version folder'''
    def isProper(self):

        if self.isNew():
            if self.new!=None and not self.new.isProperFile():
                return False

            if self.newVer!=None and not self.newVer.isProperFile():
                return False

            if self.oldVer!=None and not self.oldVer.isProperFile():
                return False
        else:
            
            if self.old!=None and not self.old.isProperFile():
                return False


        return True

        
    ''' new>old and proper>manual'''    
    def getHash(self):
        i = 0

        if self.isNew():
            i = 1
        else:
            i = 2

        if not self.isProper():
            i = i + 10                
                
        if self.isManual():
            i = i + 100

        return i

    def toString(self):
        s = self.number+'\t'+self.flags()
        s = s + '\t'+self.reportDFI(self.old)
        s = s + '\t'+self.reportDFI(self.oldVer)
        s = s + '\t'+self.reportDFI(self.new)
        s = s + '\t'+self.reportDFI(self.newVer)
        return s
        
    def flags(self):
        result = ''
        result = result+self.__toShortChar(self.old)
        result = result+self.__toShortChar(self.oldVer)
        result = result+self.__toShortChar(self.new)
        result = result+self.__toShortChar(self.newVer)
        return result

    def __toShortChar(self, dfi):
        if dfi == None:
            return '_'
        if dfi.needManualCheck:
            return 'M'
        if dfi.isProperFile():
            return 'p'
        return 'x'

    def reportDFI(self, dfi):
        if dfi == None:
            return '-\t-\t-\t-'
        else:
            return dfi.toString()
        
    def isNew(self):
        return self.new!=None or self.newVer!=None or self.oldVer!=None


'''
Normally should contain at least 1 of 3 possible file paths
path   - path to normal file, consisting of dossier number and extention (tar-gz, app, done, LIS)
backup - path to archived copies (tar, zip) or other 'strange' files
alt    - path to file, usually modified by curator, thus having highest quality

alt > path > backup

'''
class DossierFileInfo:
    def __init__(self):
        self.path = '-'
        self.backup = '-'
        self.alt = '-'
        self.needManualCheck = False

    def isProperFile(self):
        return self.path!='-' and (self.backup=='-' and self.alt=='-')

    def getRepresentative(self):
        if not self.path == '-':
            return self.path
        if not self.backup == '-':
            return self.backup
        if not self.alt == '-':
            return self.alt

    ''' proper > having path > rest > manual'''
    def getHash(self):
        i = 0
        if self.isProper():
            i = 10
        else:            
            if self.path=='' or self.path=='-':
                i = 70
            else:
                i = 20
        if needManualCheck:
            i = i + 100

        return i
    
    def toString(self):
        if self.needManualCheck:
            s = 'M'
        else:
            s = 'x'            
        s=s+'\t'+self.path+'\t'+self.backup+'\t'+self.alt
        return s
    
def isEpBis(number):
    return ((number.startswith('EP')or number.startswith('XX')) and number[4] in ('7','8','9'))

def ifPrefix(prefix):
    return prefix in ['SA', 'EP', 'FA']

def countEpBis(somedict):
    result = 0
    for key in somedict:
        if isEpBis(key):
            result = result+1
    return result


def countOld(somedict, onlyEpBises):
    result = 0
    for key in somedict:
        dossier = somedict[key]
        if (not onlyEpBises) or isEpBis(key):
            if not dossier.isNew():
                result = result+1
    
    return result

def countContainingXX(somedict, onlyEpBises):
    result = 0
    for key in somedict:
        dossier = somedict[key]
        if onlyEpBises:
            if dossier.isEpBis and dossier.containsXX:
                result = result+1
        else:
            if dossier.containsXX:
                result = result+1

    return result    

def extractXX(someDict):
    res = dict()
    keys = someDict.keys()
    for key in keys:
        if key.startswith('XX'):
            dfi=someDict[key]
            res[key]=dfi
            ''' and delete'''

    for key in res.keys():
        del someDict[key]
    return res

def getExt(file):
    ext = (os.path.splitext(file))[1]
    return ext.replace('.', '', 1)

def funcAcceptExtention(file, exts):
    ext = getExt(file).upper()
    if ext  in exts:
        return True
    else:
        print('Unknown ', ext, '  ', file)
        return False    
    
def funcAcceptTarGz(file):
    return funcAcceptExtention(file, ('TAR-GZ', 'TAR', 'ZIP'))
        
def funcAcceptSl(file):
    return funcAcceptExtention(file, ('APP'))

def funcAcceptDone(file):
    return funcAcceptExtention(file, ('DONE', 'ZIP', 'DONE_ZIP', 'ZIP_DONE', 'ERR'))    

def funcAcceptLIS(file):
    return funcAcceptExtention(file, ('LIS', 'ZIP'))       
