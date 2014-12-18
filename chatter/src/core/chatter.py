'''
Created on Nov 16, 2010

@author: clair
'''

import re
import time
import json
import bottle

from collections import defaultdict
from bottle import route, run, send_file, request, response, view, redirect, static_file, template
from model import UserSession, Conversation, Message

import dbaccess
import model

bottle.debug(True)
bottle.TEMPLATE_PATH.insert(0,'web/')
alicebot=None

def getAliceBot():
    global alicebot
    if alicebot:
        return alicebot;
    
    print 'initializing ALICE...'
    import aiml
    alicebot = aiml.Kernel()
    alicebot.learn("data/alice/std-startup.xml")
    alicebot.respond("load aiml b")
    print '            ... DONE!'
    return alicebot


allUserIcons = [['afro_32.png','alien_32.png','anciano_32.png','artista_32.png','astronauta_32.png','barbaman_32.png','bombero_32.png','boxeador_32.png'],
                ['bruce_lee_32.png','caradebolsa_32.png','chavo_32.png','cientifica_32.png','cientifico_loco_32.png','comisario_32.png','cupido_32.png','diabla_32.png'],
                ['director_32.png','dreds_32.png','elsanto_32.png','elvis_32.png','emo_32.png','escafandra_32.png','estilista_32.png','extraterrestre_32.png'],
                ['fisicoculturista_32.png','funky_32.png','futbolista_brasilero_32.png','gay_32.png','geisha_32.png','ghostbuster_32.png','glamrock_singer_32.png','guerrero_chino_32.png'],
                ['hiphopper_32.png','hombre_hippie_32.png','nena_afro_32.png','indio_32.png','joker_32.png','karateka_32.png','mago_32.png','maori_32.png'],
                ['mario_barakus_32.png','mascara_antigua_32.png','metalero_32.png','meteoro_32.png','michelin_32.png','mimo_32.png','mister_32.png','mounstrico1_32.png'],
                ['mounstrico2_32.png','mounstrico3_32.png','mounstrico4_32.png','mounstruo_32.png','muerte_32.png','mujer_hippie_32.png','mujer_latina_32.png','muneco_lego_32.png']]


users = dict()
conversations = list()
print 'creating new users'

deffer  = UserSession(id='1', name='Deffer',  online=False)
chatter = UserSession(id='0', name='Chatter', online=False)
pluto   = UserSession(id='2', name='Pluto',   online=True, icon='indio')
alice   = UserSession(id='3', name='Alice',   online=True, icon='geisha')
users['']=chatter
users['0']=chatter
users['1']=deffer
users['2']=pluto
users['3']=alice

def createNewUid():
    import uuid
    return str(uuid.uuid4())

def getConversationById(talkid):
    for c in conversations:
        if c.id==talkid:
            return c
            
def findConversation(user1, user2):
    global conversations
    for c in conversations:
        if c.isFor(user1.id, user2.id):
            return c
    return None

def createConversation(userStarted, partner):
    global conversations
    c = Conversation(createNewUid(), userStarted, partner)
    conversations+=[c]    
    userStarted.conversations+=[c]
    return c

def getConversations(userid):
    global conversations
    res = list()
    for c in conversations:
        if userid in [c.partner1.id, c.partner2.id]:
            res.append(c)
    return res

def getUsersRequestingTalk(user):
    requests = list()
    cc = getConversations(user.id)
    for c in cc:
        if not c in user.conversations:            
            if (c.partnerRequestsTalk(user)):
                partner = c.getMyPartner(user.id)
            #if partner and (partner.online or len(c.messages)):
                print "Found "+partner.name+" wants to talk to "+user.name
                requests+=[partner]
    return requests
                
def getNewChanges(user, lastMsgIds, lastTime):    
    messages = dict()
    cc = getConversations(user.id)
    for c in cc:
        if c in user.conversations:
            if c.id in lastMsgIds:
                lastMsgId =int(lastMsgIds[c.id]); 
                msgs = c.getMessagesAfter(lastMsgId);
                if len(msgs)>0:
                    partner = c.getMyPartner(user.id)
                    print "Found new messages from "+partner.name+" to "+user.name
                    messages[c.id]=msgs
                '''messages.update(c.id, msgs)'''
    result = filterUsers(user, lastTime);
    return {"requests":result['requests'], "messages":messages, 
            "userchanges":result['users']}

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
    user = dbaccess.loadUser(userid);
    if not user:
        print 'creating user for cookie';
        user = UserSession(userid, 'Chatter')        
    users[userid] = user       
    print 'user loaded', user.toString(), 'users ref is', id(users)  
    return user

