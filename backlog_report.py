import sys, os, os.path, filecmp
import fnmatch
import re
import backlog_classes
#import collections.defaultdict


        
def addNormalPath(errorMsg, dosFileInfo, path):
    global dupl
    if dosFileInfo.path != '-':
        if compareFiles(dosFileInfo.path, path):
            dupl.write('equal\t'+errorMsg+'\t'+dosFileInfo.path+'\t'+path+'\n')
        else:
            dupl.write('normal\t'+errorMsg+'\t'+dosFileInfo.path+'\t'+path+'\n')
            dosFileInfo.needManualCheck = True
    else:
        dosFileInfo.path = path

def addBackupPath(errorMsg, dosFileInfo, path):
    global dupl
    if dosFileInfo.backup != '-':
        if compareFiles(dosFileInfo.backup, path):
            dupl.write('equal\t'+errorMsg+'\t'+dosFileInfo.backup+'\t'+path+'\n')
        else:
            dupl.write('backup\t'+errorMsg+'\t'+dosFileInfo.backup+'\t'+path+'\n')
            dosFileInfo.needManualCheck = True        
    else:    
        dosFileInfo.backup = path

def addAltPath(errorMsg, dosFileInfo, path):
    global dupl
    if dosFileInfo.alt != '-':
        if compareFiles(dosFileInfo.alt, path):
            dupl.write('equal\t'+errorMsg+'\t'+dosFileInfo.alt+'\t'+path+'\n')
        else:
            dupl.write('alt\t'+errorMsg+'\t'+dosFileInfo.alt+'\t'+path+'\n')
            dosFileInfo.needManualCheck = True        
    else:        
        dosFileInfo.alt = path

def add2AnyFree(dfi, path):
    if dfi.path == '-':        
        dfi.path = path
        return True

    if dfi.backup == '-':
        dfi.backup = path
        return True

    if dfi.alt == '-':
        dfi.alt = path
        return True

    return False


def fileIterator(rootDirectory, acceptanceFunction):
    global currentPrefix
    suffix = os.path.basename(rootDirectory).upper()
    clearSuffix = False
    if suffix in ['SA', 'EP', 'FA']:
        if currentPrefix != '':
            print('Unexpected switching from ', currentPrefix, ' to ', suffix, ' for processing ', rootDirectory)
        clearSuffix = True
        currentPrefix = suffix
            
    for aCurrentDirectoryItem in [ os.path.join(rootDirectory, x) for x in os.listdir(rootDirectory) ]:        
        if not os.path.isdir(aCurrentDirectoryItem) and acceptanceFunction(aCurrentDirectoryItem):
            yield aCurrentDirectoryItem            
        if os.path.isdir(aCurrentDirectoryItem):
            '''skip those with _'''
            nm = os.path.basename(aCurrentDirectoryItem).upper()
            if not nm.endswith('_'):
                for aSubdirectoryItem in fileIterator(aCurrentDirectoryItem, acceptanceFunction):
                    yield aSubdirectoryItem
                    
    if (currentPrefix in ['SA', 'FA', 'EP'] and clearSuffix):        
        currentPrefix = ''
    
    

        
def saveFileInfoTarGz(dfi, numberInfo, file):
    global dupl
    fn = numberInfo.formattedNumber
    if numberInfo.ext.upper() == 'TAR' or numberInfo.ext.upper() == 'ZIP':
         addBackupPath(fn, dfi, file)            
    else:        
        if numberInfo.ext.upper() == 'TAR-GZ':            
            if numberInfo.parentFolder.upper()=='ALTERNATIVES':
                addAltPath(fn, dfi, file)
            else:
                addNormalPath(fn, dfi, file)
        else:
            addNormalPath(fn, dfi, file)
            print('Unknown file ',file)
            
def saveFileInfoSl(dfi, numberInfo, file):
    global dupl
    fn = numberInfo.formattedNumber
    if numberInfo.ext.upper() == 'APP':
        if numberInfo.parentFolder.upper()=='ALTERNATIVES':            
            addAltPath(fn, dfi, file)
        else:
            if dfi.path != '-' and numberInfo.suffix=='A':
                print('Skipping ', file)
            else:                    
                addNormalPath(fn, dfi, file)
    else:
        addNormalPath(fn, dfi, file)
        print('Unknown file ',file) 

