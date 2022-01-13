import scenario

class JBRowScanSnake( scenario.Scenario ):
	"""Joshua Blackwood Heuristics with a simple rowscan in the form of a snake Scenario"""

	def __init__( self, puzzle ):

		self.puzzle = puzzle
		self.name = __name__.split(".")[1]

		self.heuristic_patterns = [ [ 9, 12, 15 ] ]
		self.conflicts_indexes_allowed = []
		self.heuristic_stats16 = False
		self.depth_first_notification = 225

		self.timelimit = 5 # Minutes

		scenario.Scenario.__init__(self)

	def __str__(self):
		return self.name + " Seed="+str(self.seed) + " Patterns:" + str(self.heuristic_patterns)
	def __repr__(self):
		return self.__str__()

	def prepare_patterns_count_heuristics( self ):

		for i in range(self.puzzle.board_wh):
			if i in range(17, 27):
				self.heuristic_patterns_count[0][i] = int((i - 16) * 2.8)
			elif i in range(27, 57):
				self.heuristic_patterns_count[0][i] = int((i - 26) * 1.43333) + 28
			elif i in range(57, 77):
				self.heuristic_patterns_count[0][i] = int((i - 56) * 0.9) + 71
			elif i in range(77, 103):
				self.heuristic_patterns_count[0][i] = int((i - 76) * 0.6538) + 89
			elif i in range(103, 161):
				self.heuristic_patterns_count[0][i] = int((i - 102) / 4.4615) + 106

	def prepare_spaces_order( self ):

		depth=0
		for y in range(self.puzzle.board_h):
			r = range(self.puzzle.board_w)
			if y % 2 == 1:
				r = reversed(r)

			for x in r:
				s = x+y*self.puzzle.board_w
				self.spaces_order[ s ] = depth 
				depth+=1

		# Reverse to start from the bottom
		self.reverse_spaces_order = True


scenario.global_list.append(JBRowScanSnake)
