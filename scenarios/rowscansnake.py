import scenario

class RowScanSnake( scenario.Scenario ):
	"""The Heuristics with a simple rowscan snake Scenario"""

	def __init__( self, puzzle ):

		self.puzzle = puzzle
		self.name = __name__.split(".")[1]

		self.score_target = 480
		self.heuristic_patterns = [ ]
		self.conflicts_indexes_allowed = [256]
		self.heuristic_stats16 = False
		self.depth_first_notification = 225

		self.timelimit = 800 # Minutes

		scenario.Scenario.__init__(self)

	def __str__(self):
		return self.name + " Seed="+str(self.seed)
	def __repr__(self):
		return self.__str__()

	def prepare_patterns_count_heuristics( self ):
		pass

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

scenario.global_list.append(RowScanSnake)
