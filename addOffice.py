file = open('c:/Dowload/checks/US/output_justnumbers.txt')
outF=open('c:/Dowload/checks/US/output_justnumersandoffices.txt', 'w')

for line in file:
    outF.write(line.strip()+"\tUSPTO\n")

    
outF.close()
