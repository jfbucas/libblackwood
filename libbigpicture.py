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
import signal

import png
import math

# Local Libs
import defs
import puzzle
import scenarios
import data
import external_libs


class LibBigPicture( external_libs.External_Libs ):
	"""Defines exploration"""

	MACROS_NAMES_A = [ "utils", "generate", "main" ]
	MACROS_NAMES_B = [ ]

	FLAGS = [
			[ "Time to finish",		"time_to_finish",		"TTF" ],
			[ "Leave CPU alone",		"leave_cpu_alone",		"LCA" ],
			[ "Pause",			"pause",			"Pause" ],
			[ "Wait for Notification",	"wait_for_notification",	"WFN" ],
			[ "Send a Notification",	"send_a_notification",		"SFN" ],
			[ "Time Heartbeat",		"heartbeat",			"HB" ],
			[ "Max number of heartbeats",	"heartbeat_limit", 		"HBLimit" ],
			[ "Check for Commands",		"check_commands",		"CheckCommands" ],
			[ "Commands for Interactivity",	"commands",			"Commands" ],
			[ "Show help",			"help",				"Help" ],
			[ "Max Depth Seen",		"best_depth_seen",		"BestDepthSeen" ],
			[ "Seed",			"seed",				"Seed" ],
		]

	puzzle = None
	valid_pieces_depth = None

	# ----- Init the puzzle
	def __init__( self, puzzle, extra_name="", skipcompile=False ):
		"""
		Initialize
		"""
		self.name = "libbigpicture"

		self.puzzle = puzzle
		


		# Params for External_Libs
		#self.EXTRA_NAME = extra_name
		self.GCC_EXTRA_PARAMS = ""
		self.dependencies = [ "defs", "arrays", "validpieces" ]
		self.modules_names = self.MACROS_NAMES_A + self.MACROS_NAMES_B
		self.modules_optimize = [ "generate" ]

		external_libs.External_Libs.__init__( self, skipcompile )


	"""
		defs.Defs.__init__( self )

		self.puzzle = data.loadPuzzle()
		self.valid_pieces = self.filterValidPieces( self.puzzle.static_valid_pieces )
		
		#self.fixPiece(self.puzzle, self.valid_pieces)
		#self.getJobs(self.valid_pieces, max_width=128, max_height=128)
		self.getJobs(self.valid_pieces)
		self.getImages()
	"""

	# ----- Load the C library
	def load( self ):

		self.LibExt = ctypes.cdll.LoadLibrary( self.getNameSO() )

		signatures = []
		#signatures.extend( self.gen_getter_setter_function( only_signature=True ) )
		#signatures.extend( self.gen_allocate_blackwood_function( only_signature=True ) )
		#signatures.extend( self.gen_getSolutionURL_function( only_signature=True ) )
		#signatures.extend( self.gen_getBestDepthSeenHeartbeat_function( only_signature=True ) )
		#signatures.extend( self.gen_solve_function(only_signature=True) )
		#signatures.extend( self.gen_do_commands(only_signature=True ) )
		#signatures.extend( self.gen_set_blackwood_arrays_function(only_signature=True ) )
		signatures.extend( self.gen_print_valid_pieces_functions(only_signature=True) )
		
		self.defineFunctionsArgtypesRestype( signatures )


	# ----- generate definitions
	def getDefinitions( self, only_signature=False ):
		output = []

		# Bigpicture
		if only_signature:

			output.extend( [
				( 0, "// Job" ),
				( 0, "struct st_job {" ),
				( 2, 	"uint64 x;" ),
				( 2, 	"uint64 y;" ),
				( 2, 	"t_valid_pieces valid_pieces;" ),
				( 0, "};" ),
				( 0, "typedef struct st_job t_job;" ),
			] )

			output.extend( [
				( 0, "// Patterns Seen" ),
				( 0, "struct st_patterns_seen {" ),
				( 2, 	"uint64 u;" ),
				( 2, 	"uint64 r;" ),
				( 2, 	"uint64 d;" ),
				( 2, 	"uint64 l;" ),
				( 0, "};" ),
				( 0, "typedef struct st_patterns_seen t_patterns_seen;" ),
			] )

			output.extend( [
				(0, "// Structure Big Picture"),
				(0, "struct st_bigpicture {"),
				(0, "" ),
				] )

			output.extend( [
				(0, "" ),
				(0, "" ),
				] )

			for (c, n, s) in self.FLAGS:
				output.extend( [
				(1, "// Flag "+c+" -- "+s+" for short"),
				(1, "uint64	"+n+";"),
				(0, "" ),
				] )

			output.extend( [
				(0, ""),
				(0 , "};"),
				(0, ""),
				] )

			output.append( (0 , "") )
			output.append( (0 , "typedef struct st_bigpicture   t_bigpicture;") )
			output.append( (0 , "typedef t_bigpicture *         p_bigpicture;") )
			output.append( (0 , "") )
			output.append( (0 , "") )

			output.append( (0 , "// A global pointer") )
			output.append( (0 , "extern p_bigpicture global_bigpicture;") )
			output.append( (0 , "") )
		else:
			output.append( (0 , "// A global pointer") )
			output.append( (0 , "p_bigpicture global_bigpicture;") )
			output.append( (0 , "") )


		return output

	# ----- Generate finish flag https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Flag_of_Finland.svg/383px-Flag_of_Finland.svg.png
	def gen_sig_handler_function( self, only_signature=False ):

		output = [
			(0, "void sig_handler("),
			(1, "int signo"),
			]

		if only_signature:
			output.extend( [ (1, ');'), ])
			return output


		output.extend( [
			(1, ") {"),
			(1, 'if (signo == SIGINT) { printf( "Ctrl-C received. Interrupting.\\n"); setCheckCommands(global_bigpicture, 1); setTTF(global_bigpicture, 1); }'),
			#(1, 'if (signo == SIGUSR1) { incHB(global_blackwood); setCheckCommands(global_blackwood, 1); }'),
			#(1, 'if (signo == SIGUSR2) { togglePause(global_blackwood); setCheckCommands(global_blackwood, 1); }'),
			(0, "}"),
			])

		return output

	# ----- Generate get time to finish
	def gen_getter_setter_function( self, only_signature=False ):

		output = []
		for (c, n, s) in self.FLAGS:

			output.append( (0, "// "+c+" functions"), )

			# ---------------------------------------
			output.append( (0, "void clear"+s+"("), )
			output.append( (1, "voidp b"), )
			if only_signature:
				output.append( (1, ');') )
			else:
				output.append( (1, ') {'), ) 
				output.append( (2, 'if (b) ((p_bigpicture)b)->'+n+' = 0;'), ) 
				output.append( (2, 'else DEBUG_PRINT(("NULL on clear'+s+'\\n" ));'), )
				output.append( (1, '}'), ) 

			# ---------------------------------------
			output.append( (0, "uint64 get"+s+"("), )
			output.append( (1, "voidp b"), )
			if only_signature:
				output.append( (1, ');') )
			else:
				output.append( (1, ') {'), ) 
				output.append( (2, 'if (b) return ((p_bigpicture)b)->'+n+';'), ) 
				output.append( (2, 'DEBUG_PRINT(("NULL on get'+s+'\\n" ));'), )
				output.append( (2, 'return 0;'), ) 
				output.append( (1, '}'), ) 

			# ---------------------------------------
			output.append( (0, "void set"+s+"("), )
			output.append( (1, "voidp b,"), )
			output.append( (1, "uint64 v"), )
			if only_signature:
				output.append( (1, ');') )
			else:
				output.append( (1, ') {'), ) 
				output.append( (2, 'if (b) ((p_bigpicture)b)->'+n+' = v;'), ) 
				output.append( (2, 'else DEBUG_PRINT(("NULL on set'+s+'\\n" ));'), )
				output.append( (1, '}'), ) 

			# ---------------------------------------
			output.append( (0, "void or"+s+"("), )
			output.append( (1, "voidp b,"), )
			output.append( (1, "uint64 v"), )
			if only_signature:
				output.append( (1, ');') )
			else:
				output.append( (1, ') {'), ) 
				output.append( (2, 'if (b) ((p_bigpicture)b)->'+n+' |= v;'), ) 
				output.append( (2, 'else DEBUG_PRINT(("NULL on or'+s+'\\n" ));'), )
				output.append( (1, '}'), ) 
			
			# ---------------------------------------
			output.append( (0, "void xor"+s+"("), )
			output.append( (1, "voidp b,"), )
			output.append( (1, "uint64 v"), )
			if only_signature:
				output.append( (1, ');') )
			else:
				output.append( (1, ') {'), ) 
				output.append( (2, 'if (b) ((p_bigpicture)b)->'+n+' ^= v;'), ) 
				output.append( (2, 'else DEBUG_PRINT(("NULL on xor'+s+'\\n" ));'), )
				output.append( (1, '}'), ) 
			
			# ---------------------------------------
			output.append( (0, "void inc"+s+"("), )
			output.append( (1, "voidp b"), )
			if only_signature:
				output.append( (1, ');') )
			else:
				output.append( (1, ') {'), ) 
				output.append( (2, 'if (b) ((p_bigpicture)b)->'+n+' ++;'), ) 
				output.append( (2, 'else DEBUG_PRINT(("NULL on inc'+s+'\\n" ));'), )
				output.append( (1, '}'), ) 
			
			# ---------------------------------------
			output.append( (0, "void dec"+s+"("), )
			output.append( (1, "voidp b"), )
			if only_signature:
				output.append( (1, ');') )
			else:
				output.append( (1, ') {'), ) 
				output.append( (2, 'if (b) ((p_bigpicture)b)->'+n+' --;'), ) 
				output.append( (2, 'else DEBUG_PRINT(("NULL on dec'+s+'\\n" ));'), )
				output.append( (1, '}'), ) 
			
			# ---------------------------------------
			output.append( (0, "void toggle"+s+"("), )
			output.append( (1, "voidp b"), )
			if only_signature:
				output.append( (1, ');') )
			else:
				output.append( (1, ') {'), ) 
				output.append( (2, 'if (b) ((p_bigpicture)b)->'+n+' = ~((p_bigpicture)b)->'+n+';'), ) 
				output.append( (2, 'else DEBUG_PRINT(("NULL on toggle'+s+'\\n" ));'), )
				output.append( (1, '}'), ) 
			
		return output

	# ----- Generate print functions
	def gen_print_valid_pieces_functions( self, only_signature=False ):

		output = []

		uname = "pieces"

		W=self.puzzle.board_w
		H=self.puzzle.board_h
		WH=self.puzzle.board_wh

		for prefix in [ "", "s", "f" ]:

			if prefix == "":
				out = ""
			elif prefix == "s":
				out = "s_out,"
			elif prefix == "f":
				out = "f_out,"

			# ----------------------------------
			for dest in [ "", "_for_stats" ]:

				output.extend( [ 
					(0, "void "+prefix+"print_valid_pieces"+dest+"("),
					(1, "charp s_out,"  if (prefix == "s") else "" ),
					(1, "FILE   * f_out," if (prefix == "f") else "" ),
					(1, "t_piece_full * valid_pieces"),
					] )

				if only_signature:
					output.extend( [ (1, ');'), ])
					continue
					
				output.extend( [
					(1, ") {"),
					(1, "uint64 space, x, y, piece_index;"),
					(1, "int64 count, total;"),
					(1, "uint64 space_count[WH];"),
					(0, ''), 
					(1, 'total = 0;' ),
					(0, ''), 
					(1, 'for (space = 0; space < WH; space++) {' ),
					(2, 'space_count[space] = 0;' ),
					(2, 'while (valid_pieces[space*WH*4+space_count[space]].u != 0xff) { space_count[space]++; }' ),
					(2, 'total += space_count[space];' ),
					(1, '}' ),
					] )

				if dest == "":
					output.extend( [
						(1, 'for (y = 0; y < H; y++) {' ),
						(2, 'for (x = 0; x < W; x++) {' ),
						(3, 'count = space_count[ x+(y*W) ];' ),
						(3, 'if (count <= 0) {' ),
						(4, prefix+'printf( '+out+'"  . " );' ),
						] )

					output.extend( [
						(1, '} else if (count < 1000) {' ),
						(2, prefix+'printf( '+out+'"'+self.verdoie +"%3llu"+self.XTermNormal+' ", count/1);' ),
						(3, '} else if (count < 1000000) {' ),
						(4, prefix+'printf( '+out+'"'+self.jaunoie +"%3llu"+self.XTermNormal+' ", count/1000);' ),
						(3, '} else if (count < 1000000000) {' ),
						(4, prefix+'printf( '+out+'"'+self.rougeoie+"%3llu"+self.XTermNormal+' ", count/1000000);' ),
						(3, '} else if (count < 1000000000000) {' ),
						(4, prefix+'printf( '+out+'"'+self.violoie +"%3llu"+self.XTermNormal+' ", count/1000000000);' ),
						(3, '} else if (count < 1000000000000000) {' ),
						(4, prefix+'printf( '+out+'"'+self.bleuoie +"%3llu"+self.XTermNormal+' ", count/1000000000000);' ),
						] )

					output.extend( [
						(3, '} else {' ),
						(4, prefix+'printf( '+out+'"%3llu ", count);' ),
						(3, '}' ),
						(2, '} // x' ),
						(2, prefix+'printf( '+out+'"\\n" );' ),
						(1, '} // y' ),
						(1, prefix+'printf( '+out+'"\\n" );' ),
						(1, 'if (total == 0) {' ),
						(2, prefix+'printf( '+out+'"Total:  . '+uname+'\\n\\n" );' ),
						(1, '} else if (total < 1000) {' ),
						(2, prefix+'printf( '+out+'"Total: '+self.verdoie +"%3llu"+self.XTermNormal+' '+uname+'\\n\\n", total/1);' ),
						(1, '} else if (total < 1000000) {' ),
						(2, prefix+'printf( '+out+'"Total: '+self.jaunoie +"%3lluK"+self.XTermNormal+' '+uname+'\\n\\n", total/1000);' ),
						(1, '} else if (total < 1000000000) {' ),
						(2, prefix+'printf( '+out+'"Total: '+self.rougeoie+"%3lluM"+self.XTermNormal+' '+uname+'\\n\\n", total/1000000);' ),
						(1, '} else if (total < 1000000000000) {' ),
						(2, prefix+'printf( '+out+'"Total: '+self.violoie +"%3lluG"+self.XTermNormal+' '+uname+'\\n\\n", total/1000000000);' ),
						(1, '} else if (total < 1000000000000000) {' ),
						(2, prefix+'printf( '+out+'"Total: '+self.bleuoie +"%3lluT"+self.XTermNormal+' '+uname+'\\n\\n", total/1000000000000);' ),
						(1, '} else {' ),
						(2, prefix+'printf( '+out+'"Total: %3llu '+uname+'/s\\n\\n", total);' ),
						(1, '}' ),
						])

				elif dest == "_for_stats":
					output.extend( [
						(1, 'for (y = 0; y < H; y++) {' ),
						(2, 'for (x = 0; x < W; x++) {' ),
						(3, 'count = space_count[ x+(y*W) ];' ),
						(3, prefix+'printf( '+out+'"%llu ", count);' ),
						(2, '} // x' ),
						(1, '} // y' ),
						(1, prefix+'printf( '+out+'"\\n" );' ),
						(1, prefix+'printf( '+out+'"Total: %llu '+uname+'/s\\n", total );' ),
						])

				else:
					output.extend( [
						(1, 'for (y = 0; y < H; y++) {' ),
						(2, 'for (x = 0; x < W; x++) {' ),
						(3, 'count = space_count[ x+(y*W) ];' ),
						(3, prefix+'printf( '+out+'"%llu ", count);' ),
						(2, '} // x' ),
						(1, '} // y' ),
						(1, prefix+'printf( '+out+'"\\n" );' ),
						#(1, prefix+'printf( '+out+'"Total: %llu '+uname+'/s\\n", total );' ),
						])


				output.extend( [
					(1, 'fflush(stdout);' if prefix == "" else ""), 
					(0, '}' ),
					(0, ''), 
					] )


		return output

	# ----- Filter based on edges/patterns the valid_pieces list
	def gen_FilterValidPieces_function( self, only_signature=False ):
		
		output = [ 
			(0, "t_piece_full * filterValidPieces("),
			(1, "t_piece_full * valid_pieces"),
			]

		if only_signature:
			output.extend( [ (1, ');'), ])
			return output

		output.extend( [
			(1, ") {"),
			(1, ""),
			(2, "uint64 removed;"),
			(2, "uint64 space;"),
			(2, "uint64 piece_index, dst_piece_index;"),
			(2, "t_piece_full piece;"),
			(2, "t_patterns_seen patterns_seen[WH];"),
			(2, "t_patterns_seen local_patterns;"),
			(2, "t_piece_full * current_valid_pieces;" ),
			(2, "" ),
			(2, "t_piece_full tmp_valid_pieces[WH*WH*4];" ),
			(2, "t_piece_full * result_valid_pieces;" ),
			])

		output.extend( [
			(2, 'if (valid_pieces == NULL) return NULL;' ),
			])

		output.extend( [
			(2, 'current_valid_pieces = valid_pieces;' ),
			(2, 'result_valid_pieces = (t_piece_full *)(malloc(sizeof(t_valid_pieces)));;' ),
			(2, 'removed = 0xff;' ),
			(2, 'while (removed != 0) {' ),
			(3, '' ),
			(3, 'removed = 0;' ),
			(3, '' ),
			(3, 'for (space=0; space<WH; space++) {' ),
			(4, 'patterns_seen[space].u=0;' ),
			(4, 'patterns_seen[space].r=0;' ),
			(4, 'patterns_seen[space].d=0;' ),
			(4, 'patterns_seen[space].l=0;' ),
			(4, 'piece_index = space*WH*4;' ),
			(4, 'while (current_valid_pieces[piece_index].u != 0xff) {' ),
			(5, 'patterns_seen[space].u |= 1 << current_valid_pieces[piece_index].u;' ),
			(5, 'patterns_seen[space].r |= 1 << current_valid_pieces[piece_index].r;' ),
			(5, 'patterns_seen[space].d |= 1 << current_valid_pieces[piece_index].d;' ),
			(5, 'patterns_seen[space].l |= 1 << current_valid_pieces[piece_index].l;' ),
			(5, 'piece_index++;' ),
			(4, '}' ),
			(3, '}' ),
			(3, '' ),
			(3, 'for (space=0; space<WH; space++) {' ),
			(3, '' ),
			(4, '' ),
			(4, 'local_patterns.u = 1<<0;' ),
			(4, 'local_patterns.r = 1<<0;' ),
			(4, 'local_patterns.d = 1<<0;' ),
			(4, 'local_patterns.l = 1<<0;' ),
			(4, '' ),
			(4, 'if (space >= W)           { local_patterns.u = patterns_seen[space-W].d; }'), 
			(4, 'if ((space % W) != (W-1)) { local_patterns.r = patterns_seen[space+1].l; }'), 
			(4, 'if (space < (WH-W))       { local_patterns.d = patterns_seen[space+W].u; }'), 
			(4, 'if ((space % W) != 0    ) { local_patterns.l = patterns_seen[space-1].r; }'), 
			(4, '' ),
			(4, 'piece_index = space*WH*4;' ),
			(4, 'dst_piece_index = space*WH*4;' ),
			(4, 'while (current_valid_pieces[piece_index].u != 0xff) {' ),
			(5, '' ),
			(5, 'if ( (local_patterns.u & (1 << current_valid_pieces[piece_index].u)) &&' ),
			(5, '     (local_patterns.r & (1 << current_valid_pieces[piece_index].r)) &&' ),
			(5, '     (local_patterns.d & (1 << current_valid_pieces[piece_index].d)) &&' ),
			(5, '     (local_patterns.l & (1 << current_valid_pieces[piece_index].l)) ) {' ),
			(6, 'result_valid_pieces[dst_piece_index] = current_valid_pieces[piece_index];' ), 
			(6, 'dst_piece_index++;' ),
			(5, '} else {' ),
			(6, 'removed++;' ),
			(5, '}' ),
			(5, '' ),
			(5, 'piece_index++;' ),
			(4, '} // while' ),
			(4, '' ),
			(4, '// If nothing is copied, it is a deadend' ),
			(4, 'if (dst_piece_index == space*WH*4) {' ),
			(5, 'free(result_valid_pieces);' ),
			(5, 'return NULL;' ),
			(4, '}' ),
			(4, '' ),
			(4, '// Copy 0xff marker at the end of the list' ),
			(4, 'result_valid_pieces[dst_piece_index] = current_valid_pieces[piece_index];' ), 
			(4, '' ),
			(3, '} // For space' ),
			(3, '' ),
			(3, '// If we need to go again, we copy into tmp_valid_pieces to use it as the new source' ),
			(3, 'if (removed > 0) {' ),
			(4, 'current_valid_pieces = tmp_valid_pieces;' ),
			(4, 'for (space=0; space<WH; space++) {' ),
			(5, 'piece_index = space*WH*4;' ),
			(5, 'while (result_valid_pieces[piece_index].u != 0xff) {' ),
			(6, 'current_valid_pieces[piece_index] = result_valid_pieces[piece_index];' ), 
			(6, 'piece_index++;' ),
			(5, '}' ),
			(4, '// Copy 0xff marker at the end of the list' ),
			(4, 'current_valid_pieces[piece_index] = result_valid_pieces[piece_index];' ), 
			(4, '}' ),
			(3, '} // Copy' ),
			(3, '' ),
			(2, '} // While' ),
			(2, '' ),
			])

		output.extend( [
			(1, ""),
			(2, 'return result_valid_pieces;' ),
			(0, "}"),
			])

		return output

	
	# ----- Fix an piece in the valid_pieces
	def fixPiece( self, valid_pieces, piece_number, piece_space, piece_rotation):

		if valid_pieces == None:
			return None

		new_valid_pieces = [None] * self.puzzle.board_wh
		for space in range(self.puzzle.board_wh):
			new_valid_list = []

			for p in valid_pieces[ space ]:
				if space == piece_space:
					# on the space, we keep only that piece
					if p.p == piece_number and p.rotation == piece_rotation:
						new_valid_list.append(p)
				else:
					# everywhere else, we remove that piece
					if p.p != piece_number:
						new_valid_list.append(p)

			if len(new_valid_list) == 0:
				print("Fix Piece has reached a deadend on space", space)
				return None

			new_valid_pieces[space] = new_valid_list
	
		return new_valid_pieces



	# ----- 
	def getJobs( self, valid_pieces, pre_fixed=[], max_width=1024, max_height=1024):

		if valid_pieces == None:
			return None

		width = {}
		height = {}

		all_valid_pieces = {}
		current_valid_pieces = valid_pieces

		#for x in pre_fixed:
		#	current_valid_pieces = self.fixPiece( current_valid_pieces ....)

		#depth = len(self.puzzle.extra_fixed+self.puzzle.fixed+pre_fixed)
		#new_valid_

		depth = len(self.puzzle.extra_fixed+self.puzzle.fixed)

		all_valid_pieces[ depth-1 ] = [ (0, 0,  current_valid_pieces) ]
		width[ depth-1 ] = 1
		height[ depth-1 ] = 1

		while depth < self.puzzle.board_wh:

			orientation = depth % 2
			width[ depth ] = 0
			height[ depth ] = 0
			all_valid_pieces[ depth ] = []


			new_column_width = [1] * (width[depth-1])
			new_line_height  = [1] * (height[depth-1])

			tmp_valid_pieces = []

			for old_x, old_y, current_valid_pieces in all_valid_pieces[ depth-1 ]:
				
				#print("Depth", depth, "Old coordonates", old_x,",",old_y)

				lowest_valid_pieces = self.puzzle.board_wh*4
				best_space = None

				# Look for the space with the minimum possibilities
				for space in range(self.puzzle.board_wh):
					if  len(current_valid_pieces[ space ]) > 1:
						if  len(current_valid_pieces[ space ]) < lowest_valid_pieces:
							lowest_valid_pieces = len(current_valid_pieces[ space ])
							best_space = space

				if best_space == None:
					print("No best_space found, continuing")
					continue


				# Add the new jobs
				new_x = 0
				new_y = 0
				for  p in current_valid_pieces[ best_space ]:
					new_valid_pieces = self.filterValidPieces( self.fixPiece( current_valid_pieces, p.p, best_space, p.rotation) )
					if new_valid_pieces != None:
						tmp_valid_pieces.append( (old_x, new_x, old_y, new_y, new_valid_pieces) )

						if orientation == 0:
							new_x += 1
							if new_x > new_column_width[old_x]:
								new_column_width[old_x] = new_x
						else:
							new_y += 1
							if new_y > new_line_height[old_y]:
								new_line_height[old_y] = new_y

				
			# Adjust the coordinates of the jobs
			new_column_position = [0]
			for n in new_column_width:
				new_column_position.append( new_column_position[-1] + n )

			new_line_position = [0]
			for n in new_line_height:
				new_line_position.append( new_line_position[-1] + n )

			for old_x, new_x, old_y, new_y, valid_pieces in tmp_valid_pieces:
				actual_x = new_x+new_column_position[old_x]
				actual_y = new_y+new_line_position[old_y]

				#print("Depth", depth, "Coordonates", old_x,old_y, " -> ", actual_x, actual_y)

				all_valid_pieces[ depth ].append( (actual_x, actual_y, valid_pieces) )


			width[ depth ]  = new_column_position[-1]
			height[ depth ] = new_line_position[-1]

			print("Depth", depth, "Size of the jobs:", width[depth], "x", height[depth], "=>", len(all_valid_pieces[ depth ]))
			print()

			# Write the output
			output = ""
			for x, y, current_valid_pieces in all_valid_pieces[ depth ]:
				jobid = str(depth)+"_"+str(x)+"_"+str(y)
				extra_fixed=[]
				for space in range(self.puzzle.board_wh):
					if  (len(current_valid_pieces[ space ]) == 1) and (self.puzzle.static_spaces_type[ space ] != "fixed"): 
						piece = current_valid_pieces[ space ][0]
						extra_fixed.append( (piece.p, space, piece.rotation) )
				output += jobid+"|"+str(extra_fixed)+"\n"
			
			jobsfile = open( "jobs/"+self.getFileFriendlyName( self.puzzle.name )+"_"+str(depth)+"_"+str(pre_fixed)+".jobs.txt", "w" )
			jobsfile.write(output)
			jobsfile.close()

			if width[ depth ] > max_width and height[ depth ] > max_height:
					break
				
			depth += 1


		#print("Len of valid_pieces:", len(all_valid_pieces[-1]))

		return all_valid_pieces[-1]


	def getImages( self, pre_fixed=[] ):

		# Read the data
		for depth in range(-1, self.puzzle.board_wh):
			filename = "jobs/"+self.getFileFriendlyName( self.puzzle.name )+"_"+str(depth)+"_"+str(pre_fixed)+".jobs.txt"

			if os.path.exists(filename):
				coordinates=[]

				jobsfile = open( "jobs/"+self.getFileFriendlyName( self.puzzle.name )+"_"+str(depth)+"_"+str(pre_fixed)+".jobs.txt", "r" )
				max_x = 0
				max_y = 0
				for line in jobsfile:
					if line.startswith('#'):
						continue
					line = line.strip('\n').strip(' ')
					line = line.split("|")
					line = line[0].split("_")
					x=int(line[1])
					y=int(line[2])
					if x > max_x:
						max_x = x
					if y > max_y:
						max_y = y
					coordinates.append( (x, y) )
				jobsfile.close()


				# Create the blank image
				w = png.Writer(max_x+1, max_y+1, greyscale=True)
				img = []
				for h in range(max_y+1):
					l = [ 0 ] * (max_x+1)
					img.append(l)

				# Insert the jobs
				for x,y in coordinates:
					img[y][x] = 255

				# Write the image
				f = open("jobs/"+self.getFileFriendlyName( self.puzzle.name )+"_"+str(depth)+"_"+str(pre_fixed)+".png", 'wb')      # binary mode is important
				w.write(f, img)
				f.close()

	# ----- Generate Scoriste function
	def gen_main_function( self, only_signature=False):

		output = []

		output.extend( [ 
			(0, "int main("),
			] )

		if only_signature:
			output.append( (1, ');') )
			return output


		output.append( (1, ") {") )
		output.extend( [

			(1, '' ),
			#(1, 'if (signal(SIGINT,  sig_handler) == SIG_ERR) printf("\\nUnable to catch SIGINT\\n");' ),
			#(1, 'if (signal(SIGUSR1, sig_handler) == SIG_ERR) printf("\\nUnable to catch SIGUSR1\\n");' ),
			#(1, 'if (signal(SIGUSR2, sig_handler) == SIG_ERR) printf("\\nUnable to catch SIGUSR2\\n");' ),
			(1, '' ),
			#(1, 'return solve(NULL, NULL);'), 
			(1, 'printf("Starting\\n");'), 
			(1, 'print_valid_pieces( static_valid_pieces );'), 
			(1, 'print_valid_pieces( filterValidPieces( static_valid_pieces ) );'), 
			(1, 'return 0;'), 
			(1, '' ),
			(0, '}' ),
			] )
		
		return output

	
	# ----- generate LibGen Header
	def GenerateH( self ):

		gen = open( self.getNameH(temp=True), "w" )

		self.writeGen( gen, self.getHeaderH() )

		
		output = []

		output.extend( [
			(0, "#include <sys/stat.h>" ),
			(0, "" ),
			] )

		self.writeGen( gen, self.getDefinitions(only_signature=True) )


		self.writeGen( gen, output )
		

		self.writeGen( gen, self.gen_getter_setter_function( only_signature=True ) )
		self.writeGen( gen, self.gen_sig_handler_function(only_signature=True) )
		self.writeGen( gen, self.gen_FilterValidPieces_function(only_signature=True) )
		self.writeGen( gen, self.gen_print_valid_pieces_functions(only_signature=True) )
		"""
		self.writeGen( gen, self.gen_allocate_blackwood_function( only_signature=True ) )
		self.writeGen( gen, self.gen_free_blackwood_function( only_signature=True ) )
		self.writeGen( gen, self.gen_set_blackwood_arrays_function( only_signature=True ) )
		self.writeGen( gen, self.gen_save_best_depth_seen_function( only_signature=True ) )
		self.writeGen( gen, self.gen_getSolutionURL_function( only_signature=True ) )
		self.writeGen( gen, self.gen_getBestDepthSeenHeartbeat_function( only_signature=True ) )

		self.writeGen( gen, self.gen_print_url_functions(only_signature=True) )

		
		self.writeGen( gen, self.gen_do_commands(only_signature=True) )
		self.writeGen( gen, self.gen_print_functions(only_signature=True) )
		self.writeGen( gen, self.gen_filter_function( only_signature=True ) )
		self.writeGen( gen, self.gen_solve_function(only_signature=True) )
		"""

		self.writeGen( gen, self.getFooterH() )


	# ----- generate LibGen
	def GenerateC( self, module=None ):

		gen = open( self.getNameC(temp=True, module=module), "w" )
		self.writeGen( gen, self.getHeaderC( module=module ) )

		if module != None:
			macro_name = module
		else:
			macro_name = ""

		if macro_name == "utils":

			self.writeGen( gen, self.getDefinitions() )
		
			output = []
			output.extend( [
				(0, ""),
				] )
			self.writeGen( gen, output )

			self.writeGen( gen, self.gen_getter_setter_function( only_signature=False ) )
			self.writeGen( gen, self.gen_sig_handler_function(only_signature=False) )
			self.writeGen( gen, self.gen_FilterValidPieces_function(only_signature=False) )
			self.writeGen( gen, self.gen_print_valid_pieces_functions(only_signature=False) )
			"""
			self.writeGen( gen, self.gen_allocate_blackwood_function( only_signature=False ) )
			self.writeGen( gen, self.gen_free_blackwood_function( only_signature=False ) )
			self.writeGen( gen, self.gen_set_blackwood_arrays_function( only_signature=False ) )
			self.writeGen( gen, self.gen_save_best_depth_seen_function( only_signature=False) )
			self.writeGen( gen, self.gen_getSolutionURL_function( only_signature=False ) )
			self.writeGen( gen, self.gen_getBestDepthSeenHeartbeat_function( only_signature=False ) )
			self.writeGen( gen, self.gen_print_url_functions(only_signature=False) )
			self.writeGen( gen, self.gen_print_functions(only_signature=False) )
			self.writeGen( gen, self.gen_do_commands(only_signature=False ) )
			"""


		elif macro_name == "generate":
			"""
			self.writeGen( gen, self.gen_filter_function( only_signature=False ) )
			self.writeGen( gen, self.gen_solve_function(only_signature=False) )
			"""


		elif macro_name == "main":

			self.writeGen( gen, self.gen_main_function(only_signature=False) )


		self.writeGen( gen, self.getFooterC( module=module ) )

	# ----- Self test
	def SelfTest( self ):

		sys.stdout.flush()
		
		# Start the chrono
		self.top("selftest")

		"""
		# Start the input thread
		myInput = thread_input.Input_Thread( self.command_handler, self, 0.1 )
		myInput.start()

		# Start the solution thread
		myWFN = thread_wfn.Wait_For_Notification_Thread( self, self.puzzle )
		myWFN.start()

		# Start the locking thread
		myLCA = thread_lca.Leave_CPU_Alone_Thread( self, period=2, desktop=self.DESKTOP )
		#myLCA.start()

		# Start the periodic thread
		myHB = thread_hb.HeartBeat_Thread( self, period=1 )
		myHB.start()
		"""

		signal.signal(signal.SIGINT, self.LibExt.sig_handler)
		signal.signal(signal.SIGUSR1, self.LibExt.sig_handler)
		signal.signal(signal.SIGUSR2, self.LibExt.sig_handler)

		"""
		#thread_output_filename = ctypes.c_char_p("/tmp/test".encode('utf-8'))
		thread_output_filename = None

		cb = self.cb
		cf = self.cb
		self.copy_new_arrays_to_cb()
		"""
		"""
		l = self.gen_solve_function( only_signature=True )
		args = []
		loc = locals()
		for pname in self.getParametersNamesFromSignature(l):
			args.append( loc[ pname ] )
		self.LibExtWrapper( self.getFunctionNameFromSignature(l), args, timeit=True )
		"""
		
		l = self.gen_main_function( only_signature=True )
		args = []
		loc = locals()
		for pname in self.getParametersNamesFromSignature(l):
			args.append( loc[ pname ] )
		self.LibExtWrapper( self.getFunctionNameFromSignature(l), args, timeit=True )
		

		"""

		myLCA.stop_lca_thread = True	
		myWFN.stop_wfn_thread = True	
		myHB.stop_hb_thread = True	
		myInput.stop_input_thread = True	
		"""

		top = self.top("selftest", unit=False)
		if not self.QUIET:
			print()
			print( "Self-Test execution time: ", top )

		return False


if __name__ == "__main__":
	import data

	p = data.loadPuzzle()
	#p = data.loadPuzzle(extra_fixed=[[0,0,3],[2,9,0]])
	if p != None:

		lib = LibBigPicture( p )
		while lib.SelfTest():
			pass


# Lapin
