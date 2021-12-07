# Global Libs
import os
import sys
import ctypes
import random

# Local Libs
import defs

# General configuration for Backtrack and JBlackwood algorithm

HEURISTIC_SIDES = {
		"JB469": [ 17, 2, 18 ],
		"JB470": [ 9, 12, 15 ],
		"JB471": [ 9, 12, 15 ],
		}

HEURISTIC_SIDES_MAX_INDEX = {
		"JB469": 156,
		"JB470": 160,
		"JB471": 162,
		}

CONFLICT_INDEXES_ALLOWED = {
		"JB469": [ 201, 206, 211, 216, 221, 225, 229, 233, 237, 239, 241, 256 ],
		"JB470": [ 197, 203, 210, 216, 221, 225, 229, 233, 236, 238, 256 ],
		"JB471": [ 206, 211, 216, 221, 225, 229, 233, 237, 239, 256 ],
		}



class Scenario( defs.Defs ):
	"""Definitions for Scenarios"""

	def __init__( self, puzzle, name="JB470" ):

		self.puzzle = puzzle
		self.name = name

		if self.name not in [ "JB469", "JB470", "JB471" ]:
			self.name = "JB470"

		self.seed = 0
		self.score_target = 0
		self.heuristic_patterns = None
		self.heuristic_patterns_max_index = 0
		self.heuristic_patterns_count = []
		self.conflicts_indexes_allowed = None
		self.spaces_order = []
		self.spaces_sequence = []

		self.timelimit = 60 # Minutes

		# The Seed for the Generator
		self.seed = random.randint(0, sys.maxsize)
		if os.environ.get('SEED') != None:
			self.seed = int(os.environ.get('SEED'))
			if self.DEBUG > 0:
				self.info(" * Init Scenario Env Seed : "+str(self.seed) )


		if self.name in [ "JB469", "JB470", "JB471" ]:
			self.score_target     = int(self.name[2:])
			self.heuristic_patterns           = HEURISTIC_SIDES[ self.name ]
			self.heuristic_patterns_max_index = HEURISTIC_SIDES_MAX_INDEX[ self.name ]
			self.conflicts_indexes_allowed    = CONFLICT_INDEXES_ALLOWED[ self.name ]

		self.prepare_heuristics()
		self.prepare_sequence()

	# ----- Prepare heuristics
	def prepare_heuristics( self ):

		if self.DEBUG > 2:
			self.info( " * Preparing heuristics..." )

		self.heuristic_patterns_count = [0] * self.puzzle.board_wh
		if self.name in [ "JB469" ]:
			for i in range(self.puzzle.board_wh):
				if i <= 16:
					self.heuristic_patterns_count[i] = 0
				elif i <= 26:
					self.heuristic_patterns_count[i] = int((float(i) - 16) * float(3.1))
				elif i <= 56:
					self.heuristic_patterns_count[i] = int(((float(i) - 26) * float(1.43333)) + 31)
				elif i <= 96:
					self.heuristic_patterns_count[i] = int(((float(i) - 56) * float(0.65)) + 74)
				elif i <= self.heuristic_patterns_max_index:
					self.heuristic_patterns_count[i] = int(((float(i) - 96) / 3.75) + 100)

		elif self.name in [ "JB470", "JB471", "default" ]:
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

		if self.DEBUG_STATIC > 2:
			self.printArray(self.heuristic_patterns_count, array_w=self.puzzle.board_w, array_h=self.puzzle.board_h)

	# ----- Prepare sequences
	def prepare_sequence( self ):

		if self.DEBUG > 2:
			self.info( " * Preparing sequences..." )

		if self.name in [ "JB469", "JB470", "JB471", "default" ]:
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

		self.spaces_sequence = []
		for depth in range(self.puzzle.board_wh):
			self.spaces_sequence.append( self.spaces_order.index(depth) )

		if self.DEBUG_STATIC > 0:
			tmp = [ " " ] * self.puzzle.board_wh
			for depth in range(self.puzzle.board_wh):
				tmp[ self.spaces_sequence[ depth ] ] = "X"
				print("---[ Sequence ",depth, "]---")
				self.printArray(tmp, array_w=self.puzzle.board_w, array_h=self.puzzle.board_h)
			

		#self.spaces_board_sequence = []
		#for depth in range(self.puzzle.board_wh):
		#	space = self.spaceSequence[ depth ]
		#	self.spaces_board_sequence.append(space)


		#if self.DEBUG_STATIC > 2:
		#	self.printArray(self.heuristic_patterns_count, array_w=self.puzzle.board_w, array_h=self.puzzle.board_h)


	# ----- Provide the index name for the space
	def get_index_piece_name(self, depth):

		space = self.spaces_sequence[ depth ]
		x = space % self.puzzle.board_w
		y = space // self.puzzle.board_h

		W=self.puzzle.board_w-1
		H=self.puzzle.board_h-1

		conflicts = "" 
		if depth >= min(self.conflicts_indexes_allowed):
			conflicts = "_conflicts"
		else:
			if y == H and x != W and x != 0:
				conflicts = "_conflicts"


		master_piece_name = ""
		# Is it a corner/border?
		if y == 0:
			if x in [ 0, W ]:
				master_piece_name = "corner"
			else:
				master_piece_name = "border_u"

		elif y == H:
			if x in [ 0, W ]:
				master_piece_name = "corner"
			else:
				master_piece_name = "border_d" + conflicts
		    
		else:
			if x == 0:
				master_piece_name = "border_l"
			elif x == W:
				master_piece_name = "border_r" + conflicts

		# Is it a fixed or next to a fixed?
		if master_piece_name == "":
			for ( fpiece, fspace, frotation ) in self.puzzle.fixed:
				if space == fspace:
					master_piece_name = "fixed"+str(fpiece)
				elif space == fspace-self.puzzle.board_w:
					master_piece_name = "fixed"+str(fpiece)+"_n"
				elif space == fspace+1:
					master_piece_name = "fixed"+str(fpiece)+"_e"
				elif space == fspace+self.puzzle.board_w:
					master_piece_name = "fixed"+str(fpiece)+"_s"
				elif space == fspace-1:
					master_piece_name = "fixed"+str(fpiece)+"_w"

		# Default is center
		if master_piece_name == "":
			master_piece_name = "center" + conflicts

		return master_piece_name		


if __name__ == "__main__":
	import data

	p = data.loadPuzzle()

	s = Scenario(p, target_score)
	p.initPatternsRelations()


