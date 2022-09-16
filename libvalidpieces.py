# Global Libs
import os
import sys
import ctypes
import multiprocessing
import math
import itertools

# Local Libs
import external_libs

#
# Generates C Valid Pieces to be used by the program
#


class LibValidpieces( external_libs.External_Libs ):
	"""ValidPieces generation library"""

	MACROS_NAMES_A = [ "valid_pieces" ]

	static_references = {}


	def __init__( self, puzzle, extra_name="", skipcompile=False ):

		self.name = "libvalidpieces"

		self.puzzle = puzzle


		# Params for External_Libs
		self.EXTRA_NAME = extra_name
		self.GCC_EXTRA_PARAMS = ""
		self.dependencies = [ "defs" ]
		self.modules_names = self.MACROS_NAMES_A

		# We always want to generate new lists of pieces
		#self.force_compile = True

		external_libs.External_Libs.__init__( self, skipcompile )



	# ----- Load the C library
	def load( self ):

		self.LibExt = ctypes.cdll.LoadLibrary( self.getNameSO() )

	def chunks(self, lst, n):
		"""Yield successive n-sized chunks from lst."""
		for i in range(0, len(lst), n):
			yield lst[i:i + n]

	# ----- generate arrays
	def getDefineValidPieces( self, only_signature=False ):
		output = []
		W=self.puzzle.board_w
		H=self.puzzle.board_h
		WH=self.puzzle.board_wh

		# ---------------------------------
		if only_signature:
			output.append( (0 , "extern t_piece_full static_valid_pieces[];") )
		else:
			output.append( (0 , "t_piece_full static_valid_pieces[WH*WH*4] = {") )

			for space in range(WH):
				x = 0
				s = ""
				for p in self.puzzle.static_valid_pieces[space]:
					s += "{ .u = "+format(p.u, "2")+ ", .r = "+format(p.r, "2")+ ", .d = "+format(p.d, "2") +", .l = "+format(p.l, "2") + " },"
					x += 1

				# Padding with empty
				for n in range(x, WH*4):
					s += "{ .u = "+format(0xff, "2")+ ", .r = "+format(0xff, "2")+ ", .d = "+format(0xff, "2") +", .l = "+format(0xff, "2") + " }" + (", " if x < WH*4-1 else "")

				output.append( (2, s) )

			output.append( (2 , "};") )
			output.append( (0 , "") )



		return output


	# ----- generate LibGen Header
	def GenerateH( self ):

		gen = open( self.getNameH(temp=True), "w" )

		self.writeGen( gen, self.getHeaderH() )
		
		WH=self.puzzle.board_wh

		
		output = []
		
		output.extend( [
			( 0, "// Piece Full" ),
			( 0, "struct st_piece_full {" ),
			( 2, 	"uint8 u; // up" ),
			( 2, 	"uint8 r; // right" ),
			( 2, 	"uint8 d; // down" ),
			( 2, 	"uint8 l; // left" ),
			( 0, "};" ),
			( 0, "typedef struct st_piece_full t_piece_full;" ),
			( 0, "typedef t_piece_full * p_piece_full;" ),
			] )

		output.extend( [
			( 0, "// Valid Pieces" ),
			( 0, "typedef t_piece_full t_valid_pieces[ WH*WH*4 ];" ),
			( 0, "typedef t_valid_pieces * p_valid_pieces;" ),
			] )


		self.writeGen( gen, output )
		
		self.writeGen( gen, self.getDefineValidPieces(only_signature=True) )


		self.writeGen( gen, self.getFooterH() )


	# ----- generate LibGen
	def GenerateC( self, module=None ):

		gen = open( self.getNameC(temp=True, module=module), "w" )
		self.writeGen( gen, self.getHeaderC( module=module ) )

		if module != None:
			macro_name = module
		else:
			macro_name = ""

		if macro_name == "valid_pieces":

			self.writeGen( gen, self.getDefineValidPieces() )
	
		self.writeGen( gen, self.getFooterC() )


	# ----- Self test of all the filtering functions
	def SelfTest( self ):

		return False


if __name__ == "__main__":
	import data

	p = data.loadPuzzle()
	if p != None:
		lib = LibValidpieces( p )
		while lib.SelfTest():
			pass

