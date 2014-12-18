DS = 0
CS = 0
J = 0
C = 0
m = 0

import random

for i in range(1, 20000):
    if J > 0 : J = J-1
    if CS > 0 : CS = CS-1
    if DS > 0 : DS = DS-1
    if C > 0 : C = C-1
    if m > 0 : m = m-1
    
    if J == 0:
        print(i/100,'Jd')
        if DS < 150 : DS=150
        if CS < 150 : CS=150
        if C < 150  : C = 150
        J=800
    elif DS==0:
        print (i/100, 'DS')
        if CS < 150 : CS=150
        if J < 150 : J=150
        if C < 150  : C = 150        
        DS=1000
    elif CS==0:
        print (i/100, 'CS')
        if DS < 150 : DS=150
        if J < 150 : J=150
        if C < 150  : C = 150        
        CS=400
    elif C == 0:        
        print (i/100, 'Consecration!')
        if DS < 150 : DS=150
        if CS < 150 : CS=150
        if J < 150 : J=150
        C = 1000
        
        
    if m==0:
        m=304
        r = random.randrange(100)
        if r <= 40:
            DS = 0
            print (i/100, 'melee (proc)')
        else:
            print (i/100, 'melee')
        
        
