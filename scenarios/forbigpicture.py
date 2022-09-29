import os

import scenario

class ForBigpicture( scenario.Scenario ):
	"""The scenario for Bigpicture"""

	def __init__( self, puzzle, discriminant="" ):

		self.puzzle = puzzle
		self.name = __name__.split(".")[1] + str(discriminant)

		self.heuristic_patterns = [ ]
		self.conflicts_indexes_allowed = []
		self.heuristic_stats16 = False
		if self.puzzle.name == "EternityII":
			self.depth_first_notification = 225
		else:
			self.depth_first_notification = self.puzzle.board_wh-(self.puzzle.board_w//2)
		#self.use_adaptative_filter_depth = False

		self.timelimit = 1 # Minutes
		if os.environ.get('TIMELIMIT') != None: 
			self.timelimit = int(os.environ.get('TIMELIMIT')) # Minutes

		self.default_commands.extend( [ 
				#"CLEAR_SCREEN",
				#"SHOW_TITLE",
				#"SHOW_HEARTBEAT",
				"SHOW_RESULT_STATS_NODES_COUNT",
				"SHOW_STATS_NODES_COUNT",
				#"ZERO_STATS_NODES_COUNT",
				] )

		self.STATS = True
		#self.PERF = True

		#self.puzzle.fixed.extend( [
			#	[ 0,0,3 ],
		##		#[ 2,7,0 ],
		#			] )

		self.prefered_reference = "lu"

		scenario.Scenario.__init__(self)

	def __str__(self):
		return self.name + " Seed="+str(self.seed)
	def __repr__(self):
		return self.__str__()

	def prepare_patterns_count_heuristics( self ):
		pass

	def prepare_spaces_order( self ):


		if self.puzzle.name != "EternityII":
			depth=0
			for y in range(self.puzzle.board_h):
				for x in range(self.puzzle.board_w):
					s = x+y*self.puzzle.board_w
					self.spaces_order[ s ] = depth 
					depth+=1
		else:

			self.spaces_order = [
				  0,   1,   2,   3,   4,   5,   6,   7,   8,   9,  10,  11,  12,  13,  14,  15,  
				 16,  17,  18,  19,  20,  21,  22,  23,  24,  25,  26,  27,  28,  29,  30,  31,  
				 32,  33,  34,  35,  36,  37,  38,  39,  40,  41,  42,  43,  44,  45,  46,  47,  
				 48,  49,  50,  51,  52,  53,  54,  55,  56,  57,  58,  59,  60,  61,  62,  63,  
				 64,  65,  66,  67,  68,  69,  70,  71,  72,  73,  74,  75,  76,  77,  78,  79,  
				 80,  81,  82,  83,  84,  85,  86,  87,  88,  89,  90,  91,  92,  93,  94,  95,  
				 96,  97,  98,  99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 
				112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 
				128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 
				144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 
				160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 
				176, 177, 178, 179, 180, 201, 206, 211, 216, 221, 226, 231, 236, 237, 238, 239, 
				181, 182, 183, 184, 185, 202, 207, 212, 217, 222, 227, 232, 240, 244, 245, 246, 
				186, 187, 188, 189, 190, 203, 208, 213, 218, 223, 228, 233, 241, 247, 250, 251, 
				191, 192, 193, 194, 195, 204, 209, 214, 219, 224, 229, 234, 242, 248, 252, 253, 
				196, 197, 198, 199, 200, 205, 210, 215, 220, 225, 230, 235, 243, 249, 254, 255,
				]

			# Reverse to start from the bottom
			self.reverse_spaces_order = True
			#self.flip_spaces_order = True

scenario.global_list.append(ForBigpicture)
