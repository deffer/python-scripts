'''
Created on Dec 25, 2010

@author: clair
'''

import time
import json

msgIncrement = 0;

MSG_ACCEPTED = 'request for conversation has been ACCEPTED'
MSG_DECLINED = 'request for conversation has been DECLINED'
MSG_CLOSED   = 'conversation has been CLOSED'

def timeMillis(tm=None):
    if tm:
        return int(tm * 1000)
    else:
        return int(time.time() * 1000)


class UserSession:
    def __init__(self, id=0, name='Chatter', online=True, icon='astronauta'):
        self.id = str(id); 'uid, saved to cookie'
        self.icon = icon; 'icon name, general name without suffix and extention'
        self.conversations = list(); 'accept-list'
        self.country = None;
        self.online = online;
        self.lastPing = time.time();
        self.name = name;
        self.lastStatusChange = timeMillis() 
        
    def setName(self, name):
        if not (self.name == name):
            self.lastStatusChange = timeMillis() 
        self.name = name        

    def setIcon(self, icon):
        if not (self.icon == icon):
            self.lastStatusChange = timeMillis() 
        self.icon = icon
    
    def setOnlineStatus(self, online):
        if not (self.online==online):
            self.lastStatusChange = timeMillis() 
        self.online = online;
        
    def toString(self):
        return ""+self.name+"("+self.id+")"

class Conversation:
    def __init__(self, id, partnerStarted, partner2):
        self.id = id; 
        self.partner1 = partnerStarted; 'user, who requested conversation'
        self.partner2 = partner2;       'other user'
        self.messages=[]; 'all messages, normal and status ones'
        self.accepted = [partnerStarted.id]; 'users, accepted conversations'
    
    def acceptedBy(self, userid):
        return (userid in self.accepted)
            
    def setAccepted(self, userid, value=True):
        if value:
            if not userid in self.accepted:
                self.accepted += [userid]
        else:
            if userid in self.accepted:
                self.accepted.remove(userid)
    
    def isFor(self, userid1, userid2):
        return ({self.partner1.id, self.partner2.id}=={userid1, userid2})
            
                
    def getMyPartner(self, myId):
        if self.partner1.id==myId:
            return self.partner2
        elif self.partner2.id==myId:
            return self.partner1
        else:
            return None

    def getMessagesAfter(self, id, user=None):
        result = list()
        for msg in self.messages:
            if msg.id > id:
                if (user==None) or (user==msg.user): 
                    result+=[msg]
        return result
    
    def getLastMsgId(self): 
        if (len(self.messages)>0 and self.messages[-1]):
            print "request for last message id, returning",self.messages[-1].id 
            return self.messages[-1].id
        else:
            print "request for last message id, returning 0"
            return 0

    def getLastStatus(self, user):
        result = filter(lambda m: m.type=='s' and m.user.id==user.id, self.messages)
        return result[-1] if len(result)>0 else None
    
    'assuming _me_ is not having this conversation in his accept-list'
    def partnerRequestsTalk(self, me):        
        myStatus = self.getLastStatus(me);
        partner = self.getMyPartner(me.id);
        if (not myStatus):
            'have not accepted yet'
            return partner.online            
        if myStatus.text == MSG_CLOSED:
            'conversation has been closed by _me_, however partner wrote something more after that'            
            partnerWrites =self.getMessagesAfter(myStatus.id, partner);
            return len(partnerWrites)>0; 
        else:
            'unknown case, but let it be there'
            return partner.online
    
class Message:
    def __init__(self, text, user, type='n'):
        global msgIncrement
        self.text = text
        self.user = user
        msgIncrement+=1
        self.id = msgIncrement
        self.time = time.time()
        self.type = type

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Message):
            result ={'text':obj.text, 'userName':obj.user.name, 
                    'id':obj.id, 'time':timeMillis(obj.time), 'type':obj.type}
            if obj.type=='s':
                result['userid'] = obj.user.id 
            return result;
        elif isinstance(obj, UserSession):
            return {'icon':obj.icon, 'name':obj.name, 
                    'id':obj.id, 'online':obj.online}
        return json.JSONEncoder.default(self, obj)

if __name__=='__main__':
    msgIncrement = 3;