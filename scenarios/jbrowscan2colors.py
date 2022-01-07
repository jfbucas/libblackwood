import scenario

class JBRowScan2Colors( scenario.Scenario ):
	"""Joshua Blackwood Heuristics for a simple rowscan Scenario with only 2 colors"""

	def __init__( self, puzzle ):

		self.puzzle = puzzle
		self.name = __name__.split(".")[1]

		self.heuristic_patterns = [ [ 9, 15 ] ]
		self.conflicts_indexes_allowed = []
		self.heuristic_stats16 = False
		self.depth_first_notification = 226
		self.depth_filters = []

		self.timelimit = 800 # Minutes

		scenario.Scenario.__init__(self)

	def __str__(self):
		return self.name + " Seed="+str(self.seed) + " Patterns:" + str(self.heuristic_patterns)
	def __repr__(self):
		return self.__str__()

	def prepare_patterns_count_heuristics( self ):

		for i in range(self.puzzle.board_wh):
			if i in range(15, 27):
				self.heuristic_patterns_count[0][i] = int((i - 14) * 2)
			elif i in range(27, 37):
				self.heuristic_patterns_count[0][i] = int((i - 26) * 1.3) + 24
			elif i in range(37, 57):
				self.heuristic_patterns_count[0][i] = int((i - 36) * 1.3) + 37
			elif i in range(57, 77):
				self.heuristic_patterns_count[0][i] = int((i - 56) * 0.85) + 57
			elif i in range(77, 103):
				self.heuristic_patterns_count[0][i] = int((i - 76) * 0.5) + 74
			elif i in range(103, 151):
				self.heuristic_patterns_count[0][i] = int((i - 102) / 5.3334) + 87

	def prepare_spaces_order( self ):

		depth=0
		for y in range(self.puzzle.board_h):
			for x in range(self.puzzle.board_w):
				s = x+y*self.puzzle.board_w
				self.spaces_order[ s ] = depth 
				depth+=1

		# Reverse to start from the bottom
		self.reverse_spaces_order = True

scenario.global_list.append(JBRowScan2Colors)
