# Global Libs
import os
import sys
import ctypes
import random

# Local Libs
import defs

global_list = []

# General scenario for Backtracker

class Scenario( defs.Defs ):
	"""Definitions for Scenarios"""

	use_adaptative_filter_depth = True

	def __init__( self ):

		defs.Defs.__init__( self )

		if self.DEBUG > 0:
			self.info(" * Using scenario : "+self.name )

		self.seed = 0
		self.heuristic_patterns_count = []
		for i in range(5):
			self.heuristic_patterns_count.append( [0] * self.puzzle.board_wh )
		self.heuristic_conflicts_count = [0] * self.puzzle.board_wh
		self.heuristic_stats16_count = [0] * self.puzzle.board_wh
		self.spaces_order = [None] * self.puzzle.board_wh
		self.spaces_sequence = [None] * self.puzzle.board_wh
		self.spaces_references = [None] * self.puzzle.board_wh
		self.reverse_spaces_order = False
		self.flip_spaces_order = False

		self.score_target = self.puzzle.board_wh*2 - self.puzzle.board_w - self.puzzle.board_h
		self.score_target -= len(self.conflicts_indexes_allowed)

		# The Seed for the Generator
		self.seed = random.randint(0, sys.maxsize)
		#if os.environ.get('SEED') != None:
		#	self.seed = int(os.environ.get('SEED'))
		#	if self.DEBUG > 0:
		#		self.info(" * Init Scenario Env Seed : "+str(self.seed) )

		# Init the pattern heuristic
		self.prepare_patterns_count_heuristics()
		
		if self.puzzle.DEBUG_STATIC > 0:
			self.puzzle.info( " * Patterns count heuristics" )
			for i in range(5):
				if sum(self.heuristic_patterns_count[i]) > 0:
					self.printArray(self.heuristic_patterns_count[i], array_w=self.puzzle.board_w, array_h=self.puzzle.board_h)
			#exit()
		
		
		# Init the space order
		self.prepare_spaces_order()

		if self.DEBUG_STATIC > 0:
			self.info( " * Spaces order" )
			self.printArray(self.spaces_order, array_w=self.puzzle.board_w, array_h=self.puzzle.board_h)

		# Init the spaces sequence
		self.prepare_spaces_sequence()

		if self.DEBUG_STATIC > 0:
			self.info( " * Spaces sequence" )
			self.printArray(self.spaces_sequence, array_w=self.puzzle.board_w, array_h=self.puzzle.board_h)

		# Init the spaces references
		self.prepare_spaces_references()
		if self.DEBUG_STATIC > 0:
			self.info( " * Spaces references" )
			self.printArray(self.spaces_references, array_w=self.puzzle.board_w, array_h=self.puzzle.board_h)
		
		# Once we have the sequence, we can determine the pieces Weights, based on stats
		if self.heuristic_stats16:
			self.puzzle.prepare_stats16_from_sequence(self.spaces_sequence)
		
		# Init the stats16 heuristics
		if self.heuristic_stats16:
			self.prepare_stats16_count_heuristics()

			if self.DEBUG_STATIC > 0:
				self.info( " * Heuristics for stats16" )
				self.printArray(self.heuristic_stats16_count, array_w=self.puzzle.board_w, array_h=self.puzzle.board_h)
				#exit()

		# Init the conflicts heuristic
		self.prepare_conflicts_count_heuristics()
		
		if self.puzzle.DEBUG_STATIC > 0:
			self.puzzle.info( " * Conflict count heuristics" )
			if sum(self.heuristic_conflicts_count) > 0:
				self.printArray(self.heuristic_conflicts_count, array_w=self.puzzle.board_w, array_h=self.puzzle.board_h)
				#exit()

	# ----- Prepare spaces sequence
	def prepare_spaces_sequence( self ):
		W=self.puzzle.board_w
		H=self.puzzle.board_h
		WH=self.puzzle.board_wh

		# Reverse to start from the bottom
		if self.reverse_spaces_order:
			tmp = [ None ] * WH
			for depth in range(WH):
				s = self.spaces_order.index(depth)
				sx = s % W
				sy = s // W
				sy = W-1 - sy
				s = sx+sy*W
				self.spaces_sequence[ depth ] = s
				tmp[s] = depth
			self.spaces_order = tmp

		# Flip the space order
		if self.flip_spaces_order:
			tmp = [ None ] * WH
			for depth in range(WH):
				s = self.spaces_order.index(depth)
				sx = s % W
				sx = W-1 - sx
				sy = s // W
				s = sx+sy*W
				self.spaces_sequence[ depth ] = s
				tmp[s] = depth
			self.spaces_order = tmp


		tmp = [ " " ] * WH
		for depth in range(WH):
			self.spaces_sequence[ depth ] = self.spaces_order.index(depth)

			if self.DEBUG_STATIC > 2:
				tmp[ self.spaces_sequence[ depth ] ] = "X"
				print("---[ Sequence " + str(depth) + " ]---\n")
				self.printArray(tmp, array_w=W, array_h=H)


	# ----- Prepare spaces references
	# References can also be defined in the scenario by overloading this function
	def prepare_spaces_references( self ):
		W=self.puzzle.board_w
		H=self.puzzle.board_h
		WH=self.puzzle.board_wh

		for depth in range(WH):
			space = self.spaces_sequence[ depth ]
			ref = ""
			ref += "U" if space < W          else ( "u" if self.spaces_order[ space - W ] < depth else "" );
			ref += "R" if (space+1) % W == 0 else ( "r" if self.spaces_order[ space + 1 ] < depth else "" )
			ref += "D" if space >= WH-W      else ( "d" if self.spaces_order[ space + W ] < depth else "" );
			ref += "L" if space % W == 0     else ( "l" if self.spaces_order[ space - 1 ] < depth else "" );

			# Removes the out reference if not needed (2 ref is enough)
			for x in [0, 1]:
				if len(ref) > 2:
					one_found=False
					new_ref = ""
					for s in reversed(ref):
						if s.upper() == s and not one_found:
							one_found = True
						else:
							new_ref += s
					ref = new_ref

			ref = ref.lower()

			# Make sure we have the first 2 refs in the correct order
			if len(ref) > 1:
				while ref[0:2] not in [ "ur", "rd", "dl", "lu", "ud", "lr" ]:
					ref = ref[1:]+ref[0:1]

			self.spaces_references[ space ] = ref

			
	# ----- Return the index of the last number before the zeros
	def max_index( self, array ):

		index = len(array)-1
		while array[index] == 0:
			index -= 1

		return index

	# ----- Provide the index name for the space
	def get_index_piece_name(self, depth):

		space = self.spaces_sequence[ depth ]
		x = space % self.puzzle.board_w
		y = space // self.puzzle.board_h

		W=self.puzzle.board_w
		H=self.puzzle.board_h
		WH = W*H

		# From a certain depth, we authorize conflicts (or breaks)
		conflicts = "" 
		if self.heuristic_conflicts_count[space] > 0: 
			conflicts = "_conflicts"

		master_piece_name = ""
		# Is it a fixed or next to a fixed?
		if master_piece_name == "":
			for ( fpiece, fspace, frotation ) in self.puzzle.fixed:
				if space == fspace:
					master_piece_name = "fixed"+str(fpiece)
				elif space == self.puzzle.static_space_up[fspace]:
					master_piece_name = "fixed"+str(fpiece)+"_n"
				elif space == self.puzzle.static_space_right[fspace]:
					master_piece_name = "fixed"+str(fpiece)+"_e"
				elif space == self.puzzle.static_space_down[fspace]:
					master_piece_name = "fixed"+str(fpiece)+"_s"
				elif space == self.puzzle.static_space_left[fspace]:
					master_piece_name = "fixed"+str(fpiece)+"_w"

		# Is it a corner/border?
		if master_piece_name == "":
			if y == 0:
				if x in [ 0, W-1 ]:
					master_piece_name = "corner"
				else:
					master_piece_name = "border_u"

			elif y == H-1:
				if x in [ 0, W-1 ]:
					master_piece_name = "corner"
				else:
					master_piece_name = "border_d" + conflicts
			    
			else:
				if x == 0:
					master_piece_name = "border_l"
				elif x == W-1:
					master_piece_name = "border_r" + conflicts

		# Default is center
		if master_piece_name == "":
			master_piece_name = "center" + conflicts

		master_piece_name += "_"+self.spaces_references[ space ]

		return master_piece_name		

	# ----- Prepare spaces references
	def prepare_conflicts_count_heuristics( self ):
		W=self.puzzle.board_w
		H=self.puzzle.board_h
		WH = W*H
		if len(self.conflicts_indexes_allowed) == 0:
			return

		for depth in range(WH):
			conflicts_array = [ x for x in self.conflicts_indexes_allowed if x <= depth ]
			self.heuristic_conflicts_count[ self.spaces_sequence[ depth ] ] = len(conflicts_array)


	# ----- The next seed to prepare the pieces
	def next_seed(self):
		self.seed = random.randint(0, sys.maxsize)

		return self.seed

if __name__ == "__main__":
	import data

	p = data.loadPuzzle()


