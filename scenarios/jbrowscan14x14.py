import scenario

class JBRowScan14x14( scenario.Scenario ):
	"""Joshua Blackwood Heuristics with a simple rowscan Scenario"""

	def __init__( self, puzzle ):

		self.puzzle = puzzle
		self.name = __name__.split(".")[1]

		self.score_target = 480
		self.heuristic_patterns = [ [ 9, 15 ] ]
		self.conflicts_indexes_allowed = [256]
		self.heuristic_stats16 = False
		self.depth_first_notification = 194

		self.timelimit = 800 # Minutes

		scenario.Scenario.__init__(self)

	def prepare_patterns_count_heuristics( self ):

		for i in range(self.puzzle.board_wh):
			if i in range(15, 27):
				self.heuristic_patterns_count[0][i] = int((i - 14) * 1.5)
			elif i in range(27, 37):
				self.heuristic_patterns_count[0][i] = int((i - 26) * 1.1) + 18
			elif i in range(37, 57):
				self.heuristic_patterns_count[0][i] = int((i - 36) * 1.1) + 29
			elif i in range(57, 77):
				self.heuristic_patterns_count[0][i] = int((i - 56) * 0.75) + 52
			elif i in range(77, 103):
				self.heuristic_patterns_count[0][i] = int((i - 76) * 0.4) + 74
			elif i in range(103, 151):
				self.heuristic_patterns_count[0][i] = int((i - 102) / 5.3334) + 87


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

scenario.global_list.append(JBRowScan14x14)
