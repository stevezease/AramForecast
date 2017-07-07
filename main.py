import requests
import json
import csv
import time
## Constants
APIKey = "RGAPI-b8811a1f-977c-468f-a8d0-4284eb3752f7"
region = "na1"


Ratelimit2m = 100
Ratelimit1s = 20
matchid = 2541517190
timer2m = time.time()
timer1s = time.time()
starttime = 0
apicalls = 0
callsPer2m = 0
callsPerS = 0

def rowGenerator(matchNum):
	row = []
	##win = ""
	row.append(str(matchNum))
	if(str(matchData["participants"][0]["stats"]["win"]) == "True"):
		row.append("Blue")
	else:
		row.append("Purple")

	for y in range(1, 11):
		row.append(champNames[matchData["participants"][y-1]["championId"]])
		row.append(spellNames[matchData["participants"][y-1]["spell1Id"]])
		row.append(spellNames[matchData["participants"][y-1]["spell2Id"]])	
	##	win = str(win) + "," +str(matchData["participants"][y-1]["stats"]["win"])
	##print win
	return row






##csv intialization
fieldnames = ['MatchId']
fieldnames.append('WinningTeam')
for y in range(1, 11):
	fieldnames.append("Champion"+str(y))
	fieldnames.append("Champ"+str(y)+"Spell1")
	fieldnames.append("Champ"+str(y)+"Spell2")
with open('aram.csv', 'wb') as aramfile:
	writer = csv.writer(aramfile)
	writer.writerows([fieldnames])

with open('classic.csv', 'wb') as classicfile:
	writer = csv.writer(classicfile)
	writer.writerows([fieldnames])



starttime = time.time()

##Get static data
static = requests.get("https://global.api.riotgames.com/api/lol/static-data/NA/v1.2/champion?api_key=" + APIKey)
staticjson = static.json();
champNames = {}
for key in staticjson["data"]:
	champNames[staticjson["data"][key]["id"]] = staticjson["data"][key]["name"]

static2 = requests.get("https://na1.api.riotgames.com/lol/static-data/v3/summoner-spells?locale=en_US&dataById=false&api_key=" + APIKey)
staticjson2 = static2.json();
spellNames = {}
for key in staticjson2["data"]:
	spellNames[staticjson2["data"][key]["id"]] = staticjson2["data"][key]["name"]

for x in range(0, 10):

	##if(callsPer2m > (Ratelimit2m-3)):
	if(callsPer2m > (25)):
		print "ZzZz.. Don't want to get blacklisted\t" + "Sleeping:" + str(130-(time.time()-timer2m))
		time.sleep(130-(time.time()-timer2m))
	#Probably dont need to worry about this but including this anyway
	if(callsPerS > (Ratelimit1s-2)):
		sleep(2)

	apicalls = apicalls + 1
	##print "Cycle Time: " + str( time.strftime('%H:%M:%S', time.gmtime(time.time()-lasttime))) + "\t" + "ApiCalls since last cycle:" + str(apicalls) + "\t\t\t\ttotal elasped time: " + str( time.strftime('%H:%M:%S', time.gmtime(time.time()-starttime)))
	
	
	matchid = matchid+1
	r = requests.get("https://" + region + ".api.riotgames.com/lol/match/v3/matches/" + str(matchid)+"?api_key="+APIKey) 
	
	limits = ((r.headers)['X-Rate-Limit-Count']).split(',')
	callsPerS= int((limits[1].split(':'))[0]);
	callsPer2m= int((limits[0].split(':'))[0]);
	print callsPer2m
	if(callsPer2m == 1):
		timer2m = time.time()
	if(callsPerS == 1):
		timer1s = time.time()

	matchData =  r.json()

	##matchData["participants"][0]["championId"]
	if(r.status_code == 200):
		print str(matchid) + ": " + matchData["gameMode"]
		if(matchData["queueId"]==65):
			with open('aram.csv', 'a') as aramfile:
				writer = csv.writer(aramfile)
				writer.writerows([rowGenerator(matchid)])
		elif((matchData["queueId"]==2)or(matchData["queueId"]==14)):
			with open('classic.csv', 'a') as classicfile:
				writer = csv.writer(classicfile)
				writer.writerows([rowGenerator(matchid)])
	elif(r.status_code == 403):
		print "Well Shit you just got blacklisted"
		break
	elif(r.status_code == 429):
		print "STAHPP!"
		break
	else:
		print str(matchid) + ": " + str(r.status_code)
