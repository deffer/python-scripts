'''
Created on Jul 21, 2010

@author: Irina Benediktovich
'''
from bottle import response, request
import uuid
class Session:
    pass

SESSION_ID = 'session.id'

# str > Session
sss  = dict()

def getSession():
    id = request.COOKIES.get(SESSION_ID)
    print('Looking for session: ' + str(id))
    if id and id in sss:
        return sss[request.COOKIES[SESSION_ID]]
    else:
        return None

def createSession():
    result = Session()
    result.id = str(uuid.uuid4());
    result.params = dict()
    sss[result.id] = result
    response.set_cookie(SESSION_ID, result.id, path='/')
    print('Created session: ' + result.id)
    return result

def getOrCreateSession():
    result = getSession()
    if not result:
        result = createSession()
    return result

def removeSession(ses = None):
    if not ses:
        ses = getSession()
    if ses and ses.id in sss:
        print('Removed session: ' + str(ses.id))
        del sss[ses.id]
        return True
    else:
        return False