def saveFileInfoDone(dfi, numberInfo, file):
    global dupl
    fn = numberInfo.formattedNumber
    ext = numberInfo.ext.upper()
    if ext == 'ZIP' or ext=='DONE_ZIP' or ext=='ZIP_DONE' or ext=='ERR':
        addBackupPath(fn, dfi, file)            
    else:
        if numberInfo.ext.upper() == 'DONE':            
            if numberInfo.suffix=='_1' or numberInfo.suffix=='_2':
                addAltPath(fn, dfi, file)
            else:                                 
                addNormalPath(fn, dfi, file)
        else:
            addNormalPath(fn, dfi, file)
            print('Unknown file ',file)

def saveFileInfoLIS(dfi, numberInfo, file):
    global dupl
    fn = numberInfo.formattedNumber
    ext = numberInfo.ext.upper()
    if ext == 'ZIP':
        addBackupPath(fn, dfi, file)
        return
    
    if ext == 'LIS':        
        if numberInfo.suffix=='_1' or numberInfo.suffix=='_2':
            addAltPath(fn, dfi, file)
        else:                                 
            addNormalPath(fn, dfi, file)
    else:
        addNormalPath(fn, dfi, file)
        print('Unknown file ',file)


def processSingleCollection(rootDirName, targetFolderName, funcAcceptFile, funcSaveFileInfo):
    print('...Processing ', targetFolderName, '...')
    global dupl
    global currentMap
    global allNumbers
    global currentPrefix
    global totalFiles
    
    processingFileDir = os.path.join(rootDirName, 'processing', targetFolderName)
    if not os.path.exists(processingFileDir):        
        os.makedirs(processingFileDir)
    outF = open(os.path.join(processingFileDir, 'debug.txt'), 'w')
    f2   = open(os.path.join(processingFileDir, 'newFiles.txt'), 'w')
    f3   = open(os.path.join(processingFileDir, 'fndFiles.txt'), 'w')
    dupl = open(os.path.join(processingFileDir, 'dupl.txt'), 'w')
    
    currentMap = dict()
    currentPrefix = ''
    pathNums = 0;
    totalFiles = 0;

    rootDirPath = os.path.join(rootDirName, targetFolderName)

    for x in fileIterator(rootDirPath, funcAcceptFile):
        totalFiles = totalFiles+1        
        numberInfo = backlog_classes.parseNumber(x, currentPrefix)
        if numberInfo == None:
            print('Error parsing path ', x)
        else:
            key = numberInfo.formattedNumber
            if key not in currentMap:
                dfi = backlog_classes.DossierFileInfo()            
                currentMap[key] = dfi
                f2.write(key+'\n')
            else:
                dfi = currentMap[key]
                f3.write(key +'\n')
            funcSaveFileInfo(dfi, numberInfo, x)
            outF.write(result.format(dossiernumber=numberInfo.formattedNumber, filename=x, thetype='path'))

            fk = key.replace('XX', 'EP', 1)
            if fk not in allNumbers:
                dossier = backlog_classes.DossierInfo()
                dossier.setNumber(fk)
                dossier.containsXX = (fk != key)
                allNumbers[fk] = dossier
            else:
                dossier = allNumbers[fk]
            dossier.addDfi(dfi, targetFolderName)
            
            
    outF.close()
    f2.close()
    f3.close()
    
    print('Total files:',totalFiles,'. Unique', targetFolderName, ' numbers:',len(currentMap))
    printDfiCollectionIntoFile(targetFolderName, os.path.join(processingFileDir, (targetFolderName+'.txt')), currentMap)
    dupl.close()

def printDfiCollectionIntoFile(prefix, fileName, dfiCollection):
    dictXX = backlog_classes.extractXX(dfiCollection)
    if len(dictXX) > 0:
        #print('Merging', len(dictXX), ' numbers with EP')
        notMergedXX = mergeSets(dictXX, dfiCollection)
        if len(notMergedXX)>0:
            print(len(notMergedXX),' of ',len(dictXX), ' XX numbers were unsafely merged with EP')
            dfiCollection.update(notMergedXX)
            
    file = open(fileName, 'w')
    noPathFiles = 0;
    for key in dfiCollection.keys():
        dfi = dfiCollection[key]
        if dfi.path=='' or dfi.path=='-':
            noPathFiles = noPathFiles+1
        code = prefix
        if dfi.needManualCheck:
            code = 'manual'
        file.write(code+'\t'+key+'\t'+dfi.path+'\t'+dfi.backup+'\t'+dfi.alt+'\n')
    file.close()
    if noPathFiles>0:
        print('There are ', noPathFiles,' entries without normal path\n')
    else:
        print('\n')


        
