import bottle
from bottle import route, run, send_file, redirect, request, response
#from sessions import *
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
    sss[result.id] = result
    response.set_cookie(SESSION_ID, result.id, path='/')
    print('Created session: ' + result.id)
    return result

def removeSession(ses = None):
    if not ses:
        ses = getSession()
    if ses and ses.id in sessions:
        print('Removed session: ' + str(ses.id))
        del sss[ses.id]
        return True
    else:
        return False

bottle.debug(True)

@route('/')
def root():
    ses = getSession()
    if not ses:
        redirect('/login')
    else:
        redirect('/store/products')

@route('session/remove')
def onSessionRemove():
    removeSession()
    redirect('/')

@route('/login/perform')
def performLogin():
    if 'name' in request.params:
        ses = createSession()
        ses.name = request.params['name']
        return r'U are logged in as{name}, proceed to <a href="/store/products">store</a>'.format(name=ses.name)
    else:
        return r'U are not logged in, please <a href="/login">repeat</a>'

@route('/login')
def login():
    if not getSession():
        f = open(r'login.html')
        str = f.read();
        f.close()
        return str;
    else:
        return r'U already logged in, <a href="session/remove">Click here to log off</a>'

@route('/store/products')
def products():
    if getSession():
        return 'Ice cream'
    else:
        redirect('/login')

@route('/static/:filename')
def static_file(filename):
    send_file(filename, root=r'c:\temp')


run(host='localhost', port=8090)
