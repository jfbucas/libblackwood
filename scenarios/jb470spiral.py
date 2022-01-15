import scenario
import random
import sys
import os

class JB470Spiral( scenario.Scenario ):
	"""The Joshua Blackwood 470 Scenario with a spiral"""

	def __init__( self, puzzle ):

		self.puzzle = puzzle
		self.name = __name__.split(".")[1]

		self.heuristic_patterns = []
		self.conflicts_indexes_allowed = [ 220, 223, 227, 232, 237, 243, 246, 250, 252, 254 ]
		self.heuristic_stats16 = False
		self.depth_first_notification = 220

		#self.timelimit = 15 # Minutes
		self.timelimit = 5*60 # Minutes

		scenario.Scenario.__init__(self)

	def __str__(self):
		return self.name + " Seed="+str(self.seed) + " Patterns:" + str(self.heuristic_patterns) + " Conflicts:" + str(self.conflicts_indexes_allowed)
	def __repr__(self):
		return self.__str__()

	def prepare_patterns_count_heuristics( self ):
		pass


	def prepare_spaces_order( self ):


		used = [ False ] * self.puzzle.board_wh

		directions = [
			self.puzzle.static_space_up, 
			self.puzzle.static_space_right, 
			self.puzzle.static_space_down, 
			self.puzzle.static_space_left
			]

		depth = 0
		while depth < self.puzzle.board_wh:

			for d in directions: 
				new_spaces = []

				l = range(self.puzzle.board_wh)
				if d == self.puzzle.static_space_down or d == self.puzzle.static_space_left:
					l = reversed(l)

				for s in l:
					if not used[ s ]:
						if d[s] == None:
							new_spaces.append(s)
						else:
							if used[ d[s] ]:
								new_spaces.append(s)

				print(new_spaces)
				for s in new_spaces:
					used[s] = True
					self.spaces_order[ s ] = depth
					depth += 1


		# Reverse to start from the bottom
		#self.reverse_spaces_order = True
		#self.flip_spaces_order = True

scenario.global_list.append(JB470Spiral)