def makeNewUser():    
    userid=createNewUid()
    user = UserSession(userid, 'Chatter')        
    users[userid] = user       
    response.set_cookie('chatteruserid', userid)
    print 'creating new chatter ', userid
    return user


def filterUsers(forUser, since=1):
    ''' simple implementation '''
    
    ''' 1. those onliners matched by filter
        2. yourself. TODO remove
        3. me, pluto and alice
        4. conversation partners (that are offline and thus not matched in 1.)
        5. users, requesting talks but not matched by filter
    '''
    userid = forUser.id;
    result = list();
    matchedIds = set()
    requests = list()
    
    '1,2,3 - contact list filter'
    for user in users.values():
        if user.id != '' and user.id !='0':
            if user.id==userid or user.online or user.id=='1' or user.id=='2':
                if user.lastStatusChange > since:
                    result+=[user]
                    matchedIds.add(user.id)
                
    '4  -  conversation partners'
    for c in forUser.conversations:
        partner = c.getMyPartner(userid);
        if not partner.id in matchedIds and user.lastStatusChange > since:
            result+=[partner]
            matchedIds.add(partner.id)
    
    '5  -  requesting talks'
    for u in getUsersRequestingTalk(forUser):
        requests += [u.id]
        if not u.id in matchedIds:
            result+=[u]
            matchedIds.add(u.id)
             
    return {"users":result, "requests":requests}

def updatedUsers(since, additionalUsers):
    addit = list(additionalUsers)
    result = list()    
    for user in users.values():
        if user.lastStatusChange > since:
            result+=[user]
            if user.id in addit:
                addit.remove(user.id)
    for userid in addit:
        result+=[users[userid]]
        
    return result

@route('/')
@view('main')
def index():    
    user = getCurrentUser()
    print 'creating page for user', user.toString()
    result = filterUsers(user);
    response.headers['Cache-Control']='no-cache, must-revalidate'
    response.headers['Expires']='Sat, 26 Jul 1997 05:00:00 GMT'
    print users
    return dict(result=user, onliners=result["users"], 
                talks=user.conversations, allIcons=allUserIcons, 
                lastTime=model.timeMillis())


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
        message=Message(msgText, user) 
        c.messages.append(message)
        result = c.getMessagesAfter(int(lastIdStr))
        
        ''' if talking to pluto or alice - respond '''
        partner = c.getMyPartner(user.id)
        if partner==pluto:
            if msgText=='printdb':
                pmessage = Message(dbaccess.printStatus(), pluto)
                c.messages.append(pmessage)
            elif msgText=='show error':
                raise Exception('Artificial exception')              
            else:
                pmessage = Message(msgText+" :)", pluto)
                c.messages.append(pmessage)
        elif partner==alice:
            amessage = Message(getAliceBot().respond(msgText, user.id), alice); 
            c.messages.append(amessage)
            
        return json.dumps({'newTime':str(model.timeMillis()),
                           'messages':result}, cls=model.ComplexEncoder)
    else:
        return json.dumps({'newTime':str(model.timeMillis()), 'msg':"conversation is closed"})       



@route ('/ping.do', method='POST')
def ping():    
    user = getCurrentUser()
    if user == chatter:
        return json.dumps({'newTime':str(model.timeMillis())})
    
    req = request.POST.get('gettime')
    if req:
        print "returning server time"
        return json.dumps({'newTime':str(model.timeMillis())})
    
    user.lastPing = time.time()        
    msgIdMap = json.loads(request.POST.get('conversations'))
    lastTime =  request.POST.get('lastTime')
    print "request for changes from "+user.name        
    changes = getNewChanges(user, msgIdMap, int(lastTime))       
    return json.dumps({'newTime':str(model.timeMillis()),                        
                       'messages':changes['messages'],
                       'requests':changes['requests'],
                       'userchanges':changes['userchanges']}, cls=model.ComplexEncoder)
       


