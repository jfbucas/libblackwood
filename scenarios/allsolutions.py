import os

import scenario

class AllSolutions( scenario.Scenario ):
	"""The scenario for finding all solutions"""

	def __init__( self, puzzle, params={} ):

		self.puzzle = puzzle
		self.name = __name__.split(".")[1] + str(params)

		self.heuristic_patterns = [ ]
		self.conflicts_indexes_allowed = []
		self.heuristic_stats16 = False
		self.depth_first_notification = self.puzzle.board_wh*2
		self.use_adaptative_filter_depth = False
		
		self.report_all_solutions = True

		self.timelimit = 0xffffffffffffff # Minutes

		self.default_commands.extend( [ 
				#"CLEAR_SCREEN",
				#"SHOW_TITLE",
				#"SHOW_HEARTBEAT",
				#"SHOW_RESULT_STATS_NODES_COUNT",
				#"SHOW_STATS_NODES_COUNT",
				#"ZERO_STATS_NODES_COUNT",
				] )

		#self.STATS = True
		#self.PERF = True

		self.prefered_reference = "lu"

		scenario.Scenario.__init__(self, params=params)

	def __str__(self):
		return self.name + " Seed="+str(self.seed)
	def __repr__(self):
		return self.__str__()

	def prepare_patterns_count_heuristics( self ):
		pass

	def prepare_spaces_order( self ):

		depth=0
		for y in range(self.puzzle.board_h):
			for x in range(self.puzzle.board_w):
				s = x+y*self.puzzle.board_w
				self.spaces_order[ s ] = depth 
				depth+=1

scenario.global_list.append(AllSolutions)