def mergeSets(dictXX, dictOther):
    restXX = dict()
    keysXX = dictXX.keys()
    for keyXX in keysXX:
        dfiXX = dictXX[keyXX]            
        keyEP = keyXX.replace('XX', 'EP', 1)        
        if keyEP in dictOther.keys():
            dfiEP=dictOther[keyEP]
            if not mergeNumbers(dfiXX, dfiEP, keyEP):
                restXX[keyXX] = dfiXX
        else:
            restXX[keyXX]=dfiXX

    return restXX

def mergeNumbers(dfiXX, dfiEP, number):
    global dupl
    if compareFiles(dfiXX.path, dfiEP.path):        
        dupl.write('equal\t'+number+'\t'+dfiXX.path+'\t'+dfiEP.path+'\n')
        mergeTwoDfi(dfiXX, dfiEP)
        return True

    if compareFiles(dfiXX.backup, dfiEP.backup):
        dupl.write('equal\t'+number+'\t'+dfiXX.backup+'\t'+dfiEP.backup+'\n')        
        mergeTwoDfi(dfiXX, dfiEP)
        return True

    if compareFiles(dfiXX.alt, dfiEP.alt):
        dupl.write('equal\t'+number+'\t'+dfiXX.alt+'\t'+dfiEP.alt+'\n')        
        mergeTwoDfi(dfiXX, dfiEP)
        return True

    ''' merging anyway and setting "manual check" '''
    ''' update: DONT set manual check - no way to check 2k files manually'''
    ''' dfiEP.needManualCheck = True'''
    dupl.write('merged\t'+number+'\t'+dfiXX.getRepresentative()+'\t'+dfiEP.getRepresentative()+'\n')        
    if not dfiXX.path == '-':
        if not add2AnyFree(dfiEP, dfiXX.path):
            print('Unable to merge - too many versions of', number, dfiXX.path, dfiEP.path)
            return True

    if not dfiXX.backup == '-':
        if not add2AnyFree(dfiEP, dfiXX.backup):
            print('Unable to merge - too many versions of', number, dfiXX.backup, dfiEP.backup)
            return True

    if not dfiXX.alt == '-':
        if not add2AnyFree(dfiEP, dfiXX.alt):
            print('Unable to merge - too many versions of', number, dfiXX.alt, dfiEP.alt)
            return True

    return True
        
def compareFiles(file1, file2):
    if file1==None or file1=='' or file1=='-' or file2==None or file2=='' or file2=='-':
        return False
    if filecmp.cmp(file1, file2):
        return True


def mergeTwoDfi(dfiXX, dfiEP):
    if (not dfiXX.path == '-') and dfiEP.path=='-':
        print('Merging   XX normal path added to EP:',dfiXX.path)
        dfiEP.path=dfiXX.path    
    if (not dfiXX.backup == '-') and dfiEP.backup=='-':
        print('Merging   XX backup path added to EP:',dfiXX.backup)        
        dfiEP.backup=dfiXX.backup
    if (not dfiXX.alt == '-') and dfiEP.alt=='-':
        print('Merging   XX alt path added to EP:',dfiXX.alt)                
        dfiEP.alt=dfiXX.alt

def printReportFile():
    file = open(os.path.join(baseDir, 'processing/report.xls'), 'w')    
    columnNames = ('Total numbers', 'Total epBis', 'Old numbers', 'Old epbises', 'Merged with XX', 'EpBises with XX')
    string = ''
    for name in columnNames:
        string = string+'\t'+name
    string = string.replace('\t', '', 1)
    file.write(string+'\n')

    string = ''+str(len(allNumbers))+'\t'+str(backlog_classes.countEpBis(allNumbers))+'\t'
    string = string + str(backlog_classes.countOld(allNumbers, False))+'\t'+str(backlog_classes.countOld(allNumbers, True))+'\t'
    string = string + str(backlog_classes.countContainingXX(allNumbers, False))+'\t'+str(backlog_classes.countContainingXX(allNumbers, True))+'\n'
    file.write(string)

    file.close()

