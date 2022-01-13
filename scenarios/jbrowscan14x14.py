import scenario

class JBRowScan14x14( scenario.Scenario ):
	"""Joshua Blackwood Heuristics with a simple rowscan Scenario"""

	def __init__( self, puzzle ):

		self.puzzle = puzzle
		self.name = __name__.split(".")[1]

		self.heuristic_patterns = [ [ 9, 15 ] ]
		self.conflicts_indexes_allowed = []
		self.heuristic_stats16 = False
		self.depth_first_notification = 187
		self.use_adaptative_filter_depth = True

		self.timelimit = 800 # Minutes

		scenario.Scenario.__init__(self)

	def __str__(self):
		return self.name + " Seed="+str(self.seed) + " Patterns:" + str(self.heuristic_patterns)
	def __repr__(self):
		return self.__str__()

	def prepare_patterns_count_heuristics( self ):

		for i in range(self.puzzle.board_wh):
			if i in range(1, 15):
				self.heuristic_patterns_count[0][i] = int((i - 1) * 1.5)
			if i in range(15, 27):
				self.heuristic_patterns_count[0][i] = int((i - 14) * 1.1) + self.heuristic_patterns_count[0][14] 
			elif i in range(27, 37):
				self.heuristic_patterns_count[0][i] = int((i - 26) * 0.9) + self.heuristic_patterns_count[0][26]
			elif i in range(37, 57):
				self.heuristic_patterns_count[0][i] = int((i - 36) * 0.85) + self.heuristic_patterns_count[0][36]
			elif i in range(57, 77):
				self.heuristic_patterns_count[0][i] = int((i - 56) * 0.5) + self.heuristic_patterns_count[0][56]
			elif i in range(77, 103):
				self.heuristic_patterns_count[0][i] = int((i - 76) * 0.5) + self.heuristic_patterns_count[0][76]
			elif i in range(103, 151):
				self.heuristic_patterns_count[0][i] = int((i - 102) / 2.8034) + self.heuristic_patterns_count[0][102] 
			#elif i in range(151, 180):
			#	self.heuristic_patterns_count[0][i] = int((i - 151) / 3.0334) + self.heuristic_patterns_count[0][150]


	def prepare_spaces_order( self ):

		depth=0
		for y in range(self.puzzle.board_h):
			for x in range(self.puzzle.board_w):
				s = x+y*self.puzzle.board_w
				if s in self.puzzle.static_spaces_centers:
					self.spaces_order[ s ] = depth 
					depth+=1

		for y in range(self.puzzle.board_h):
			for x in range(self.puzzle.board_w):
				s = x+y*self.puzzle.board_w
				if s not in self.puzzle.static_spaces_centers:
					self.spaces_order[ s ] = depth 
					depth+=1

		# Reverse to start from the bottom
		#self.reverse_spaces_order = True

scenario.global_list.append(JBRowScan14x14)