@route ('/request.do', method='POST')
def requestConversation():
    user = getCurrentUser()
    if user==chatter:
        user=makeNewUser()
    else:
        user.lastPing = time.time()
    partnerid = request.POST.get('partnerid').strip()
    print 'processing request for', user.toString(), 'talk to', partnerid 
    if partnerid in users:
        partner = users[partnerid]
        c = findConversation(user, partner)
        if c:
            if not c.acceptedBy(user.id):
                'accepting conversation'
                print 'user', user.name, 'accepts talk to', partner.name
                c.setAccepted(user.id)
                user.conversations+=[c]
                message=Message(model.MSG_ACCEPTED, user, type='s') 
                c.messages.append(message)
                
        else:
            c = createConversation(user, partner)
            'automatically accept by pluto'
            if partner.id=='2' and not c in partner.conversations:
                partner.conversations+=[c]
                c.setAccepted(partner.id)
            
                        
        htmlBody = template('conversation', talk=c, partner=partner)        
        return json.dumps({'talkid':c.id, 'myid':user.id, 'html':htmlBody, 
                           'msgId':c.getLastMsgId(), 'time':model.timeMillis()})
    else:
        return json.dumps({'msg':'User is offline'})
        
@route ('/decline.do', method='POST')
def declineConversation():
    
    user = getCurrentUser()
    if user==chatter:
        user=makeNewUser()
    else:
        user.lastPing = time.time()
    partnerid = request.POST.get('partnerid').strip()
    print 'processing decline from', user.toString(), 'of', partnerid 
    if partnerid in users:
        partner = users[partnerid]
        c = findConversation(user, partner)
        if c:
            message=Message(model.MSG_DECLINED, user, type='s') 
            c.messages.append(message)

@route ('/close.do', method='POST')
def closeConversation():
    user = getCurrentUser()
    if user==chatter:
        user=makeNewUser()
    else:
        user.lastPing = time.time()
    talkid = request.POST.get('talkid').strip()
    c = getConversationById(talkid)
    if not c:
        return json.dumps({'msg':'Conversation is already closed'})
    
    partner = c.getMyPartner(user.id)    
    print 'closing conversation of', user.toString(), 'with', partner.name 
    if not partner.id in users:
        return json.dumps({'msg':'User is offline'})
    
    'close conversation'
    if c in user.conversations:
        user.conversations.remove(c)
    c.setAccepted(user.id, value=False)
    
    'update status (to stop blinking on the partner\'s page)'
    user.lastStatusChange = model.timeMillis();
    
    'remove or send close message'        
    if not c.acceptedBy(partner.id):
        print 'removing conversation', c.partner1.name,'<-->', c.partner2.name
        if c in partner.conversations:
            partner.conversations.remove(c)
        conversations.remove(c)        
    else:
        'send CLOSED system message to partner'
        message=Message(model.MSG_CLOSED, user, type='s') 
        c.messages.append(message)

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
        print 'saving user to db (1)'
        dbaccess.saveUserInfo(user);        
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
        user.setIcon(inputIconName)
        dbaccess.saveUserInfo(user);
        return json.dumps({'myid':user.id})
    else:
        return json.dumps({'msg':"icon not set"})

@route ('/links.html',)
def staticLinks():
    send_file("links.html", root='web/')

@route('/usericons/:path#.+#')
def serve_icons(path):
    return static_file(path, root='web/icons', mimetype='image/png')
 
''' Just return scripts '''
@route('/scripts/:file')
@route('/styles/:file')
def serve_resources(file):
    try:
        if file.endswith(".gz"):
            response.headers['Content-Encoding'] = "gzip"
    except Exception as e:
        print(e)
            
    send_file(file, root='web/') 

if __name__=='__main__':
    import socket
    ipaddr = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][0]
    dbaccess.initDB();
    run(host=ipaddr, port=8080)
    
#run(host='10.3.3.59', port=8080)
#run(host='86.87.205.142', port=8080)