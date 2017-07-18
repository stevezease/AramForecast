import csv
import json
from pprint import pprint

def win_chance(percentages, team):
	chance = 0.0
	for i in range(5):
		chance += float(percentages[team[i]])
	chance = chance / 5
	return chance

def naive_win_predictor():
	with open('percentage.json') as win_percentages:
		percentages = json.load(win_percentages)
		with open('cache.csv', 'rb') as arams:
			reader = csv.reader(arams, delimiter='\n')
			next(reader)
			correct_predictions = 0
			total_predictions = 0
			for row in reader:
				game_info = row[0].split(',')
				# indices for blue champ names
				blue_champs = [game_info[2],game_info[5],game_info[8],game_info[11],game_info[14]]

				# indices for purple champ names
				purple_champs = [game_info[17],game_info[20],game_info[23],game_info[26],game_info[29]]
				blue_win_chance = win_chance(percentages, blue_champs)
				purple_win_chance = win_chance(percentages, purple_champs)
				# print blue_champs, blue_win_chance
				# print purple_champs, purple_win_chance

				winner = ""

				if (blue_win_chance > purple_win_chance):
					winner = 'Blue'
				else:
					winner = 'Purple'

				# index of which side won
				if (winner == game_info[1]):
					correct_predictions += 1
				total_predictions += 1
			print "correct predictions: " + str(correct_predictions)
			print "total predictions :" + str(total_predictions)
			print "% of correct predictions: " + str(1.0 * correct_predictions / total_predictions)

def main():
	naive_win_predictor()

if __name__ == "__main__":
    main()
