import scenario
import random
import sys
import os

#for i in {0..11}; do (for j in {0..419}; do STRUCT=$((i*420+j)) NOLCA=1 QUIET=1 FORCE_COMPILE=1 SEED=395724 DEBUG_PERF=1 SCENARIO=jb470struct$i PUZZLE=E2ncud  python3 ./libblackwood.py >> STRUCT_$i.txt; done &); sleep 30; done

class JB470Struct( scenario.Scenario ):
	"""Assessing structure order's influence on performance"""

	def __init__( self, puzzle, params={} ):

		self.puzzle = puzzle
		self.name = __name__.split(".")[1] + str(params)

		self.heuristic_patterns = [ [ 9, 12, 15 ] ]
		self.conflicts_indexes_allowed = [ 197, 203, 210, 216, 221, 225, 229, 233, 236, 238 ] # + [ 240, 242, 244, 246, 248, 250 ]
		self.heuristic_stats16 = False
		self.depth_first_notification = 254
		self.use_adaptative_filter_depth = False

		self.timelimit = 1 # Minutes
		#self.timelimit = 10 # Minutes

		scenario.Scenario.__init__(self, params=params)

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
		self.flip_spaces_order = True

	def next_seed(self):
		self.seed = random.randint(0, sys.maxsize)

		if os.environ.get('SEED') != None:
			self.seed = int(os.environ.get('SEED'))
			if self.seed == 18:
				self.seed = 3316111202040243245 # 253 in 18 sec! with PUZZLE=E2ncud
			if self.seed == 85:
				self.seed = 3957753796008984024 # 253 in 85 sec! with PUZZLE=E2ncud
			if self.seed == 244:
				self.seed = 8192406586059670907 # 253 in 244 sec! with PUZZLE=E2ncud

			if self.DEBUG > 0:
				self.info(" * Init Scenario Env Seed : "+str(self.seed) )

		return self.seed

scenario.global_list.append(JB470Struct)
