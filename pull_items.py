import requests

wowItemUrl='http://us.battle.net/api/wow/item/'

for i in range(1, 5):
	itemid=18800+i
	r=requests.get(wowItemUrl + str(itemid))
	print r.text
	