def reportEpBises():
    file = open(os.path.join(baseDir, 'processing/epbises_all.txt'), 'w')
    fileNew = open(os.path.join(baseDir, 'processing/epbises_new.txt'), 'w')
    fileOld = open(os.path.join(baseDir, 'processing/epbises_old.txt'), 'w')
    fileSAnew = open(os.path.join(baseDir, 'processing/SA_new.txt'), 'w')
    fileSAold = open(os.path.join(baseDir, 'processing/SA_old.txt'), 'w')
    fileEPnew = open(os.path.join(baseDir, 'processing/EP_new.txt'), 'w')
    fileEPold = open(os.path.join(baseDir, 'processing/EP_old.txt'), 'w')
    fileNNnew = open(os.path.join(baseDir, 'processing/NN_new.txt'), 'w')
    fileNNold = open(os.path.join(baseDir, 'processing/NN_old.txt'), 'w')
    sett = set()
    setNew = set()
    setOld = set()
    setSAnew = set()
    setSAold = set()
    setEPnew = set()
    setEPold = set()
    setNNnew = set()
    setNNold = set()
    for key in allNumbers:
        dossier = allNumbers[key]
        if backlog_classes.isEpBis(dossier.number):
            sett.add(dossier.number.replace('XX', 'EP', 1))
            if dossier.isNew():
                setNew.add(dossier.number.replace('XX', 'EP', 1))
            else:
                setOld.add(dossier.number.replace('XX', 'EP', 1))
        else:
            if dossier.number.startswith('SA'):
                if dossier.isNew():
                    setSAnew.add(dossier.number)
                else:
                    setSAold.add(dossier.number)
            elif (dossier.number.startswith('EP') or dossier.number.startswith('XX')):
                if dossier.isNew():
                    setEPnew.add(dossier.number.replace('XX', 'EP', 1))
                else:
                    setEPold.add(dossier.number.replace('XX', 'EP', 1))
            else:
                if dossier.isNew():
                    setNNnew.add(dossier.number)
                else:
                    setNNold.add(dossier.number)
                 
    res =  sorted(sett)
    resNew = sorted(setNew)
    resOld = sorted(setOld)
    setSAnew = sorted(setSAnew)
    setSAold = sorted(setSAold)
    setEPnew = sorted(setEPnew)
    setEPold = sorted(setEPold)
    setNNnew = sorted(setNNnew)
    setNNold = sorted(setNNold)    
    for number in res:
        file.write(number+'\n')
    file.close()
    for number in resNew:
        fileNew.write(number+'\n')
    fileNew.close()
    for number in resOld:
        fileOld.write(number+'\n')
    fileOld.close()

    file = fileSAnew
    for number in setSAnew:
        file.write(number+'\n')
    file.close()

    file = fileSAold
    for number in setSAold:
        file.write(number+'\n')
    file.close()    

    file = fileEPnew
    for number in setEPnew:
        file.write(number+'\n')
    file.close()

    file = fileEPold
    for number in setEPold:
        file.write(number+'\n')
    file.close()

    file = fileNNnew
    for number in setNNnew:
        file.write(number+'\n')
    file.close()

    file = fileNNold
    for number in setNNold:
        file.write(number+'\n')
    file.close()

    
def extendedReportOn(fileName):
    fileFilter = open(fileName)
    file = open(os.path.join(baseDir, 'processing/filter.txt'), 'w')
    filterSet = set()
    for s in fileFilter:
        filterSet.add(s.strip())

    sortedAll = sorted(allNumbers, key=sortingFunctionOfAllNumbers)

    result = list()
    
    ''' sortedAll  is  LIST ??????'''
    for key in sortedAll:
        dossier = allNumbers[key]
        fixedNumber = dossier.number.replace('XX', 'EP', 1)
        if fixedNumber in filterSet:
            result.append(dossier)
            '''file.write(dossier.toString()+'\n')'''

    resultSorted = sorted(result, key=sortingFunctionOfExtendedReport)
    for dossier in resultSorted:
        file.write(dossier.toString()+'\n')
    
    fileFilter.close()
    file.close()

def sortingFunctionOfAllNumbers(key):
    di = allNumbers[key]
    return di.getHash()

def sortingFunctionOfExtendedReport(dossier):
    return dossier.flags()
        
result = '''{dossiernumber}\t{thetype}\t{filename}\n'''
currentMap = dict()
allNumbers = dict()
currentPrefix = ''
totalFiles = 0;
baseDir = 'G:\\epbisbl'
            
processSingleCollection(baseDir,'tar-gz', backlog_classes.funcAcceptTarGz, saveFileInfoTarGz)
processSingleCollection(baseDir,'sl',     backlog_classes.funcAcceptSl,    saveFileInfoSl)
processSingleCollection(baseDir,'done',   backlog_classes.funcAcceptDone,  saveFileInfoDone)
processSingleCollection(baseDir,'lis',    backlog_classes.funcAcceptLIS,   saveFileInfoLIS)

print('TOTAL:', len(allNumbers), 'unique numbers, ', backlog_classes.countEpBis(allNumbers), 'epBis-es.')
printReportFile()
reportEpBises()
extendedReportOn(r'g:\epbisbl\processing\publications.txt')

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
