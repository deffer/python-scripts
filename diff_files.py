import sys

file_all = open(r'G:\epbisbl\processing\epbises.txt')
file_new = open(r'G:\epbisbl\processing\epbises_new.txt')
file_rest = open(r'G:\epbisbl\processing\epbises_rest.txt', 'w')


set_new = set()
for line in file_new:
    set_new.add(line.strip())


for line in file_all:
    if not line.strip() in set_new:
        file_rest.write(line)
        
file_rest.close()
