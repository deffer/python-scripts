import sys, os, os.path
import fnmatch
import re

def findFileGenerator(rootDirectory, acceptanceFunction):
  for aCurrentDirectoryItem in [ os.path.join(rootDirectory, x) for x in os.listdir(rootDirectory) ]:
    if acceptanceFunction(aCurrentDirectoryItem):
      yield aCurrentDirectoryItem
    if os.path.isdir(aCurrentDirectoryItem):
      for aSubdirectoryItem in findFileGenerator(aCurrentDirectoryItem, acceptanceFunction):
        yield aSubdirectoryItem

if __name__ == "__main__":
  rootOfSearch = 'c:\\Documents and Settings\\ib82573\\.m2\\repository\\'
  if sys.argv[1:]:
    rootOfSearch = sys.argv[1]
  if sys.argv[2:]:
    classnameFragment = sys.argv[2].replace('.', '/')
    def anAcceptanceFunction (itemToTest):
      return not os.path.isdir(itemToTest) and fnmatch.fnmatch(itemToTest, '*.jar') and \
             classnameFragment in os.popen('jar -tf %s' % itemToTest).read()
  else:  
    def anAcceptanceFunction (itemToTest):
      return not os.path.isdir(itemToTest) and fnmatch.fnmatch(itemToTest, '*.jar')

  result = '''mvn install:install-file -Dfile={artifact} \\
                         -DgroupId={group} \\
                         -DartifactId={name} \\
                         -Dversion={version} \\
                         -Dpackaging=jar'''
  
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
