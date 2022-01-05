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


	def __init__( self, puzzle, extra_name="", skipcompile=False ):

		self.name = "libarrays"

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
	def getDefineArrays( self, only_signature=False ):
		output = []
		W=self.puzzle.board_w
		H=self.puzzle.board_h
		WH=self.puzzle.board_wh

		LAST =  len(self.puzzle.master_lists_of_rotated_pieces)-1

		# ---------------------------------
		if not only_signature:
			output.append( (0 , "#define LAST "+format(LAST, '6')) )

		# ---------------------------------
		if only_signature:
			for name,array in self.puzzle.master_index.items():
				output.append( (0 , "extern uint64 master_index_"+name+"[ "+str(len(array))+" ];") )
		else:
			for name,array in self.puzzle.master_index.items():
				output.append( (0 , "uint64 master_index_"+name+"[] = {") )
			
				l = len([x for x in self.chunks(array, 1<<self.EDGE_SHIFT_LEFT)])
				for x in self.chunks(array, 1<<self.EDGE_SHIFT_LEFT):
					output.append( (2 , ", ".join([format(n, '6') if n != None else "  LAST" for n in x]) + ( "," if l!=0 else "" )) )
					l -= 1

				output.append( (2 , "};") )
				output.append( (0 , "") )

		# ---------------------------------
		if not only_signature:
			output.append( (0, "// master_all_rotated_pieces") )
			output.append( (1 , "#define MAURPNULL { .value = 0 }" )) 
			l = sorted(self.puzzle.master_all_rotated_pieces.keys())
			n = 0
			for y in l:
				x = self.puzzle.master_all_rotated_pieces[y]

				edges = ", .u ="+format(x.u, "3")+ ", .r ="+format(x.r, "3")+ ", .d ="+format(x.d, "3")+ ",  .l ="+format(x.l, "3")

				heuristic_patterns = ""
				for i in range(5):
					if sum(self.puzzle.scenario.heuristic_patterns_count[i]) > 0:
						heuristic_patterns += ", .heuristic_patterns_"+str(i)+" ="+format(x.heuristic_patterns_count[i], "3")

				heuristic_stats16 = ""
				if self.puzzle.scenario.heuristic_stats16:
					heuristic_stats16 = ", .heuristic_stats16_count ="+format(x.heuristic_stats16_count, "3")

				output.append( (1, "#define MAURP"+str(n)+" { .info = { " \
					".p ="+format(x.p, "3")+ \
					edges + \
					heuristic_patterns + \
					heuristic_stats16 + \
					", .heuristic_conflicts ="+format(x.conflicts_count, "3")+ \
					" } }" + " // " + y + "  #" +str(n)) )
				n += 1

			output.append( (0 , "") )

		

		# ---------------------------------
		if only_signature:
			output.append( (0 , "extern t_union_rotated_piece master_lists_of_union_rotated_pieces[ "+str(len(self.puzzle.master_lists_of_rotated_pieces))+" ];") )
			output.append( (0 , "#define MAURP master_all_union_rotated_pieces") )
		else:
			
			output.append( (0 , "t_union_rotated_piece master_lists_of_union_rotated_pieces[] = {") )
			v = 0
			for x in self.chunks(self.puzzle.master_lists_of_rotated_pieces, 16):
				output.append( (2 , ", ".join([format("MAURP"+str(n),"8") if n != None else format("MAURPNULL", '8') for n in x]) + ( "," if len(x)==16 else " " ) + "  // "+str(v)) )
				v += 16

			output.append( (2 , "};") )
			output.append( (0 , "") )



		# ---------------------------------
		if only_signature:
			output.append( (0 , "extern t_union_rotated_piece master_all_union_rotated_pieces[ "+str(len(self.puzzle.master_all_rotated_pieces))+" ];") )
		else:
			output.append( (0 , "t_union_rotated_piece master_all_union_rotated_pieces[] = {") )
			l = sorted(self.puzzle.master_all_rotated_pieces.keys())
			n = 0
			for y in l:
				x = self.puzzle.master_all_rotated_pieces[y]
				output.append( (2, "MAURP"+str(n) + (", " if str(x) != l[-1] else "  ") + " // " + y + "  #" +str(n)) )

				n += 1

			output.append( (2 , "};") )
			output.append( (0 , "") )

		
		
		# ---------------------
		if only_signature:
			output.append( (0 , "extern t_piece pieces[WH];") )
		else:

			output.append( (0 , "t_piece pieces[] = {") )
			x = 0
			for p in self.puzzle.pieces:
				output.append( (2, "{ .u = "+format(p[0], "2")+ ", .r = "+format(p[1], "2")+ ", .d = "+format(p[2], "2") +", .l = "+format(p[3], "2") + " }" + (", " if x < WH-1 else "") + " // #" + str(x)) )
				x += 1
			output.append( (2 , "};") )
			output.append( (0 , "") )


		# ---------------------
		if only_signature:
			output.append( (0 , "extern uint8 spaces_sequence[WH];") )
		else:

			output.append( (0 , "uint8 spaces_sequence[] = {") )
			for y in range(H):
				output.append( (2 , ",".join([format(n, '3') for n in self.puzzle.scenario.spaces_sequence[y*W:(y+1)*W]]) + ( "," if y<(H-1) else "" )) )
			output.append( (2 , "};") )
			output.append( (0 , "") )
			
		# ---------------------
		if only_signature:
			for i in range(5):
				if sum(self.puzzle.scenario.heuristic_patterns_count[i]) > 0:
					output.append( (0 , "extern uint64 heuristic_patterns_count_"+str(i)+"[WH];") )
		else:

			for i in range(5):
				if sum(self.puzzle.scenario.heuristic_patterns_count[i]) > 0:
					output.append( (0 , "uint64 heuristic_patterns_count_"+str(i)+"[] = {") )
					for y in range(H):
						output.append( (2 , ",".join([format(n, '3') for n in self.puzzle.scenario.heuristic_patterns_count[i][y*W:(y+1)*W]]) + ( "," if y<(H-1) else "" )) )
					output.append( (2 , "};") )
					output.append( (0 , "") )
			

		# ---------------------
		if only_signature:
			output.append( (0 , "extern uint64 heartbeat_time_bonus[WH];") )
		else:

			output.append( (0 , "uint64 heartbeat_time_bonus[] = {") )
			for y in range(H):
				output.append( (2 , ",".join([format(n, '3') for n in [ int(2*pow(3, (x+y*W)-250)*60) if (x+y*W)>250 else 0 if x+y>0 else 60*self.puzzle.scenario.timelimit for x in range(W)]]) + ( "," if y<(H-1) else "" )) )
			output.append( (2 , "};") )
			output.append( (0 , "") )
			

		# ---------------------
		if not only_signature:

			output.append( (0 , "/* Get Index Piece Name") )
			array = [ "" ] * WH
			for y in range(H):
				l = "// "
				for x in range(W):
					d = x+y*W
					array[ self.puzzle.scenario.spaces_sequence[d] ] += format(self.puzzle.scenario.get_index_piece_name(x+y*W), "19")
			for y in range(H):
				l = "// "+" ".join(array[y*W:(y+1)*W])
				output.append( (0 , l) )
			output.append( (0 , "*/") )
			output.append( (0 , "") )
			

		# ---------------------
		if not only_signature:

			output.append( (0 , "/* Get References") )
			o = self.printArray(self.puzzle.scenario.spaces_references, array_w=W, array_h=H, noprint=True)
			output.append( (0 , o) )
			output.append( (0 , "*/") )
			output.append( (0 , "") )
			
		# ---------------------
		if not only_signature:
			output.append( (0 , "/* Get Sequence") )
			tmp = [ " " ] * WH
			for depth in range(WH):
				tmp[ self.puzzle.scenario.spaces_sequence[ depth ] ] = "X"
				o = self.printArray(tmp, array_w=W, array_h=H, noprint=True)
				output.append((0, "---[ Sequence " + str(depth) + " ]---\n" + o))
			output.append( (0 , "*/") )
			output.append( (0 , "") )


		return output


	
	# ----- generate LibGen Header
	def GenerateH( self ):

		gen = open( self.getNameH(temp=True), "w" )

		self.writeGen( gen, self.getHeaderH() )

		
		output = []
		
		heuristic_stats16 = ""
		if self.puzzle.scenario.heuristic_stats16:
			heuristic_stats16 = "uint8 heuristic_stats16_count;"

		heuristic_patterns = ""
		for i in range(5):
			if sum(self.puzzle.scenario.heuristic_patterns_count[i]) > 0:
				heuristic_patterns += "uint8 heuristic_patterns_"+str(i)+";"

		output.extend( [
			( 0, "// Rotated Piece Union" ),
			( 0, "union union_rotated_piece {" ),
			( 1,	"struct {" ),
			( 2,		"uint8 p;" ),
			( 2,		"uint8 u;" ),
			( 2,		"uint8 r;" ),
			( 2,		"uint8 d;" ),
			( 2,		"uint8 l;" ),
			( 2,		heuristic_stats16 ),
			( 2,		heuristic_patterns ),
			( 2,		"uint8 heuristic_conflicts;" ),
			( 1,	"} info;" ),
			( 1,	"uint64 value;" ),
			( 0, "};" ),
			( 0, "typedef union union_rotated_piece t_union_rotated_piece;" ),
			( 0, "typedef union union_rotated_piece * p_union_rotated_piece;" ),
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

