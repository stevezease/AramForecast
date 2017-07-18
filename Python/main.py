import requests
import operator
import json
import csv
import time
import os
from queue import*

## Constants
APIKey = "RGAPI-1f43700f-6788-4f91-8cf8-6eb6f50e8752"
region = "na1"
Ratelimit2m = 100 #your 2 minute api rate limit
Ratelimit1s = 20

##Global resources
iterations = 10000   ##number of times you want the loop to run
matchid = 2548124361 ##Backup Starting matchid
champNames = {}		##Dictionary containing id -> champion name
spellNames = {}		##Dictionary containing id -> spell name
itemNames = {}		##Dictionary containing id -> item name
masteryNames = {}
queuetracker = {}	##Dictionary that keeps a running sum of all encountered match types

#champion stats tracker
aramchampfreq = {}
aramwinrate = {}
aramitemwinrate = {}
aramitemfrequency = {}



##Functions


#
def load():
	global queuetracker
	global aramchampfreq
	global aramwinrate
	global aramitemwinrate
	global aramitemfrequency
	global matchid
	if(os.path.isfile("queuetracker.txt") and (os.stat("queuetracker.txt").st_size != 0)):
		with open('queuetracker.txt') as json_file:  
			queuetracker = json.load(json_file)
	queuetracker = {int(k):int(v) for k,v in queuetracker.items()}
	if(os.path.isfile("aramchampfreq.txt") and (os.stat("aramchampfreq.txt").st_size != 0)):
		with open('aramchampfreq.txt') as json_file:  
			aramchampfreq = json.load(json_file)
	if(os.path.isfile("aramwinrate.txt") and (os.stat("aramwinrate.txt").st_size != 0)):
		with open('aramwinrate.txt') as json_file:  
			aramwinrate = json.load(json_file)
	if(os.path.isfile("aramitemwinrate.txt") and (os.stat("aramitemwinrate.txt").st_size != 0)):
		with open('aramitemwinrate.txt') as json_file:  
			aramitemwinrate = json.load(json_file)
	if(os.path.isfile("aramitemfrequency.txt") and (os.stat("aramitemfrequency.txt").st_size != 0)):		
		with open('aramitemfrequency.txt') as json_file:  
			aramitemfrequency = json.load(json_file)
	if(os.path.isfile("matchid.txt") and (os.stat("matchid.txt").st_size != 0)):		
		with open('matchid.txt', 'r') as f:
			matchid = int(f.read())

def save():
	with open('queuetracker.txt', 'w') as outfile:
		json.dump(queuetracker, outfile)
	with open('aramchampfreq.txt', 'w') as outfile:
		json.dump(aramchampfreq, outfile)
	with open('aramwinrate.txt', 'w') as outfile:
		json.dump(aramwinrate, outfile)
	with open('aramitemwinrate.txt', 'w') as outfile:
		json.dump(aramitemwinrate, outfile)
	with open('aramitemfrequency.txt', 'w') as outfile:
		json.dump(aramitemfrequency, outfile)
	with open('matchid.txt', 'w') as outfile:
		outfile.write(str(matchid+1))

			
def aramChampTally(matchData):
	for y in range(0, 10):
		name = champNames[matchData["participants"][y]["championId"]]
		if ((name in aramitemwinrate) == False):
				aramitemwinrate[name] = {}
				aramitemfrequency[name] = {}
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
		for x in range(0,6):
				if (matchData["participants"][y]["stats"]["item"+str(x)] != 0):
					item = itemNames[matchData["participants"][y]["stats"]["item"+str(x)]]
					if item in aramitemfrequency[name]:
						aramitemfrequency[name][item] += 1
					else:
						aramitemfrequency[name][item] = 1
		if name in aramchampfreq:
			aramchampfreq[name]+=1
		else:
			aramchampfreq[name]=1

