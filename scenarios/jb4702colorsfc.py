import scenario
import random

class JB4702ColorsFC( scenario.Scenario ):
	"""The Joshua Blackwood 470 Scenario with only 2 colors and fixed corner"""

	def __init__( self, puzzle, discriminant="" ):

		self.puzzle = puzzle
		self.name = __name__.split(".")[1] + str(discriminant)

		self.heuristic_patterns = [ [ 9, 15 ] ]
		#self.heuristic_patterns = [ [ 3, 21 ] ] # XXX
		#self.heuristic_patterns = [ [ 9, 19 ] ] # XXX
		#self.heuristic_patterns = [ [ 9, 19 ] ] # Ok
		#self.heuristic_patterns = [ [ 9, 19 ] ] # Ok
		self.conflicts_indexes_allowed = [ 197, 203, 210, 216, 221, 225, 229, 233, 236, 238 ]
		#self.conflicts_indexes_allowed = [ 197, 203, 210, 216, 221, 225, 229, 233, 236, 238 ] + list(range(240,256,1))
		#self.conflicts_indexes_allowed = list(range(197,256,3))
		#while len(self.conflicts_indexes_allowed) > 10:
		#	e = random.choice(self.conflicts_indexes_allowed)
		#	self.conflicts_indexes_allowed.remove(e)
		self.heuristic_stats16 = False
		self.depth_first_notification = 252

		#self.timelimit = 4*60 # Minutes
		self.timelimit = 30 # Minutes

		# Add a fixed corner in upside-down scenario and reversed space_order
		if not self.puzzle.upside_down:
			#self.puzzle.fixed.extend( [ [ 1, 0, 3 ] ] )    # Left-Up Corner
			self.puzzle.fixed.extend( [ [ 1, 15, 0 ] ] )    # Up-Right Corner
			#self.puzzle.fixed.extend( [ [ 1, 240, ? ] ] )  # Corner
			#self.puzzle.fixed.extend( [ [ 1, 255, ? ] ] )  # Corner
		else:
			#self.puzzle.fixed.extend( [ [ 1, 0, 3 ] ] )    # Corner
			#self.puzzle.fixed.extend( [ [ 1, 15, 0 ] ] )    # Corner
			#self.puzzle.fixed.extend( [ [ 1, 240, 2 ] ] )  # Corner
			self.puzzle.fixed.extend( [ [ 1, 255, 1 ] ] )  # Left Up Corner

		scenario.Scenario.__init__(self)

	def __str__(self):
		return self.name + " Seed="+str(self.seed) + " Patterns:" + str(self.heuristic_patterns) + " Conflicts:" + str(self.conflicts_indexes_allowed)
	def __repr__(self):
		return self.__str__()

	def prepare_patterns_count_heuristics( self ):

		for i in range(self.puzzle.board_wh):
			if i in range(15, 27):
				self.heuristic_patterns_count[0][i] = int((i - 14) * 2)
			elif i in range(27, 37):
				self.heuristic_patterns_count[0][i] = int((i - 26) * 1.3) + 24 #self.heuristic_patterns_count[0][26]
			elif i in range(37, 57):
				self.heuristic_patterns_count[0][i] = int((i - 36) * 1.3) + 37 #self.heuristic_patterns_count[0][36]
			elif i in range(57, 77):
				self.heuristic_patterns_count[0][i] = int((i - 56) * 0.85) + 57 #self.heuristic_patterns_count[0][56]
			elif i in range(77, 103):
				self.heuristic_patterns_count[0][i] = int((i - 76) * 0.5) + 74 #self.heuristic_patterns_count[0][76]
			elif i in range(103, 151):
				self.heuristic_patterns_count[0][i] = int((i - 102) / 5.3334) + 87 #self.heuristic_patterns_count[0][102]
			elif i in range(151, 180):
				self.heuristic_patterns_count[0][i] = int((i - 151) / 8.3334) + 95 #self.heuristic_patterns_count[0][102]

	def prepare_spaces_order( self ):

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
		#self.reverse_spaces_order = True
		#self.flip_spaces_order = True


scenario.global_list.append(JB4702ColorsFC)
