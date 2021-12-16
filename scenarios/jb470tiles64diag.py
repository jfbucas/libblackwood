import scenario

class JB470Tiles64Diag( scenario.Scenario ):
	"""The Joshua Blackwood 470 with a sequence by tiles64, but last tiles64 in diagonal Scenario"""

	def __init__( self, puzzle ):

		self.puzzle = puzzle
		self.name = "JB470tiles64diag"

		self.score_target = 470
		self.heuristic_patterns = [ 9, 12, 15 ]
		self.heuristic_patterns_max_index = 160
		self.conflicts_indexes_allowed = [ 197, 203, 210, 216, 221, 225, 229, 233, 236, 238, 256 ]

		self.timelimit = 180 # Minutes

		scenario.Scenario.__init__(self)

	def prepare_patterns_count_heuristics( self ):

		for i in range(self.puzzle.board_wh):
			if i <= 16:
				self.heuristic_patterns_count[i] = 0
			elif i <= 26:
				self.heuristic_patterns_count[i] = int((float(i) - 16) * float(2.8))
			elif i <= 56:
				self.heuristic_patterns_count[i] = int(((float(i) - 26) * float(1.43333)) + 28)
			elif i <= 76:
				self.heuristic_patterns_count[i] = int(((float(i) - 56) * float(0.9)) + 71)
			elif i <= 102:
				self.heuristic_patterns_count[i] = int(((float(i) - 76) * float(0.6538)) + 89)
			elif i <= self.heuristic_patterns_max_index:
				self.heuristic_patterns_count[i] = int(((float(i) - 102) / 4.4615) + 106)

	def prepare_spaces_order( self ):

		depth=0
		for (ys, ye, xs, xe) in [
			(0, self.puzzle.board_h//2, 0,self.puzzle.board_w//2),
			(0, self.puzzle.board_h//2, self.puzzle.board_w//2, self.puzzle.board_w),
			(self.puzzle.board_h//2, self.puzzle.board_h, 0,self.puzzle.board_w//2),
			]:
		      
			for y in range(ys, ye):
				for x in range(xs, xe):
					s = x+y*self.puzzle.board_w
					self.spaces_order[ s ] = depth 
					depth+=1

		for y in range(0, self.puzzle.board_h//2):
			for x in range(y+1):
				s = self.puzzle.board_w//2 + x + (y+(self.puzzle.board_h//2)-x)*self.puzzle.board_w
				self.spaces_order[ s ] = depth 
				depth+=1

		for x in range(self.puzzle.board_w//2+1, self.puzzle.board_w):
			for y in range(self.puzzle.board_w-x):
				s = x+y+(self.puzzle.board_h-1-y)*self.puzzle.board_w
				self.spaces_order[ s ] = depth 
				depth+=1

