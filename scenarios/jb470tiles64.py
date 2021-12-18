import scenario

class JB470Tiles64( scenario.Scenario ):
	"""The Joshua Blackwood 470 with a sequence by tiles64 Scenario"""

	def __init__( self, puzzle ):

		self.puzzle = puzzle
		self.name = __name__.split(".")[1]

		self.score_target = 470
		self.heuristic_patterns = [ [ 9, 12, 15 ] ]
		self.conflicts_indexes_allowed = [ 197, 203, 210, 216, 221, 225, 229, 233, 236, 238, 256 ]

		self.timelimit = 180 # Minutes

		scenario.Scenario.__init__(self)

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
		for (ys, ye, xs, xe) in [
			(0, self.puzzle.board_h//2, 0,self.puzzle.board_w//2),
			(0, self.puzzle.board_h//2, self.puzzle.board_w//2, self.puzzle.board_w),
			(self.puzzle.board_h//2, self.puzzle.board_h, 0,self.puzzle.board_w//2),
			(self.puzzle.board_h//2, self.puzzle.board_h, self.puzzle.board_w//2, self.puzzle.board_w),
			]:
		      
			for y in range(ys, ye):
				for x in range(xs, xe):
					s = x+y*self.puzzle.board_w
					self.spaces_order[ s ] = depth 
					depth+=1

scenario.global_list.append(JB470Tiles64)
