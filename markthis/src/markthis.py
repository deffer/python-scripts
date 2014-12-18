'''
Created on Jul 21, 2010
Simple JavaScript/Python(Bottle powered) application 
to mark up text with tags for CRF (Conditional Random Fields)

@author: Irina Benediktovich
'''
import bottle
import io
import session

from bottle import route, run, send_file, request, response, view, redirect

bottle.debug(True)
bottle.TEMPLATE_PATH.insert(0,'../web/')

validTags = [] # tags applicable to items

'''Tag allowed to me marked in principal.
Has name, background and key.
Used to mark up text, build stylesheet, build tags bar.'''
class ValidTag:
    def __init__(self, params):
        self.name = params[0]
        if len(params)>1 and params[1].strip() != '':
            self.background = params[1].strip()
        else:
            self.background = '#d0e4fe'
        if len(params)>2 and params[2].strip() != '':
            self.key = params[2].strip()
        else:
            self.key = ''

'''
Applied tag, it is used in Items objects to store information
about position where begin coloring and where to end it.
Note: there should be two instances of MarkTag class.
One for beginning of the selection and one for the end.
'''
class MarkTag:
    def __init__(self, kind : "['start', 'end']", name: "author, title...", pos:"actual location"):
        self.pos = pos
        self.kind = kind
        self.name = name

'''
Object of this class is created for every line in source file.
It actually represents one training entity and contains information about
its index, unmodified text and its marking.
Also has methods to build HTML representation and pseudoXML
'''
class Item:
    def __init__(self, index, original):
        self.tags = dict()
        self.index = index
        self.original = original

    def updateTag(self, name, start, end):
        if not start in self.tags:
            self.tags[start] = []
        if not end in self.tags:
            self.tags[end] = []
            
        self.tags[start].append(MarkTag('start', name, start))
        self.tags[end].insert(0, MarkTag('end', name, end))

    def resetTags(self):
        self.tags = dict()
    
    def getFormattedText(self, tagmaker):
        startfrom = 0
        result = ''
        for position in sorted(self.tags.keys()):
            result += self.original[startfrom:position]
            for tag in self.tags[position]:
                result += tagmaker(tag.kind, tag.name)
            startfrom = position
        result += self.original[startfrom:len(self.original)]
        return result
        
    def getInnerHTML(self):
        def htmlTagMaker(ttype, tname):
            if ttype=='start':
                result = '<span class="{tag}">'.format(tag=tname)
            else:
                result = '</span>'
            return result
        return self.getFormattedText(tagmaker = htmlTagMaker)

    def getTaggedText(self):
        def htmlTagMaker(ttype, tname):
            if ttype=='start':
                result = '<{tag}>'
            else:
                result = '</{tag}>'
            result = result.format(tag=tname)
            return result
        return self.getFormattedText(tagmaker = htmlTagMaker)
    

def getItems():
    ses = session.getOrCreateSession()
    if 'items' in ses.params:
        return ses.params['items']
    else:
        return createItems()

def createItems():
    ses = session.getOrCreateSession()
    result = []
    ses.params['items'] = result
    return result

''' Just return scripts '''
@route('/scripts/:file')
@route('/styles/:file')
def getfile(file):
    send_file(file, root='../web/')

''' Main page, where user actually marks tags '''
@route('/')
@view('markthis')
def mainPage():
    global validTags
    validTags = []
    readValidTags()
    return dict(items=getItems(), validTags=validTags)

''' Here user could see result as plain text '''
@route('/result')
def printResult():
    result = '' 
    for item in getItems():
        result += item.getTaggedText() + '\n'
    response.headers['Content-Type'] = 'text/plain; charset=UTF-8'
    return result

''' By going to '/result/result.txt' user will be offered by
    Download dialog to download result as text file'''
@route('/result/result.txt')
def downloadResult():
    result = ''
    for item in getItems():
        result += item.getTaggedText() + '\n'
    response.headers['Content-Type'] = 'text/plain; charset=UTF-8'
    response.headers['Content-Length'] = len(result)
    response.headers['Content-Disposition'] = 'attachment; filename=\"result.txt\"'
    return result

@route ('/item/:recordid', method='DELETE')
def resetItem(recordid):
    print ("deleting item: {n}".format(n = recordid))
    items = getItems()
    items[int(recordid)].resetTags()
    return items[int(recordid)].getInnerHTML()

@route ('/item/:recordid', method='POST')
def updateItem(recordid):
    print ("updating item: {n}".format(n = recordid))
    tag = request.params['tag']
    start = int(request.params['start'])
    end = int(request.params['end'])
    print("{}:{}:{}".format(tag, start, end))
    items = getItems()
    items[int(recordid)].updateTag(tag, start, end)
    return items[int(recordid)].getInnerHTML()

@route('/item/:recordid', method='GET')
def getItemHTML(recordid):
    print(recordid)
    items = getItems()
    return items[int(recordid)].getInnerHTML()

@route ('/source', method='POST')
def uploadSource():
    datafile = request.POST.get('datafile')
    loaditems(io.StringIO(str(datafile.file.read().encode("ISO-8859-1"), encoding='utf-8')))
    redirect('/')

def testit():
    items = getItems()
    items[1].updateTag ('author', 10, 25)
    print (items[1].getInnerHTML())
#    items[0].resetTags()
#    print (items[0].getInnerHTML())    

''' Reads all available tags from csv file: '..\resources\tags.txt' '''
def readValidTags():
    f = open(r'..\resources\tags.txt')
    for line in f:
        line = line.strip()
        if not line == '' and not line.startswith('#'):
            validTags.append(ValidTag([x.strip() for x in line.split(',')]))
    f.close()

def loaditems(f):
    index = 0;
    items = createItems()
    for line in f:
        item = Item(index, line.strip())
        items.append(item)
        index +=1

readValidTags()

run(host='localhost', port=8281)
