import itertools

#s = 'Yersinia pestis biovar Mediaevalis str. Harbin 35'.split()
s = 'Human endogenous retro virus'.split()
r = list(itertools.permutations(s, 2));
print(len(r))

for i in range(0, len(r)):
    #if i % 100 == 0:
        print(r[i])
