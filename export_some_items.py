#import requests
import io
import codecs
import json
import time

#wowItemUrl='http://us.battle.net/api/wow/item/'
elasticItemUrl='http://localhost:9200/wow/item/'

count = 0
errorsCount = 0
successCount = 0

fname="./auctions.json"

itemsCache = dict()
errorsCache = set()

f = io.open(fname, encoding="utf-8")
jsonContent = json.load(f)
if not "auctions" in jsonContent:
    print "No auctions section"
    exit()

if not "auctions" in jsonContent["auctions"]:
    print "No auctions in auctions section"
    exit()

auctions = jsonContent["auctions"]["auctions"]

recodedf = codecs.open("auctions.csv", "w", "utf-8")
#json.dump(["aucid", "itemid", "owner", "realm", "bid", "buyout", "quantity", "timeleft", "seed", "context"], recodedf)
recodedf.write("aucid|itemid|owner|realm|bid|buyout|quantity|timeleft|seed|context\n")
for a in auctions:
    #print json.dumps(a)
    item = a["item"]
    id = a["auc"]
    count += 1
    if item in itemsCache:
        #print "item found "+str(item)+" count "+str(itemsCache[item])
        itemsCache[item] = itemsCache[item]+1
    else:
        itemsCache[item] = 1

    if (count % 1000)==0:
        print "Errors - "+str(len(errorsCache))+" Last id "+str(id)

#    recodedf.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (a["auc"], a["item"], a["owner"], a["ownerRealm"], a["bid"], a["buyout"], a["quantity"], a["timeLeft"], a["seed"], a["context"]))
    recodedf.write("%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n" % (a["auc"], a["item"], a["owner"], a["ownerRealm"], a["bid"], a["buyout"], a["quantity"], a["timeLeft"], a["seed"], a["context"]))
    

recodedf.close()
for d in sorted(itemsCache.items(), key=lambda(k,v): v, reverse=True):
    if d[1]>1:
        print "Item "+ str(d[0])+": "+str(d[1])

print "Auctions - "+str(count)+", items - "+str(len(itemsCache))