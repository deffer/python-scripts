import requests
import json
import time

wowItemUrl='http://us.battle.net/api/wow/item/'

print str(int(time.time() * 1000))

errorsCount = 0
successCount = 0
countBase = 120945

for i in range(1, 20001):
        itemid=countBase + i
        lastRequestTime = time.time()
        r = requests.get(wowItemUrl + str(itemid))
        #{status: "nok",reason: "unable to get item information."}
        #{status: "nok",reason: "When in doubt, blow it up. (page not found)"}
        jsonResp = r.json()
        if "status" in jsonResp and jsonResp["status"] == "nok":
                #print "ERROR", jsonResp["reason"], "\n"
                errorsCount += 1
                if (errorsCount % 50) == 0:
                        print "Errors - "+str(errorsCount)+" Last id "+str(itemid)
        else:
                #print r.text, "\n"
                requests.post("http://localhost:9200/wow/item/"+str(itemid), data=r.text)
                successCount += 1
                if (successCount % 50)==0:
                        print "fetched item "+str(itemid)

        toWait = time.time() - (lastRequestTime+0.1)
        if toWait>0:
                time.sleep(toWait)

print "FINISH. Errors - "+str(errorsCount)+" Success - "+str(successCount)+" Last id "+str(itemid)