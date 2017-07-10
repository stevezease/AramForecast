import requests
import operator
import json
import csv
import time
from queue import*

## Constants
APIKey = "RGAPI-49f885be-ce13-4194-8dfb-8a985d8302f4"
region = "na1"
Ratelimit2m = 100 #your 2 minute api rate limit
Ratelimit1s = 20

##Global resources
iterations = 90   ##number of times you want the loop to run
matchid = 2542998351 ##Starting matchid
champNames = {}		##Dictionary containing id -> champion name
spellNames = {}		##Dictionary containing id -> spell name
itemNames = {}		##Dictionary containing id -> item name
queuetracker = {}	##Dictionary that keeps a running sum of all encountered match types

#champion stats tracker
aramchampfreq = {}
aramwinrate = {}
aramitemwinrate = {}




##Functions


#

def aramChampTally(matchData):
	for y in range(0, 10):
		name = champNames[matchData["participants"][y]["championId"]]
		if ((name in aramitemwinrate) == False):
				aramitemwinrate[name] = {}
		if(str(matchData["participants"][y]["stats"]["win"]) == "True"):
			if name in aramwinrate:
				aramwinrate[name][0] += 1
				aramwinrate[name][1] += 1
			else: 
				aramwinrate[name] = [1,1]

			for x in range(0,6):
				if (matchData["participants"][y]["stats"]["item"+str(x)] != 0):
					item = itemNames[matchData["participants"][y]["stats"]["item"+str(x)]]
					if item in aramitemwinrate[name]:
						aramitemwinrate[name][item][0] +=1
						aramitemwinrate[name][item][1] +=1
					else:
						aramitemwinrate[name][item] = [1,1]
				
		else:
			if name in aramwinrate:
				aramwinrate[name][1] += 1
			else: 
				aramwinrate[name] = [0,1]

			for x in range(0,6):
				if (matchData["participants"][y]["stats"]["item"+str(x)] != 0):
					item = itemNames[matchData["participants"][y]["stats"]["item"+str(x)]]
					if item in aramitemwinrate[name]:
						aramitemwinrate[name][item][1] +=1
					else:
						aramitemwinrate[name][item] = [0,1]

		if name in aramchampfreq:
			aramchampfreq[name]+=1
		else:
			aramchampfreq[name]=1

##generates rows
def rowGenerator(matchNum,matchData):
	row = []
	row.append(str(matchNum))
	if(str(matchData["participants"][0]["stats"]["win"]) == "True"):
		row.append("Blue")
	else:
		row.append("Purple")
	for y in range(1, 11):
		row.append(matchData["participants"][y-1]["highestAchievedSeasonTier"])
		row.append(champNames[matchData["participants"][y-1]["championId"]])
		row.append(spellNames[matchData["participants"][y-1]["spell1Id"]])
		row.append(spellNames[matchData["participants"][y-1]["spell2Id"]])	
		for x in range(0,6):
			if (matchData["participants"][y-1]["stats"]["item"+str(x)] != 0):
				row.append(itemNames[matchData["participants"][y-1]["stats"]["item"+str(x)]])
			else:
				row.append("N/A")
	return row


##csv intialization
def csvGenerator():
	fieldnames = ['MatchId']
	fieldnames.append('WinningTeam')
	for y in range(1, 11):
		fieldnames.append("Champ"+str(y)+"Rank")
		fieldnames.append("Champion"+str(y))
		#fieldnames.append("Champ"+str(y)+"KeyStone")
		fieldnames.append("Champ"+str(y)+"Spell1")
		fieldnames.append("Champ"+str(y)+"Spell2")
		for x in range(0,6):
			fieldnames.append("Champ"+str(y) + "item" + str(x))
	
	with open('aram.csv', 'wb') as aramfile:
		writer = csv.writer(aramfile)
		writer.writerows([fieldnames])

	with open('classic.csv', 'wb') as classicfile:
		writer = csv.writer(classicfile)
		writer.writerows([fieldnames])




