'''
Created on Nov 16, 2010

@author: clair
'''
import bottle
import re
import time
import json

from collections import defaultdict
from bottle import route, run, send_file, request, response, view, redirect, static_file, template

bottle.debug(True)
bottle.TEMPLATE_PATH.insert(0,'../web/')

defaultUserNames = ['Alice', 'Bob', 'Eve','Helen', 'Boris']
defaultUserIcons = {'Alice':'geisha', 'Bob':'guerrero_chino', 'Eve':'diabla', 'Helen':'estilista', 'Boris':'hiphopper'}
allUserIcons = [['afro_32.png','alien_32.png','anciano_32.png','artista_32.png','astronauta_32.png','barbaman_32.png','bombero_32.png','boxeador_32.png'],
                ['bruce_lee_32.png','caradebolsa_32.png','chavo_32.png','cientifica_32.png','cientifico_loco_32.png','comisario_32.png','cupido_32.png','diabla_32.png'],
                ['director_32.png','dreds_32.png','elsanto_32.png','elvis_32.png','emo_32.png','escafandra_32.png','estilista_32.png','extraterrestre_32.png'],
                ['fisicoculturista_32.png','funky_32.png','futbolista_brasilero_32.png','gay_32.png','geisha_32.png','ghostbuster_32.png','glamrock_singer_32.png','guerrero_chino_32.png'],
                ['hiphopper_32.png','hombre_hippie_32.png','nena_afro_32.png','indio_32.png','joker_32.png','karateka_32.png','mago_32.png','maori_32.png'],
                ['mario_barakus_32.png','mascara_antigua_32.png','metalero_32.png','meteoro_32.png','michelin_32.png','mimo_32.png','mister_32.png','mounstrico1_32.png'],
                ['mounstrico2_32.png','mounstrico3_32.png','mounstrico4_32.png','mounstruo_32.png','muerte_32.png','mujer_hippie_32.png','mujer_latina_32.png','muneco_lego_32.png']]

deffer = None
chatter = None
class UserSession:
    def __init__(self, id=0, name='Chatter', online=True):
        self.id = str(id)        
        self.icon = 'astronauta'
        self.conversations = list()
        self.country = None
        self.online = online
        self.lastPing = time.time()
        self.name = name;
        
    def setName(self, name):
        self.name = name

    def setIcon(self, icon):
        self.icon = icon
    
    def toString(self):
        return ""+self.id+"("+self.name+")"

class Conversation:
    def __init__(self, id, partner1, partner2):
        self.id = id
        self.partner1 = partner1
        self.partner2 = partner2
        self.messages=[]
        
    def getMyPartner(self, myId):
        if self.partner1.id==myId:
            return self.partner2
        elif self.partner2.id==myId:
            return self.partner1
        else:
            return None

    def getMessagesAfter(self, id):
        result = list()
        for msg in self.messages:
            if msg.id > id:
                result+=[msg]
        return result

class Message:
    def __init__(self, text, userName):
        global msgIncrement
        self.text = text
        self.userName = userName
        msgIncrement+=1
        self.id = msgIncrement
        self.time = timeMillis()

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Message):
            return {'text':obj.text, 'userName':obj.userName, 
                    'id':obj.id, 'time':obj.time}
        return json.JSONEncoder.default(self, obj)


users = dict()
conversations = list()


deffer = UserSession(id='1', name='Deffer', online=False)
chatter = UserSession(id='0', name='Chatter', online=False)
pluto = UserSession(id='2', name='Pluto', online=True)
pluto.icon = 'indio'
users['']=chatter
users['0']=chatter
users['1']=deffer
users['2']=pluto

increment = 2
msgIncrement = 2;


def getConversationById(talkid):
    for c in conversations:
        if c.id==talkid:
            return c
            
def getConversation(partner1, partner2):
    global increment
    global conversations
    for c in conversations: 
        if c.partner1.id in [partner1.id, partner2.id] and c.partner2.id in [partner1.id, partner2.id]:
            return c
    
    increment+=1
    c = Conversation(str(increment), users[partner1.id], users[partner2.id])
    conversations+=[c]
    return c

def getConversations(userid):
    global conversations
    res = list()
    for c in conversations:
        if userid in [c.partner1.id, c.partner2.id]:
            res.append(c)
    return res

def getNewChanges(user, lastMsgId):
    requests = list()
    messages = dict()
    cc = getConversations(user.id)
    for c in cc:
        if c in user.conversations:
            msgs = c.getMessagesAfter(lastMsgId);
            if len(msgs)>0:
                partner = c.getMyPartner(user.id)
                print "Found new messages from "+partner.id+"("+partner.name+") to "+user.id+"("+user.name+")"
                messages[c.id]=msgs
                '''messages.update(c.id, msgs)'''
        else:
            partner = c.getMyPartner(user.id)
            if partner.online:
                print "Found "+partner.toString()+" wants to talk to "+user.id+"("+user.name+")"
                requests+=[partner.id]
    
    return {"requests":requests, "messages":messages}

def getCurrentUser():
    userid = request.COOKIES.get('chatteruserid', '') 
    if not userid or userid=='0':
        return chatter
    if not userid in users:
        user = loadUser(userid)
    else:
        user = users[userid]
    return user

