#!/usr/bin/env python

import time, random, math

#number of attempts
no = 10000

v1 = 0
v2 = 1
MatchDeltas = ((0,1), (0,-1), (1,0), (-1,0))

def _Compare(i, j, color, kind):
    if MatchMap.has_key((i,j)):
        return    
    if (i,j) in tmpPoints:
        if Field[i,j] == color:
                MatchMap[i,j] = kind
                for (dx, dy) in MatchDeltas:
                    _Compare(i+dx, j+dy, color, kind)

for m in (9,10,8,7,6):
    for n in (13, 12, 11):
        print m, n
        filename = "balance/"+str(m)+"x"+str(n)+".def"
        f = file(filename, "wt")
        f.write("MasterChef{\n")
        f.write("  width = "+str(m)+"\n")
        f.write("  height = "+str(n)+"\n")
        
        f.write("  group {rate = '0.0' size = '0' max = '0' min = '0'}\n")
        
        for pp in range(100):
            print pp
            p = (pp+1)*0.01
            
            NonZero = 0
            MaxSum = 0
            AveSum = 0
            AveSum2 = 0
            MinSize = m*n
            MaxSize = 0
        
            for ii in range(no):
                #filling the field
                Field = {}
                for i in range(m):
                    for j in range(n):
                        if random.random() < p:
                            Field[i,j] = v2
                        else:
                            Field[i,j] = v1
                            
                #calculating max group size
                MatchMap = {}
                curKind = 0
                tmpPoints = filter(lambda x: Field[x] == v2, Field.keys())
                for (i,j) in tmpPoints:
                    if not MatchMap.has_key((i,j)):
                        _Compare(i, j, Field[(i,j)], curKind)
                        curKind +=1
                tmpChains = map(lambda x: filter(lambda y: MatchMap[y] == x, MatchMap.keys()),
                                range(curKind))
                tmpLens = map(lambda x: len(x), tmpChains)
                if tmpLens != []:
                    MaxLen = max(tmpLens)
                    AveLen = reduce(lambda a, b: a+b, tmpLens, 0)/len(tmpLens)
                    AveLen2 = MaxLen - math.sqrt(reduce(lambda a, b: a+(MaxLen-b)**2, tmpLens, 0)/len(tmpLens))
                else:
                    MaxLen = 0
                    AveLen = 0
                    AveLen2 = 0
                    
                MinSize = min(MinSize, MaxLen)
                MaxSize = max(MaxSize, MaxLen)
                MaxSum += MaxLen
                AveSum += AveLen
                AveSum2 += AveLen2
                if MaxLen >0:
                    NonZero += 1
                
            f.write("  group {rate = '"+str(p)+"' size = '"+str(1.0*AveSum/no)+
                    "' min = '"+str(MinSize)+"' max = '"+str(MaxSize)+"'}\n")
            #print p, ',', 1.0*AveSum/no, ',', 1.0*AveSum2/no, ',', 1.0*MaxSum/no, ',', NonZero, ',', MinSize, ',', MaxSize
        f.write("}\n")
        