##generates rows
def rowGenerator(matchNum,matchData):
	keystone = [6161,6162,6164,6261,6262,6263,6361,6362,6363]
	row = []
	row.append(str(matchNum))
	if(str(matchData["participants"][0]["stats"]["win"]) == "True"):
		row.append("Blue")
	else:
		row.append("Purple")
	for y in range(1, 11):
		participant = matchData["participants"][y-1]
		row.append(participant["highestAchievedSeasonTier"])
		row.append(champNames[participant["championId"]])
		row.append(spellNames[participant["spell1Id"]])
		row.append(spellNames[participant["spell2Id"]])
		printedmastery = False	
		if("masteries" in participant):
			for x in range(0, len(participant["masteries"])):
				mastery = participant["masteries"][x]
				if(mastery['rank'] == 1)and(mastery['masteryId'] in keystone):
						row.append(masteryNames[mastery['masteryId']])
						printedmastery = True
						break
		if(printedmastery == False):
			row.append("N/A")
		for x in range(0,6):
			if (participant["stats"]["item"+str(x)] != 0):
				row.append(itemNames[participant["stats"]["item"+str(x)]])
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
		fieldnames.append("Champ"+str(y)+"KeyStone")
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
	
	static2 = requests.get("https://kr.api.riotgames.com/lol/static-data/v3/summoner-spells?locale=en_US&dataById=false&api_key=" + APIKey)
	if (static2.status_code == 200):
		staticjson2 = static2.json();
		for key in staticjson2["data"]:
			spellNames[staticjson2["data"][key]["id"]] = staticjson2["data"][key]["name"]

	static3 = requests.get("https://kr.api.riotgames.com/lol/static-data/v3/items?locale=en_US&api_key=" + APIKey)
	if (static3.status_code == 200):
		staticjson3 = static3.json();
		for key in staticjson3["data"]:
			if "name" in staticjson3["data"][key]:
				itemNames[staticjson3["data"][key]["id"]] = staticjson3["data"][key]["name"]

	static4 = requests.get("https://kr.api.riotgames.com/lol/static-data/v3/masteries?locale=en_US&api_key=" + APIKey)
	if (static4.status_code == 200):
		staticjson4 = static4.json();
		for key in staticjson4["data"]:
			if "name" in staticjson4["data"][key]:
				masteryNames[staticjson4["data"][key]["id"]] = staticjson4["data"][key]["name"]

def summary():
	print "\nData Collection Complete\t\t\t\tTotal Elasped Time: " + str( time.strftime('%H:%M:%S', time.gmtime(time.time()-starttime)))
	print "Here are the stats:\n"
	print "1. Queue/Match type Frequency:"
	for key in queuetracker:
		if key in queuename:
			print str(queuename[key])+": "+ str(queuetracker[key] )
	refinedfreq = sorted(aramchampfreq.items(), key=operator.itemgetter(1), reverse=True)

	print "\n\n2. Champion Frequency\n"
	for key in refinedfreq:
		print str(key[0])+": " + str(key[1])
	refinedawr = {}

	print "\n\n3. Champion Win Rates\n"
	for key in aramwinrate:
		refinedawr[key] = round((float(aramwinrate[key][0])/float(aramwinrate[key][1]))*100,2)

	winrates = sorted(refinedawr.items(), key=operator.itemgetter(1), reverse=True)
	for key in winrates:
		print '{:60} {:>10}'.format((str(key[0]) + ": " + str(key[1])+"%"),(str(aramwinrate[key[0]][0])+"/"+str(aramwinrate[key[0]][1])))

	print "\n\n4. Item Win Rates"
	for key in aramitemwinrate:
		temp = aramitemwinrate[key]
		itemwinrate = {}
		for item in temp:
			itemwinrate[item] = round((float(temp[item][0])/float(temp[item][1]))*100,2)
		itemwinrates = 	sorted(itemwinrate.items(), key=operator.itemgetter(1), reverse=True)
		itemfrequency  = sorted(aramitemfrequency[key].items(), key=operator.itemgetter(1), reverse=True)
		print "\n\n" + key  
		print "Item\t\t\t\t\t   Pick Rate\t Win %\t Win Frac"
		for x in range(0,min(len(itemfrequency),10)):
			print '{:40} {:>10} {:>10} {:>10}'.format(str(itemfrequency[x][0]),(str(str(itemfrequency[x][1])+"/"+str(aramchampfreq[key]))),(str(itemwinrate[itemfrequency[x][0]])+"%"),(str(temp[itemfrequency[x][0]][0]) + "/" + str(temp[itemfrequency[x][0]][1])))


if __name__ == "__main__":
	if(os.path.isfile("aram.csv")==False):
		csvGenerator()
	staticDataGenerator()
	load()
	#variable initialization
	apicalls = 0
	starttime = time.time()
	timer2m = time.time()
	timer1s = time.time()
	callsPer2m = 0
	callsPerS = 0
	aramtracker = False
	counter = 0
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
		
		if('X-Rate-Limit-Count' in r.headers):
			limits = ((r.headers)['X-Rate-Limit-Count']).split(',')
			callsPerS= int((limits[1].split(':'))[0]);
			callsPer2m= int((limits[0].split(':'))[0]);
		else:
			callsPerS+=1
			callsPer2m+=1

		if(callsPer2m == 1):
			timer2m = time.time()
		if(callsPerS == 1):
			timer1s = time.time()

		matchData =  r.json()
		if(counter>90):
			print "In a Dry Zone. Jumping MatchId's"
			counter = 0
			matchid+= 2500
		if(r.status_code == 200):
			key = matchData["queueId"]
			if(key in queuename):
				if key in queuetracker:
					queuetracker[key]+=1
				else:
					queuetracker[key]=1

				print str(apicalls)+ ". " + str(matchid) + "\tMode: " + '{0: <15}'.format(matchData["gameMode"]) + "\tQueue: " + '{0: <45}'.format(queuename[matchData["queueId"]]) + "\tLimit: " + str(callsPer2m) 
				if(key==65):
					counter = 0
					with open('aram.csv', 'a') as aramfile:
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
		counter += 1
	summary()