import requests
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
items = dict()
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
        itemsCache[item] = itemsCache[item]+1
    else:
        itemsCache[item] = 1
        r = requests.get(elasticItemUrl + str(item))
        jsonResp = r.json()
        if "found" in jsonResp and (jsonResp["found"]=="false" or jsonResp["found"]==False):
            if item in errorsCache:
                errorsCache[item] = errorsCache[item]+1
            else:
                errorsCache[item] = 1
        else:
            itemobject=jsonResp["_source"]
            itemobject["itemid"]=item
            items[item]=itemobject

    if (count % 1000)==0:
        print "Errors - "+str(len(errorsCache))+" Last id "+str(id)

#    recodedf.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (a["auc"], a["item"], a["owner"], a["ownerRealm"], a["bid"], a["buyout"], a["quantity"], a["timeLeft"], a["seed"], a["context"]))
    recodedf.write("%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n" % (a["auc"], a["item"], a["owner"], a["ownerRealm"], a["bid"], a["buyout"], a["quantity"], a["timeLeft"], a["seed"], a["context"]))
    
recodedf.close()


tosave=[]
tosavefew=[]
for d in sorted(itemsCache.items(), key=lambda(k,v): v, reverse=True):
    if d[1]>100:
        print "Item "+ str(d[0])+": "+str(d[1])
        tosavefew.append(items[d[0]])

    tosave.append(items[d[0]])

itemsf = codecs.open("items.json", "w", "utf-8")
json.dump(tosave, itemsf)
itemsf.close()

itemsfew = codecs.open("itemsfew.json", "w", "utf-8")
json.dump(tosavefew, itemsfew)
itemsfew.close()



print "Auctions - "+str(count)+", items - "+str(len(itemsCache))
