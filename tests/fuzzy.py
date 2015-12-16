#!/usr/bin/env python
import sys; sys.path.append("..")
import random
import logging
from fireplace.cards.heroes import *
from fireplace.game import Game
from fireplace.player import Player
from fireplace.utils import random_draft
from fireplace.exceptions import GameOver
import time
import traceback

# This script infinitely runs games, and writes the log to an output file when an exception occurs

class OnDemandLogHandler(logging.StreamHandler):
	def __init__(self):
		logging.StreamHandler.__init__(self)
		self._logBuffer = []
		self.filters = []
	def emit(self, record):
		self._logBuffer.append(record.getMessage())
	def getFullLog(self):
		return "\n".join(self._logBuffer)
	def clear(self):
		self._logBuffer = []

def main():
	logdir="/fplogs/"
	odlh = OnDemandLogHandler()
	odlh.setLevel(logging.DEBUG)
	logger = logging.getLogger("fireplace")
	logger.handlers[0].setLevel(999) # The console logger slows this down a lot.
	logger.addHandler(odlh)
	gameCount = 0
	while True:
		gameCount += 1
		print("Starting game %r" % gameCount)
		try:
			odlh.clear()
			rungame()
		except GameOver:
			pass
		except KeyboardInterrupt:
			return
		except:
			logger.error(traceback.format_exc())
			fullLog = odlh.getFullLog()
			filename = logdir + "game" + str(gameCount) + ".txt"
			f = open(filename, "w")
			f.write(fullLog)
			f.close()
			print("Error log written to " + filename)

def rungame():
	hero1 = random.choice([WARRIOR, SHAMAN, ROGUE, PALADIN, HUNTER, DRUID, WARLOCK, MAGE, PRIEST])
	hero2 = random.choice([WARRIOR, SHAMAN, ROGUE, PALADIN, HUNTER, DRUID, WARLOCK, MAGE, PRIEST])
	deck1 = random_draft(hero=hero1)
	deck2 = random_draft(hero=hero2)
	player1 = Player(name="Player1")
	player1.prepare_deck(deck1, hero1)
	player2 = Player(name="Player2")
	player2.prepare_deck(deck2, hero2)

	game = Game(players=(player1, player2))
	game.start()

	for player in game.players:
		mull_count = random.randint(0, len(player.choice.cards))
		cards_to_mulligan = random.sample(player.choice.cards, mull_count)
		player.choice.choose(*cards_to_mulligan)

	while True:
		heropower = game.current_player.hero.power
		options = ["ENDTURN"]
		if game.current_player.choice:
			options = []
			for choicecard in game.current_player.choice.cards:
				options.append(choicecard)
		else:
			if heropower.is_usable():
				options.append(heropower)
			for card in game.current_player.hand:
				if card.is_playable():
					options.append(card)
			for character in game.current_player.characters:
				if character.can_attack():
					options.append(character)
		selectedchoice = random.choice(options)
		if selectedchoice == "ENDTURN":
			game.end_turn()
		elif game.current_player.choice:
			game.current_player.choice.choose(selectedchoice)
		elif selectedchoice is heropower:
			if selectedchoice.has_target():
				heropowerTarget = random.choice(selectedchoice.targets)
				selectedchoice.use(target=heropowerTarget)
			else:
				selectedchoice.use()
		elif selectedchoice in game.current_player.hand:
			target = None
			choose = None
			if selectedchoice.choose_cards:
				choose = random.choice(selectedchoice.choose_cards)
				if choose.has_target():
					target = random.choice(choose.targets)
			elif selectedchoice.has_target():
				target = random.choice(selectedchoice.targets)
			selectedchoice.play(target=target, choose=choose)
		elif selectedchoice in game.current_player.characters:
			attackTarget = random.choice(selectedchoice.targets)
			selectedchoice.attack(attackTarget)
		else:
			raise Exception("Unknown choice: %r" % (selectedchoice)) #TODO remove


if __name__ == "__main__":
	main()
