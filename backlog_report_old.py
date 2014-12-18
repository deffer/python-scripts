import sys, os, os.path
import fnmatch
import re

class nn:
    pass
pat = re.compile('([^\\d]+)?(\\d+)(.+)');
def parseNumber(file):
    global currentPrefix
    global pat
    strFileName = os.path.basename(file)
    strName = os.path.splitext(strFileName)[0]
    strExt = getExt(strFileName)
    m = pat.match(strName)
    if not m:
        print('OMG cant parse file name '+file)
        return None
    else:
        result = nn()
        result.code = m.group(1)
        if result.code == '' and ifPrefix():
            result.code = currentPrefix
        result.number=m.group(2)
        result.suffix=m.group(3)
        result.ext = strExt
        result.formattedNumber=result.code+result.number
        parentFolder = os.path.basename(os.path.split(file)[0])
        result.parentFolder = parentFolder
        return result

'''
Normally should contain two DossierFileInfo objects: paths to unverified and verified files
'''
class DossierInfo:
    pass

'''
Normally should contain at least 1 out of 3 possible file paths
path   - path to normal file, consisting of dossier number and extention (tar-gz, app, done, LIS)
backup - path to archived copies (tar, zip)
alt    - path to file, usually modified by curator, thus having highest quality

alt > path > backup

'''
class DossierFileInfo:
    def init():
        path = '-'
        backup = '-'
        alt = '-'

def addNormalPath(dosFileInfo, path):
    dosFileInfo.path = path

def addBackupPath(dosFileInfo, path):
    dosFileInfo.backup = path

def addAltPath(dosFileInfo, path):
    dosFileInfo.alt = path

mapTarGz = dict()

currentMap = dict()
currentPrefix = ''

def ifPrefix():
    global currentPrefix    
    return currentPrefix in ['SA', 'EP', 'FA']

def fileIterator(rootDirectory, acceptanceFunction):
    global currentPrefix
    suffix = os.path.basename(rootDirectory).upper()    
    if suffix in ['SA', 'EP', 'FA']:
        if currentPrefix != '':
            print('Switching from ', currentPrefix, ' to ', suffix)
        else:
            currentPrefix = suffix
    else:
        currentPrefix = ''
            
    for aCurrentDirectoryItem in [ os.path.join(rootDirectory, x) for x in os.listdir(rootDirectory) ]:        
        if acceptanceFunction(aCurrentDirectoryItem):
            yield aCurrentDirectoryItem
        if os.path.isdir(aCurrentDirectoryItem):
            for aSubdirectoryItem in fileIterator(aCurrentDirectoryItem, acceptanceFunction):
                yield aSubdirectoryItem
    
def getExt(file):
    ext = (os.path.splitext(file))[1]
    return ext.replace('.', '', 1)
    
def funcAcceptTarGz(file):    
    if os.path.isdir(file):
        return False
    else:
        ext = getExt(file).upper()
        if ext == 'TAR-GZ' or ext == 'TAR' or ext == 'ZIP':
            return True
        else:
            print('Unknown ', ext, '  ', file)
            return False

outF=open('g:\\epbisbl\\report.txt', 'w')
result = '''{dossiernumber}\t{thetype}\t{filename}\n'''

for x in fileIterator('G:/epbisbl/tar-gz', funcAcceptTarGz):
    numberInfo = parseNumber(x)
    if numberInfo == None:
        print('Error ', x)
    else:
        key = numberInfo.formattedNumber
        if key not in currentMap
            dfi = DossierFileInfo()
            dfi.init()
            currentMap[numberInfo.formattedNumber] = dfi
        else:
            dfi = currentMap[numberInfo.formattedNumber]        
        if numberInfo.ext.upper() == 'TAR' or numberInfo.ext.upper() == 'ZIP':
            ttype = 'backup'
            addBackupPath(dfi, x)            
        else:
            if numberInfo.ext.upper() == 'TAR-GZ':
                if numberInfo.parentFolder.upper()=='ALTERNATIVES':
                    ttype = 'alt'
                    addAltPathPath(dfi, x)
                else:
                    ttype = 'path'
                    addNormalPath(dfi, x)
            else:
                addNormalPath(dfi, x)
                ttype = 'ERROR'
        outF.write(result.format(dossiernumber=numberInfo.formattedNumber, filename=x, thetype=ttype))
outF.close()

'''
  try:
    pat = re.compile('(.+?)(?:-([\d\$](?:.*)))?\.jar');
    for x in findFileGenerator(rootOfSearch, anAcceptanceFunction):
      name = os.path.basename(x);
      m = pat.match(name);
      if not m:
        print('!!!!!', name)
      else:
        print(result.format(artifact=x, group=m.group(1), name=m.group(1), version=m.group(2)))


  except Exception as anException:
    print(anException)
'''