def staticDataGenerator():
	static = requests.get("https://global.api.riotgames.com/api/lol/static-data/NA/v1.2/champion?api_key=" + APIKey)
	if (static.status_code == 200):
		staticjson = static.json();
		for key in staticjson["data"]:
			champNames[staticjson["data"][key]["id"]] = staticjson["data"][key]["name"]
	
	static2 = requests.get("https://na1.api.riotgames.com/lol/static-data/v3/summoner-spells?locale=en_US&dataById=false&api_key=" + APIKey)
	if (static2.status_code == 200):
		staticjson2 = static2.json();
		for key in staticjson2["data"]:
			spellNames[staticjson2["data"][key]["id"]] = staticjson2["data"][key]["name"]

	static3 = requests.get("https://na1.api.riotgames.com/lol/static-data/v3/items?locale=en_US&api_key=" + APIKey)
	if (static3.status_code == 200):
		staticjson3 = static3.json();
		for key in staticjson3["data"]:
			if "name" in staticjson3["data"][key]:
				itemNames[staticjson3["data"][key]["id"]] = staticjson3["data"][key]["name"]

def summary():
	print "\nData Collection Complete\t\t\t\tTotal Elasped Time: " + str( time.strftime('%H:%M:%S', time.gmtime(time.time()-starttime)))
	print "Here are the stats:\n"
	print "1. Queue/Match type Frequency:"
	for key in queuetracker:
		if key in queuename:
			print str(queuename[key])+": "+ str(queuetracker[key] )

	refinedawr = {}
	print "2. Champion Win Rates\n"
	for key in aramwinrate:
		refinedawr[key] = float(aramwinrate[key][0])/float(aramwinrate[key][1])

	winrates = sorted(refinedawr.items(), key=operator.itemgetter(1), reverse=True)
	for key in winrates:
		print str(key[0]) + ": " + str(key[1])

	print "3. Item Win Rates\n"
	for key in aramitemwinrate:
		temp = aramitemwinrate[key]
		itemwinrate = {}
		for item in temp:
			itemwinrate[item] = float(temp[item][0])/float(temp[item][1])
		itemwinrates = 	sorted(itemwinrate.items(), key=operator.itemgetter(1), reverse=True)
		print "\n\n" + key 
		for x in range(0,min(len(itemwinrates),10)):
			print str(itemwinrates[x][0]) + ": " + str(itemwinrates[x][1])


if __name__ == "__main__":
	
	csvGenerator()
	staticDataGenerator()
	
	#variable initialization
	apicalls = 0
	starttime = time.time()
	timer2m = time.time()
	timer1s = time.time()
	callsPer2m = 0
	callsPerS = 0
	aramnum = 0
	normnum = 0 
	key = 0

	##main loop
	for x in range(0, iterations):
		if(callsPer2m > (Ratelimit2m-10)):
			print "ZzZz.. Don't want to get blacklisted\t" + "Sleeping:" + str(130-(time.time()-timer2m))
			time.sleep(130-(time.time()-timer2m))
		if(callsPerS > (Ratelimit1s-2)):
			sleep(2)

		apicalls = apicalls + 1
		matchid = matchid+1

		r = requests.get("https://" + region + ".api.riotgames.com/lol/match/v3/matches/" + str(matchid)+"?api_key="+APIKey) 
		
		limits = ((r.headers)['X-Rate-Limit-Count']).split(',')
		callsPerS= int((limits[1].split(':'))[0]);
		callsPer2m= int((limits[0].split(':'))[0]);
		if(callsPer2m == 1):
			timer2m = time.time()
		if(callsPerS == 1):
			timer1s = time.time()

		matchData =  r.json()
		
		
		if(r.status_code == 200):
			key = matchData["queueId"]
			if key in queuetracker:
				queuetracker[key]+=1
			else:
				queuetracker[key]=1

			print str(apicalls)+ ". " + str(matchid) + "\tMode: " + '{0: <15}'.format(matchData["gameMode"]) + "\tQueue: " + '{0: <45}'.format(queuename[matchData["queueId"]]) + "\tLimit: " + str(callsPer2m) 
			if(key==65):
				with open('aram.csv', 'a') as aramfile:
					aramnum = aramnum+1
					writer = csv.writer(aramfile)
					writer.writerows([rowGenerator(matchid,matchData)])
				aramChampTally(matchData)
			elif((key==2)or(key==14)):
				with open('classic.csv', 'a') as classicfile:
					normnum = normnum +1
					writer = csv.writer(classicfile)
					writer.writerows([rowGenerator(matchid,matchData)])
		elif(r.status_code == 403):
			print "Well Shit you just got blacklisted"
			break
		elif(r.status_code == 429):
			print "STAHPP! You gon get blacklisted soon"
			break
		else:
			print str(apicalls)+ ". " +str(matchid) + ": " + str(r.status_code)

	summary()