def loadUser(userid):
    global increment
    if int(userid)>increment:
        increment+=1
    user = UserSession(userid, 'Chatter')        
    users[userid] = user       
    print 'loading Chatter ', userid
    return user

def makeNewUser():
    global increment
    increment+=1
    userid=str(increment)
    user = UserSession(userid, 'Chatter')        
    users[userid] = user       
    response.set_cookie('chatteruserid', userid)
    print 'creating new Chatter ', userid
    return user

def timeMillis():
    return int(time.time() * 1000)

def filterUsers(userid):
    ''' simple implementation '''
    
    ''' 1. those onliners matched by filter
        2. yourself
        3. me
        4. TODO conversation partners (that are offline and so not matched in 1.)
    '''
    result = list()
    for user in users.values():
        if user.id != '' and user.id !='0':
            if user.id==userid or user.online or user.id=='1' or user.id=='2':
                result+=[user]
        
    return result


@route('/')
@view('main')
def index():    
    result = getCurrentUser()
    return dict(result=result, onliners=filterUsers(result.id), 
                talks=result.conversations, allIcons=allUserIcons, 
                lastTime=timeMillis(), lastMsgId = msgIncrement)


@route ('/message.do', method='POST')
def sendMessage():    
    user = getCurrentUser()
    user.lastPing = time.time()
    talkid = request.POST.get('talkid').strip()
    msgText = request.POST.get('message').strip()
    lastIdStr = request.POST.get('lastMsgId')
    print "message from "+user.name+": ", msgText        
    c = getConversationById(talkid)
    if c:
        message=Message(msgText, user.name) 
        c.messages.append(message)
        result = c.getMessagesAfter(int(lastIdStr))
        
        ''' if talking to pluto - respond '''
        partner = c.getMyPartner(user.id)
        if partner==pluto:
            pmessage = Message(msgText+" :)", partner.name)
            c.messages.append(pmessage)
        
        return json.dumps({'newTime':str(timeMillis()), 'newMsgId':message.id, 'messages':result}, cls=ComplexEncoder)
    else:
        return json.dumps({'newTime':str(timeMillis()), 'msg':"conversation is closed"})       


@route ('/ping.do', method='POST')
def ping():    
    global msgIncrement
    user = getCurrentUser()
    if user == chatter:
        return json.dumps({'newTime':str(timeMillis())})
    
    user.lastPing = time.time()    
    lastIdStr = request.POST.get('lastMsgId')
    print "request for changes from "+user.id+"("+user.name+")"        
    changes = getNewChanges(user, int(lastIdStr))       
    return json.dumps({'newTime':str(timeMillis()), 
                       'newMsgId':msgIncrement, 
                       'messages':changes['messages'],
                       'requests':changes['requests']}, cls=ComplexEncoder)
       


@route ('/request.do', method='POST')
def requestConversation():
    global msgIncrement
    user = getCurrentUser()
    if user==chatter:
        user=makeNewUser()
    else:
        user.lastPing = time.time()
    partnerid = request.POST.get('partnerid').strip()
    print 'requesting for', user.id,'(',user.name, ') talk to', partnerid 
    if partnerid in users:
        partner = users[partnerid]
        c = getConversation(partner, user)
        if not c in user.conversations:
            user.conversations+=[c]
        if partner.id=='2' and not c in partner.conversations:
            partner.conversations+=[c]
        htmlBody = template('conversation', talk=c)
        return json.dumps({'talkid':c.id, 'myid':user.id, 'html':htmlBody, 
                           'msgId':msgIncrement, 'time':timeMillis()})
    else:
        return json.dumps({'msg':'User is offline'})
        

@route ('/username.do', method='POST')
def setUserName():        
    inputUserName = request.POST.get('userName').strip()
    print 'name' , inputUserName
    if (not inputUserName==''):
        user=getCurrentUser()
        if user==chatter:
            user=makeNewUser() 
        else:
            user.lastPing =time.time()    
        user.name=inputUserName        
        return json.dumps({'myid':user.id})
    else:
        return json.dumps({'msg':"name not set"})
    
    
@route ('/usericon.do', method='POST')    
def setUserIcon():        
    inputIconName = request.POST.get('iconname').strip()
    print 'icon ', inputIconName
    if (not inputIconName=='') :
        user=getCurrentUser()
        if user==chatter:
            user=makeNewUser()
        else:
            user.lastPing = time.time()
        user.icon = inputIconName
        return json.dumps({'myid':user.id})
    else:
        return json.dumps({'msg':"icon not set"})

@route ('/links.html',)
def staticLinks():
    send_file("links.html", root='../web/')

@route('/usericons/:path#.+#')
def serve_icons(path):
    return static_file(path, root='../web/icons', mimetype='image/png')
 
''' Just return scripts '''
@route('/scripts/:file')
@route('/styles/:file')
def serve_resources(file):
    try:
        if file.endswith(".gz"):
            response.headers['Content-Encoding'] = "gzip"
    except Exception as e:
        print(e)
            
    send_file(file, root='../web/') 
    
#run(host='10.0.0.171', port=8080)
run(host='10.3.3.59', port=8080)
#run(host='86.87.205.142', port=8080)