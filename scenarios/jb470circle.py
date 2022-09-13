import scenario

class JB470Circle( scenario.Scenario ):
	"""The Joshua Blackwood 470 with a growing circle from the top-left corner Scenario"""

	def __init__( self, puzzle, discriminant="" ):

		self.puzzle = puzzle
		self.name = __name__.split(".")[1] + str(discriminant)

		self.heuristic_patterns = [ [ 9, 12, 15 ] ]
		self.conflicts_indexes_allowed = [ 197, 203, 210, 216, 221, 225, 229, 233, 236, 238 ]
		self.heuristic_stats16 = False
		self.depth_first_notification = 252

		self.timelimit = 180 # Minutes

		scenario.Scenario.__init__(self)

	def __str__(self):
		return self.name + " Seed="+str(self.seed) + " Patterns:" + str(self.heuristic_patterns) + " Conflicts:" + str(self.conflicts_indexes_allowed)
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

		used = [ False ] * self.puzzle.board_wh
		for depth in range( self.puzzle.board_wh ):
			WH = self.puzzle.board_wh
			d_selected = WH*WH + WH*WH
			s_selected = WH
			for y in range(self.puzzle.board_h):
				for x in range(self.puzzle.board_w):
					s = x+y*self.puzzle.board_w
					if used[ s ]:
						continue
					
					# distance to top left corner
					d = x*x + y*y
					if d_selected > d:
						x_selected = x
						y_selected = y
						d_selected = d
						s_selected = s

			used[ s_selected ] = True
			self.spaces_order[ s_selected ] = depth 

scenario.global_list.append(JB470Circle)
