# Global Libs
import os
import sys
import ctypes
import multiprocessing
import math

# Local Libs
import external_libs

#
# Generates C Arrays to be used by the program
#


class LibArrays( external_libs.External_Libs ):
	"""Arrays generation library"""

	MACROS_NAMES_A = [ "arrays" ]

	static_references = {}


	def __init__( self, puzzle, extra_name="" ):

		self.name = "libarrays"

		self.puzzle = puzzle

		# Params for External_Libs
		self.EXTRA_NAME = extra_name
		self.GCC_EXTRA_PARAMS = ""
		self.dependencies = [ "defs" ]
		self.modules_names = self.MACROS_NAMES_A

		# We always want to generate new random lists of pieces
		#self.force_compile = True

		external_libs.External_Libs.__init__( self )



	# ----- Load the C library
	def load( self ):


		self.LibExt = ctypes.cdll.LoadLibrary( self.getNameSO() )

	def chunks(self, lst, n):
		"""Yield successive n-sized chunks from lst."""
		for i in range(0, len(lst), n):
			yield lst[i:i + n]

	# ----- generate arrays
	def getDefineArrays( self, only_signature=False ):
		output = []

		# ---------------------------------
		if only_signature:
			output.append( (0 , "uint64 seed;") )
		else:
			output.append( (0 , "uint64 seed = "+str(self.puzzle.seed)+";" ) )

		# ---------------------------------
		if only_signature:
			for name,array in self.puzzle.master_index.items():
				output.append( (0 , "uint64 master_index_"+name+"[ "+str(len(array))+" ];") )
		else:
			for name,array in self.puzzle.master_index.items():
				output.append( (0 , "uint64 master_index_"+name+"[] = {") )
			
				l = len([x for x in self.chunks(array, 32)])
				for x in self.chunks(array, 32):
					output.append( (2 , ", ".join([format(n, '6') if n != None else "0xffff" for n in x]) + ( "," if l!=0 else "" )) )
					l -= 1

				output.append( (2 , "};") )
				output.append( (0 , "") )


		# ---------------------------------
		if only_signature:
			output.append( (0 , "p_rotated_piece master_lists_of_rotated_pieces[ "+str(len(self.puzzle.master_lists_of_rotated_pieces))+" ];") )
		else:
			output.append( (0 , "p_rotated_piece master_lists_of_rotated_pieces[] = {") )
			for x in self.chunks(self.puzzle.master_lists_of_rotated_pieces, 8):
				output.append( (2 , ", ".join(["&(master_all_rotated_pieces["+format(n, '6')+"])" if n != None else format("NULL", '36') for n in x]) + ( "," if len(x)==8 else "" )) )

			output.append( (2 , "};") )
			output.append( (0 , "") )



		# ---------------------------------
		if only_signature:
			output.append( (0 , "t_rotated_piece master_all_rotated_pieces[ "+str(len(self.puzzle.master_all_rotated_pieces))+" ];") )
		else:
			output.append( (0 , "t_rotated_piece master_all_rotated_pieces[] = {") )
			l = sorted(self.puzzle.master_all_rotated_pieces.keys())
			for y in l:
				x = self.puzzle.master_all_rotated_pieces[y]
				output.append( (2, "{ .p ="+format(x.p, "3")+ ", .u ="+format(x.u, "3")+ ",  .r ="+format(x.r, "3") + ", .heuristic_side_and_break_count =("+format(x.heuristic_side_count, "3") + "<< 1) +"+format(x.break_count, "3")+ "  }" + (", " if str(x) != l[-1] else "") + " // " + y) )

			output.append( (2 , "};") )
			output.append( (0 , "") )

		
		
		# ---------------------
		if only_signature:
			output.append( (0 , "t_piece pieces[WH];") )
		else:

			output.append( (0 , "t_piece pieces[] = {") )
			x = 0
			for p in self.puzzle.pieces:
				output.append( (2, "{ .u = "+format(p[0], "2")+ ", .r = "+format(p[1], "2")+ ", .d = "+format(p[2], "2") +", .l = "+format(p[3], "2") + " }" + (", " if x < self.puzzle.board_wh-1 else "") + " // " + str(x)) )
				x += 1
			output.append( (2 , "};") )
			output.append( (0 , "") )


		# ---------------------
		if only_signature:
			output.append( (0 , "uint8 spaces_board_sequence[WH];") )
		else:

			output.append( (0 , "uint8 spaces_board_sequence[] = {") )
			for y in range(self.puzzle.board_h):
				output.append( (2 , ",".join([format(n, '3') for n in self.puzzle.spaces_board_sequence[y*self.puzzle.board_w:(y+1)*self.puzzle.board_w]]) + ( "," if y<(self.puzzle.board_h-1) else "" )) )
			output.append( (2 , "};") )
			output.append( (0 , "") )
			
		# ---------------------
		if only_signature:
			output.append( (0 , "uint8 spaces_patterns_sequence[WH];") )
		else:

			output.append( (0 , "uint8 spaces_patterns_sequence[] = {") )
			for y in range(self.puzzle.board_h):
				output.append( (2 , ",".join([format(n, '3') for n in self.puzzle.spaces_patterns_sequence[y*self.puzzle.board_w:(y+1)*self.puzzle.board_w]]) + ( "," if y<(self.puzzle.board_h-1) else "" )) )
			output.append( (2 , "};") )
			output.append( (0 , "") )
			

		# ---------------------
		if only_signature:
			output.append( (0 , "uint64 heartbeat_time_bonus[WH];") )
		else:

			output.append( (0 , "uint64 heartbeat_time_bonus[] = {") )
			for y in range(self.puzzle.board_h):
				output.append( (2 , ",".join([format(n, '3') for n in [ int(2*pow(3, (x+y*self.puzzle.board_w)-250)*60) if (x+y*self.puzzle.board_w)>250 else 0 if x+y>0 else 60*45 for x in range(self.puzzle.board_w)]]) + ( "," if y<(self.puzzle.board_h-1) else "" )) )
			output.append( (2 , "};") )
			output.append( (0 , "") )
			

		return output


	
	# ----- generate LibGen Header
	def GenerateH( self ):

		gen = open( self.getNameH(temp=True), "w" )

		self.writeGen( gen, self.getHeaderH() )

		
		output = []

		
		output.extend( [

			( 0, "// Rotated Piece" ),
			( 0, "struct st_rotated_piece {" ),
			( 1,	"uint8 p;" ),
			( 1,	"uint8 u;" ),
			( 1,	"uint8 r;" ),
			( 1,	"uint8 heuristic_side_and_break_count;" ),
			( 0, "};" ),
			( 0, "typedef struct st_rotated_piece t_rotated_piece;" ),
			( 0, "typedef struct st_rotated_piece * p_rotated_piece;" ),
			( 0, "" ),
			( 0, "" ),
			( 0, "" ),
			( 0, "" ),
			( 0, "" ),
			( 0, "// Piece" ),
			( 0, "struct st_piece {" ),
			( 2, 	"uint8 u; // up" ),
			( 2, 	"uint8 r; // right" ),
			( 2, 	"uint8 d; // down" ),
			( 2, 	"uint8 l; // left" ),
			( 0, "};" ),
			( 0, "typedef struct st_piece t_piece;" ),
			] )



		self.writeGen( gen, output )
		
		self.writeGen( gen, self.getDefineArrays(only_signature=True) )


		self.writeGen( gen, self.getFooterH() )


	# ----- generate LibGen
	def GenerateC( self, module=None ):

		gen = open( self.getNameC(temp=True, module=module), "w" )
		self.writeGen( gen, self.getHeaderC( module=module ) )

		if module != None:
			macro_name = module
		else:
			macro_name = ""

		if macro_name == "arrays":

			self.writeGen( gen, self.getDefineArrays() )
	

		self.writeGen( gen, self.getFooterC() )


	# ----- Self test of all the filtering functions
	def SelfTest( self ):

		return False


if __name__ == "__main__":
	import data

	p = data.loadPuzzle()
	if p != None:
		lib = LibArrays( p )
		while lib.SelfTest():
			pass

