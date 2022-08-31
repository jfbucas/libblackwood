# Global Libs
import os
import sys
import time
import datetime
import select
import random
import multiprocessing
import itertools
import ctypes

# Local Libs
import defs
import puzzle
import scenarios
import data


class Explorer( defs.Defs ):
	"""Defines exploration"""

	puzzle = None
	valid_pieces_depth = None

	# ----- Init the puzzle
	def __init__( self ):
		"""
		Initialize
		"""

		defs.Defs.__init__( self )

		self.puzzle = data.loadPuzzle()

		self.board_w = self.puzzle.board_w
		self.board_h = self.puzzle.board_h
		self.board_wh = self.puzzle.board_wh


		self.filterValidPieces( self.puzzle.static_valid_pieces )


	# ----- Filter the valid_pieces
	def filterValidPieces( self, valid_pieces ):


		current_valid_pieces = valid_pieces

		removed = -1
		while removed != 0:
			removed = 0
			new_valid_pieces = [None] * self.board_wh

			patterns_border = {"u":{0:True}, "r":{0:True}, "d":{0:True}, "l":{0:True}}
			patterns_seen = [ ]
			for space in range(self.puzzle.board_wh):
				patterns_seen.append( {"u":{}, "r":{}, "d":{}, "l":{}} )

			for space in range(self.puzzle.board_wh):
				for i in range(0, self.MAX_NB_COLORS):
					patterns_seen[ space ]["u"][i] = False
					patterns_seen[ space ]["r"][i] = False
					patterns_seen[ space ]["d"][i] = False
					patterns_seen[ space ]["l"][i] = False

			for space in range(self.puzzle.board_wh):
				for p in current_valid_pieces[ space ]:
					patterns_seen[ space ]["u"][p.u] = True
					patterns_seen[ space ]["r"][p.r] = True
					patterns_seen[ space ]["d"][p.d] = True
					patterns_seen[ space ]["l"][p.l] = True

				#print(space)
				#print(patterns_seen[space]["u"])
				#print(patterns_seen[space]["r"])
				#print(patterns_seen[space]["d"])
				#print(patterns_seen[space]["l"])

			for space in range(self.puzzle.board_wh):
				new_valid_list = []

				space_u_patterns = patterns_border["d"]
				space_r_patterns = patterns_border["l"]
				space_d_patterns = patterns_border["u"]
				space_l_patterns = patterns_border["r"]
					
				
				if ((space % self.board_w) != 0          )	: space_l_patterns = patterns_seen[space-1]["r"]
				if ((space % self.board_w) != (self.board_w-1))	: space_r_patterns = patterns_seen[space+1]["l"]
				if (space >= self.board_w)			: space_u_patterns = patterns_seen[space-self.board_w]["d"]
				if (space < (self.board_wh - self.board_w))	: space_d_patterns = patterns_seen[space+self.board_w]["u"]



				for p in current_valid_pieces[ space ]:
					if not space_u_patterns[ p.u ] or \
					   not space_r_patterns[ p.r ] or \
					   not space_d_patterns[ p.d ] or \
					   not space_l_patterns[ p.l ]:
						removed += 1
					else:
						new_valid_list.append(p)

				new_valid_pieces[space] = new_valid_list

			current_valid_pieces = new_valid_pieces


			
			if self.DEBUG_STATIC > 0:
				self.info( " * New Valid pieces" )
				a = []
				for space in range(self.board_wh):
					a.append(len(new_valid_pieces[ space ]))

				self.printArray( a, array_w=self.board_w, array_h=self.board_h)
				

				#if self.DEBUG_STATIC > 4:
				#	for space in range(self.board_wh):
				#		if self.static_spaces_type[ space ] == "border":
				#			print(self.static_valid_pieces[ space ])
		
		return current_valid_pieces



if __name__ == "__main__":

	e = Explorer()



# Lapin
