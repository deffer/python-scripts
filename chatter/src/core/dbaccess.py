'''
Created on Dec 5, 2010
@author: clair
'''

import sqlite3, time, sys;
#from __future__ import print_function

conn = sqlite3.connect('data/db')
conn.row_factory = sqlite3.Row


def initDB():
    c = conn.cursor()

    try:
        c.execute('''create table users
        (cookid text primary key, name text, icon text, lastdbtime time, lastonline time)''')

        c.execute('''create table messages
        (msgid long primary key, msg text, userfrom text, userto text, msgtime time,
        FOREIGN KEY (userfrom) REFERENCES users(cookid),
        FOREIGN KEY (userto) REFERENCES users(cookid))''')

        conn.commit()
        return 1
    except sqlite3.OperationalError as ex:
        print 'db is already initialized:', ex
        return selectMaxMsgId()
    finally:
        c.close()
        

def selectMaxMsgId():
    c = conn.cursor()
    try:
        c.execute('select max(msgid) from messages');
    
        r = c.fetchone()
        if r and r[0]:
            return int(r[0])
        else:
            print "message table is empty, returning 1 as maximum id"
            return 1
    except sqlite3.OperationalError as ex:
        print "Error reading messages table, returning 1 as maximum id"
        return 1
    finally:
        c.close()    
        
def saveUserInfo(user):
    print 'saving user to db (2)'
    c = None
    try:
        existing = loadUser(user.id)
        c = conn.cursor()
        if existing:
            print 'db update'+user.name
            c.execute('update users set name=?, icon=?, lastdbtime=?, lastonline=? where cookid=?', 
                  (user.name, user.icon, time.time(), user.lastPing, user.id));
        else:
            print 'db insert'+user.name            
            c.execute('''insert into users values (?,?,?,?,?)''', 
                  (user.id, user.name, user.icon, time.time(), user.lastPing));
        conn.commit()
    except sqlite3.OperationalError as ex:
        print 'Error sqlite3 while saving user:', ex
    except Exception, e:
        print 'Exception while saving user:', e
    except:
        print 'Error while saving user:', sys.exc_info()
    finally:
        if c: c.close()
    

def loadUser(id):
    c = conn.cursor()
    c.execute('select * from users where cookid=?', [id]);
    
    r = c.fetchone()
    if r and r['cookid'] and r['name'] and r['icon']:
        from chatter import UserSession
        user = UserSession(r['cookid'], r['name'], True)
        user.setIcon(r['icon'])
        c.close()
        return user
    else:
        return None    

'''class Writable:
    def __init__(self):
        self.str = ''
        
    def write(self, text):
        self.str+=text
'''        
def printStatus():
    c = conn.cursor()
    c.execute('select * from users order by lastdbtime DESC');
    print "status"
    count = 0;
    string = ''
    for row in c:
        count+=1
        if count<=10:
            string+="{0} %{2}% {1}\n".format(row['name'], row['cookid'], row['icon'])
            print row
    if count>10:
        string += 'TOTAL: '+str(count)+' entries'
    c.close()
    return string

if __name__=='__main__':
    c = conn.cursor()
    c.execute('select * from users order by lastdbtime DESC');
    row = c.fetchone();
    print "{0} %{2}% ({1})".format(row['name'], row['cookid'], row['icon'])
'''initDB()'''