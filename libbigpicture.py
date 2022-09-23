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

import thread_bp_hb
#import thread_lca
#import thread_wfn
import thread_bp_input


class LibBigPicture( external_libs.External_Libs ):
	"""Defines exploration"""

	MACROS_NAMES_A = [ "utils", "generate", "main" ]
	MACROS_NAMES_B = [ ]

	COMMANDS = {}
	COMMANDS_LIST = [
				'CLEAR_SCREEN',
				'SHOW_TITLE',
				'SHOW_HEARTBEAT',
				'SHOW_STATS',
				'SHOW_HELP',

				'LEAVE_CPU_ALONE',
				'TIME_TO_FINISH',
			]

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

	STATS =	[
			("StatsAllocate", "stats_allocate", "allocation", "STATS_ALLOCATE"),
			("StatsCopy", "stats_copy", "copies", "STATS_COPY"),
			("StatsFilterValidPieces", "stats_filter_valid_pieces", "filter valid_pieces", "STATS_FILTER_VALID_PIECES"),
			("StatsFixPieces", "stats_fix_pieces", "fix piece", "STATS_FIX_PIECES"),

			("StatsFilterValidPiecesRemoved", "stats_filter_valid_pieces_removed", "removed", "STATS_FILTER_VALID_PIECES_REMOVED"),
			("StatsFilterValidPiecesDeadEnd", "stats_filter_valid_pieces_dead_end", "dead ends", "STATS_FILTER_VALID_PIECES_DEAD_END"),
			("StatsFixPiecesDeadEnd", "stats_fix_pieces_dead_end", "dead ends", "STATS_FIX_PIECES_DEAD_END"),
		]

	ARRAYS = STATS + [
			("NodesHeartbeat", "nodes_heartbeat", "heartbeats", "NODES_HEARTBEAT"),
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
		
		# Add to the commands the arrays
		for (fname, vname, uname, flag)  in self.ARRAYS:
			self.COMMANDS_LIST.append( "SHOW_"+flag )
			self.COMMANDS_LIST.append( "ZERO_"+flag )
			self.COMMANDS_LIST.append( "ZERO_TOTAL_"+flag )
			self.COMMANDS_LIST.append( "SHOW_RESULT_"+flag )


		self.COMMANDS[ "NONE" ] = 0
		i = 0
		for c in self.COMMANDS_LIST:
			self.COMMANDS[ c ] = 1<<i
			i += 1


		# Params for External_Libs
		#self.EXTRA_NAME = extra_name
		self.GCC_EXTRA_PARAMS = ""
		self.dependencies = [ "defs", "arrays", "validpieces" ]
		self.modules_names = self.MACROS_NAMES_A + self.MACROS_NAMES_B
		self.modules_optimize = [ "generate" ]

		external_libs.External_Libs.__init__( self, skipcompile )

		# Access to the globally defined structure
		self.LibExt.global_bigpicture = self.LibExt.allocate_bigpicture()
		self.global_bigpicture = self.LibExt.global_bigpicture


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
		signatures.extend( self.gen_getter_setter_function( only_signature=True ) )
		signatures.extend( self.gen_do_commands(only_signature=True ) )
		signatures.extend( self.gen_allocate_bigpicture_function( only_signature=True ) )
		signatures.extend( self.gen_free_bigpicture_function( only_signature=True ) )
		signatures.extend( self.gen_get_static_valid_pieces_function( only_signature=True ) )
		#signatures.extend( self.gen_getSolutionURL_function( only_signature=True ) )
		#signatures.extend( self.gen_getBestDepthSeenHeartbeat_function( only_signature=True ) )
		#signatures.extend( self.gen_solve_function(only_signature=True) )
		#signatures.extend( self.gen_set_blackwood_arrays_function(only_signature=True ) )
		#signatures.extend( self.gen_print_valid_pieces_functions(only_signature=True) )
		
		self.defineFunctionsArgtypesRestype( signatures )


	# ----- generate definitions
	def getDefinitions( self, only_signature=False ):
		output = []

		# Bigpicture
		if only_signature:
			output.append( (0, '// Command flags' ), )
			for (n,v) in self.COMMANDS.items():
				output.append( (0, '#define '+str(n)+' '+str(v) ), )
			output.append( (0 , "") )

			output.extend( [
				( 0, "// Job" ),
				( 0, "struct st_job {" ),
				( 2, 	"uint64 x;" ),
				( 2, 	"uint64 y;" ),
				( 2, 	"uint64 shift_x;" ),
				( 2, 	"uint64 shift_y;" ),
				( 2, 	"t_piece_full * valid_pieces;" ),
				( 0, "};" ),
				( 0, "typedef struct st_job t_job;" ),
				( 0, "typedef t_job * p_job;" ),
			] )

			output.extend( [
				( 0, "// Piece fixed" ),
				( 0, "struct st_piece_fixed {" ),
				( 2, 	"uint64 number;" ),
				( 2, 	"uint64 space;" ),
				( 2, 	"uint64 rotation;" ),
				( 0, "};" ),
				( 0, "typedef struct st_piece_fixed t_piece_fixed;" ),
				( 0, "typedef t_piece_fixed * p_piece_fixed;" ),
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
				( 0, "typedef t_patterns_seen * p_patterns_seens;" ),
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

			for (fname, vname, uname, flag)  in self.STATS:
				output.extend( [
				(1, "// Statistics "+uname ),
				(1, "uint64 "+vname+";"),
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
			(1, 'if (signo == SIGUSR1) { incHB(global_bigpicture); setCheckCommands(global_bigpicture, 1); }'),
			(1, 'if (signo == SIGUSR2) { togglePause(global_bigpicture); setCheckCommands(global_bigpicture, 1); }'),
			(0, "}"),
			])

		return output

	# ----- Handles commands given on STDIN
	def command_handler( self, commands ):
		if self.DEBUG > 2:
			print( "Commands received: ]", commands, "[" )
			print( "global_bigpicture:", self.global_bigpicture )
			for (c, n, s) in self.FLAGS:
				f = getattr( self.LibExt, "get"+s )
				print( "get"+s+" "+str(f( self.global_bigpicture ))+" | "+c )

		command_found = False

		for command in commands:
			if command in [ "c", "cls", "clear_screen" ]:
				self.LibExt.xorCommands( self.global_bigpicture, self.COMMANDS[ 'CLEAR_SCREEN' ] )
				command_found = True
			elif command in [ "", "print", "cc", "check_commands" ]:
				self.LibExt.setCheckCommands( self.global_bigpicture, 1 )
				command_found = True
			elif command in [ "n", "next" ]:
				self.LibExt.setHB( self.global_bigpicture, 10000000 )
				command_found = True
			elif command in [ "0", "000" ]:
				self.LibExt.clearHB( self.global_bigpicture )
				command_found = True
			elif command in [ "hb", "heartbeat" ]:
				lca   = self.LibExt.getLCA( self.global_bigpicture )
				pause = self.LibExt.getPause( self.global_bigpicture )
				if (lca == 0) or (pause == 0):
					self.LibExt.incHB( self.global_bigpicture )
				command_found = True
			elif command in [ "s", "stats" ]:
				self.LibExt.xorCommands( self.global_bigpicture, self.COMMANDS[ 'SHOW_STATS' ] )
				command_found = True
			elif command in [ "p", "pause", "lca" ]:
				self.LibExt.togglePause( self.global_bigpicture, 1 )
				command_found = True
			elif command in [ "w", "sfn" ]:
				self.LibExt.setSFN( self.global_bigpicture, 1 )
				command_found = True
			elif command in [ "q", "quit", "exit" ]:
				if self.DEBUG > 0:
					print('x-]'+self.XTermInfo+'  TTF  '+self.XTermNormal+'[-x')
				self.LibExt.setTTF( self.global_bigpicture, 1 )
				command_found = True

			elif command in [ "h", "help", "?" ]:
				self.LibExt.xorCommands( self.global_bigpicture, self.COMMANDS[ 'SHOW_HELP' ] )
				command_found = True

			if not command_found:
				for (fname, vname, uname, flag)  in self.ARRAYS:
					if command in  [ "SHOW_"+flag, "ZERO_"+flag, "ZERO_TOTAL_"+flag, "ZERO_END_"+flag ]:
						self.LibExt.xorCommands( self.global_bigpicture, self.COMMANDS[ command ] )
						command_found = True

		if command_found:
			self.LibExt.setCheckCommands( self.global_bigpicture, 1 )


	# ----- Generate command functions
	def gen_do_commands( self, only_signature=False ):

		output = []

		for prefix in [ "", "s", "f" ]:

			if prefix == "":
				out = ""
			elif prefix == "s":
				out = "s_out,"
			elif prefix == "f":
				out = "f_out,"

			output.extend( [ 
				(0, "void "+prefix+"do_commands("),
				(1, "charp s_out,"  if (prefix == "s") else "" ),
				(1, "FILE  * f_out," if (prefix == "f") else "" ),
				(1, "p_bigpicture b"),
				] )

			if only_signature:
				output.extend( [ (1, ');'), ])
				continue
			
			output.extend( [
				(1, ") {"),
				(1, '' ),
				(1, 'uint64 i, s;' ),
				(1, '' ),

				# GENERAL COMMANDS
				(1, 'if (b->commands & CLEAR_SCREEN)' ),
				(2, prefix+'printf( '+out+' "'+self.XTermClearScr+'" );' ),
				(0, '' ),

				(1, 'if (b->commands & SHOW_TITLE)' ),
				(2, prefix+'printf( '+out+' "\\n' + self.H1_OPEN + self.puzzle.TITLE_STR + self.H1_CLOSE + '\\n\\n" );' ),
				(0, '' ),

				(1, 'if (b->commands & SHOW_HEARTBEAT)' ),
				(2, prefix+'printf( '+out+' "Heartbeats: %llu/%llu\\n", b->heartbeat, b->heartbeat_limit);' ),
				(0, '' ),

				(1, 'if (b->commands & SHOW_STATS) {' ),
				] )

			for (fname, vname, uname, flag)  in self.STATS:
				output.append( (2, prefix+'printf( '+out+' "'+uname+': %llu\\n", b->'+vname+');' ), )

			output.extend( [
				(2, prefix+'printf( '+out+' "\\n");' ),
				(1, '}' ),
				] )




			for (fname, vname, uname, flag)  in self.STATS:
				vtname = vname.replace("stats_", "stats_total_")

				output.extend( [
				(1, 'if (b->commands & SHOW_'+flag+') {' ),
				#(2, prefix+'print'+fname+'( '+out+' b );'  if self.puzzle.scenario.STATS else ""),
				#(2, 'printf( "Total '+vname+' = %llu\\n", b->'+vtname+' );' if self.puzzle.scenario.PERF else ""),
				(1, '}' ),
				(0, '' ),

				(1, 'if ((b->commands & SHOW_RESULT_'+flag+')&&(b->time_to_finish)) {' ),
				#(2, prefix+'print'+fname+'_for_stats_by_depth( '+out+' b );'  if self.puzzle.scenario.STATS else ""),
				#(2, 'printf( "'+vname+' = %llu  (avg = %llu)\\n", b->'+vtname+', b->'+vtname+' / b->heartbeat );' if self.puzzle.scenario.PERF else ""),
				(1, '}' ),
				(0, '' ),

				#(1, 'if (b->commands & ZERO_'+flag+')' ),
				##(2, 'for(i=0;i<WH;i++) { b->'+vtname+' += b->'+vname+'[i]; b->'+vname+'[i] = 0; }' ),
				#(2, 'for(i=0;i<WH;i++) { b->'+vname+'[i] = 0; }' if self.puzzle.scenario.STATS else ""),
				#(0, '' ),

				#(1, 'if (b->commands & ZERO_TOTAL_'+flag+')' ),
				#(2, 'b->'+vtname+' = 0;' if self.puzzle.scenario.PERF else ""),
				#(0, '' ),
				] )



			output.extend( [
				# HELP
				(1, 'if (b->commands & SHOW_HELP) {' ),
				(2, prefix+'printf( '+out+' "\\n");'),
				(2, prefix+'printf( '+out+' "'+self.H1_OPEN+"List of commands"+self.H1_CLOSE+'\\n");'),
				(2, prefix+'printf( '+out+' " > 0  | reset heartbeat\\n");'),
				(2, prefix+'printf( '+out+' " > hb | one heartbeat\\n");'),
				(2, prefix+'printf( '+out+' " > c  | cls\\n");'),
				(2, prefix+'printf( '+out+' " > w  | send notification\\n");'),
				(2, prefix+'printf( '+out+' " > n  | next\\n");'),
				(2, prefix+'printf( '+out+' " > p  | pause\\n");'),
				(2, prefix+'printf( '+out+' " > n  | next\\n");'),
				(2, prefix+'printf( '+out+' " > s  | save\\n");'),
				(2, prefix+'printf( '+out+' " > q  | quit\\n");'),

				(2, (prefix+'printf( '+out+' "\\n Stats:\\n'+ "".join([
					"  > "+format("SHOW_"+flag, "45")+
					"  > "+format("ZERO_"+flag, "45")+
					"  > "+format("ZERO_TOTAL_"+flag, "45")+"\\n" 
					for (fname, vname, uname, flag) in self.ARRAYS])+'\\n");') if self.puzzle.scenario.STATS or self.puzzle.scenario.PERF else ""),
				#(2, 'b->commands &= ~SHOW_HELP;' ),
				(1, '}' ),
				(0, '' ),
				(0, '' ),


				] )

			output.extend( [
				(0, '}' ),
				(0, '' ),
				] )
	
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

	# ----- Allocate bigpicture memory
	def gen_allocate_bigpicture_function( self, only_signature=False ):

		output = [ 
			(0, "p_bigpicture allocate_bigpicture("),
			]

		if only_signature:
			output.append( (1, ');') )
			return output

		output.append( (1, ") {") )
		output.append( (1, "p_bigpicture b;") )
		output.append( (1, "uint64 i;") )
		output.append( (0, "") )
		#output.append( (1, 'DEBUG3_PRINT(("Allocate Blackwood\\n" ));'), )
		output.append( (1, 'b = (p_bigpicture)calloc(1, sizeof(t_bigpicture));') )

		for (c, n, s) in self.FLAGS:
			output.append( (1, "b->"+n+" = 0;") )

		output.extend( [
			(1, 'return b;'), 
			(0, '}' ),
			] )
			
		return output

	# ----- Free bigpicture memory
	def gen_free_bigpicture_function( self, only_signature=False ):

		output = [ 
			(0, "p_bigpicture free_bigpicture("),
			(1, "p_bigpicture b"),
			]

		if only_signature:
			output.append( (1, ');') )
			return output

		output.append( (1, ") {") )
		output.append( (1, 'free(b);') )
		output.append( (1, 'return NULL;') )
		output.append( (0, '}') )
		return output

	# ----- Get Static Valid Pieces
	def gen_get_static_valid_pieces_function( self, only_signature=False ):

		output = [ 
			(0, "p_piece_full get_static_valid_pieces("),
			]

		if only_signature:
			output.append( (1, ');') )
			return output

		output.append( (1, ") {") )
		output.append( (1, 'return static_valid_pieces;') )
		output.append( (0, '}') )
		return output

	# ----- Generate print functions
	def gen_PrintValidPieces_functions( self, only_signature=False ):

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
					(0, "void "+prefix+"PrintValidPieces"+dest+"("),
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
					(1, 'if (valid_pieces == NULL) {' ),
					(2, 'printf("NULL: Nothing to print\\n");' ),
					(1, 'return;' ),
					(1, '}' ),
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

	# ----- Allocate
	def gen_AllocateValidPieces_function( self, only_signature=False ):
		
		output = [ 
			(0, "t_piece_full * AllocateValidPieces("),
			(1, "p_bigpicture bigpicture"),
			]

		if only_signature:
			output.extend( [ (1, ');'), ])
			return output

		output.extend( [
			(1, ") {"),
			(1, ""),
			(1, "bigpicture->stats_allocate++;"),
			(1, 'return (t_piece_full *)(malloc(sizeof(t_piece_full)*WH*WH*4));' ),
			(1, ""),
			(0, "}"),
			])

		return output

	# ----- Copy
	def gen_CopyValidPieces_function( self, only_signature=False ):
		
		output = [ 
			(0, "t_piece_full * CopyValidPieces("),
			(1, "p_bigpicture bigpicture,"),
			(1, "t_piece_full * src_valid_pieces,"),
			(1, "t_piece_full * dst_valid_pieces"),
			]

		if only_signature:
			output.extend( [ (1, ');'), ])
			return output

		output.extend( [
			(1, ") {"),
			(1, ""),
			(1, "uint64 space;"),
			(1, "uint64 piece_index;"),
			(1, ""),
			(1, 'if (src_valid_pieces == NULL) ' ),
			(2, 'return NULL;' ),
			(1, 'if (dst_valid_pieces == NULL) ' ),
			(2, 'return NULL;' ),
			(1, ""),
			(1, "bigpicture->stats_copy++;"),
			(1, ""),
			(1, 'for (space=0; space<WH; space++) {' ),
			(2, 'piece_index = space*WH*4;' ),
			(2, 'while (src_valid_pieces[piece_index].u != 0xff) {' ),
			(3, 'dst_valid_pieces[piece_index] = src_valid_pieces[piece_index];' ), 
			(3, 'piece_index++;' ),
			(2, '}' ),
			(1, ""),
			(2, '// Copy 0xff marker at the end of the list' ),
			(2, 'dst_valid_pieces[piece_index] = src_valid_pieces[piece_index];' ), 
			(1, '}' ),
			(1, 'return dst_valid_pieces;' ),
			(1, ""),
			(0, "}"),
			])

		return output


	# ----- Filter based on edges/patterns the valid_pieces list
	def gen_FilterValidPieces_function( self, only_signature=False ):
		
		output = []
		for variant in [ "", "Overwrite"]:
			output.extend( [
				(0, "p_piece_full FilterValidPieces"+variant+"("),
				(1, "p_bigpicture bigpicture,"),
				(1, "p_piece_full valid_pieces"),
				#(1, "uint64 allocate"),
				] )

			if only_signature:
				output.extend( [ (1, ');'), ])
				continue

			output.extend( [
				(1, ") {"),
				(1, ""),
				(1, "uint64 removed;"),
				(1, "uint64 space;"),
				(1, "uint64 piece_index, dst_piece_index;"),
				(1, "t_piece_full piece;"),
				(1, "t_patterns_seen patterns_seen[WH];"),
				(1, "t_patterns_seen local_patterns;"),
				(1, "t_piece_full * current_valid_pieces;" ),
				(1, "t_piece_full * result_valid_pieces;" ),
				(1, "t_piece_full tmp_valid_pieces[WH*WH*4];" if variant in [ "", "Overwrite" ] else "" ),
				])

			output.extend( [
				(1, 'if (valid_pieces == NULL) return NULL;' ),
				(1, '' ),
				(1, "bigpicture->stats_filter_valid_pieces++;"),
				])

			output.extend( [
				(1, 'current_valid_pieces = valid_pieces;' ),
				(1, 'result_valid_pieces = AllocateValidPieces(bigpicture);' if variant == "" else ""),
				(1, 'result_valid_pieces = tmp_valid_pieces;' if variant == "Overwrite" else ""),
				(1, 'removed = 0xff;' ),
				(1, 'while (removed != 0) {' ),
				(2, '' ),
				(2, 'removed = 0;' ),
				(2, '' ),
				(2, 'for (space=0; space<WH; space++) {' ),
				(3, 'patterns_seen[space].u=0;' ),
				(3, 'patterns_seen[space].r=0;' ),
				(3, 'patterns_seen[space].d=0;' ),
				(3, 'patterns_seen[space].l=0;' ),
				(3, 'piece_index = space*WH*4;' ),
				(3, 'while (current_valid_pieces[piece_index].u != 0xff) {' ),
				(4, 'patterns_seen[space].u |= 1 << current_valid_pieces[piece_index].u;' ),
				(4, 'patterns_seen[space].r |= 1 << current_valid_pieces[piece_index].r;' ),
				(4, 'patterns_seen[space].d |= 1 << current_valid_pieces[piece_index].d;' ),
				(4, 'patterns_seen[space].l |= 1 << current_valid_pieces[piece_index].l;' ),
				(4, 'piece_index++;' ),
				(3, '}' ),
				(2, '}' ),
				(2, '' ),
				(2, 'for (space=0; space<WH; space++) {' ),
				(3, '' ),
				(3, 'local_patterns.u = 1<<0;' ),
				(3, 'local_patterns.r = 1<<0;' ),
				(3, 'local_patterns.d = 1<<0;' ),
				(3, 'local_patterns.l = 1<<0;' ),
				(3, '' ),
				(3, 'if (space >= W)           { local_patterns.u = patterns_seen[space-W].d; }'), 
				(3, 'if ((space % W) != (W-1)) { local_patterns.r = patterns_seen[space+1].l; }'), 
				(3, 'if (space < (WH-W))       { local_patterns.d = patterns_seen[space+W].u; }'), 
				(3, 'if ((space % W) != 0    ) { local_patterns.l = patterns_seen[space-1].r; }'), 
				(3, '' ),
				(3, 'piece_index = space*WH*4;' ),
				(3, 'dst_piece_index = space*WH*4;' ),
				(3, 'while (current_valid_pieces[piece_index].u != 0xff) {' ),
				(4, '' ),
				(4, 'if ( (local_patterns.u & (1 << current_valid_pieces[piece_index].u)) &&' ),
				(4, '     (local_patterns.r & (1 << current_valid_pieces[piece_index].r)) &&' ),
				(4, '     (local_patterns.d & (1 << current_valid_pieces[piece_index].d)) &&' ),
				(4, '     (local_patterns.l & (1 << current_valid_pieces[piece_index].l)) ) {' ),
				(5, 'result_valid_pieces[dst_piece_index] = current_valid_pieces[piece_index];' ), 
				(5, 'dst_piece_index++;' ),
				(4, '} else {' ),
				(5, 'removed++;' ),
				(4, '}' ),
				(4, '' ),
				(4, 'piece_index++;' ),
				(3, '} // while' ),
				(3, '' ),
				(3, '// If nothing is copied, it is a deadend' ),
				(3, 'if (dst_piece_index == space*WH*4) {' ),
				#(4, 'printf("Filter Pieces deadend on space %lld\\n", space);' ),
				(4, "bigpicture->stats_filter_valid_pieces_dead_end ++;"),
				(4, 'free(result_valid_pieces);' if variant == "" else "" ),
				(4, 'return NULL;' ),
				(3, '}' ),
				(3, '' ),
				(3, '// Copy 0xff marker at the end of the list' ),
				(3, 'result_valid_pieces[dst_piece_index] = current_valid_pieces[piece_index];' ), 
				(3, '' ),
				(2, '} // For space' ),
				(2, '' ),
				(2, '// If we need to go again, we copy into tmp_valid_pieces to use it as the new source' ),
				(2, 'if (removed > 0) {' ),
				(3, 'current_valid_pieces = tmp_valid_pieces;' if variant == "" else "" ),
				(3, 'CopyValidPieces(bigpicture, result_valid_pieces, tmp_valid_pieces);' if variant == "" else "" ),
				(3, 'CopyValidPieces(bigpicture, result_valid_pieces, valid_pieces);' if variant == "Overwrite" else "" ),
				(2, '}' ),
				(2, '' ),
				(2, "bigpicture->stats_filter_valid_pieces_removed++;"),
				(1, '} // While removed' ),
				(1, '' ),
				])

			output.extend( [
				(1, 'CopyValidPieces(bigpicture, result_valid_pieces, valid_pieces);' if variant == "Overwrite" else "" ),
				(1, ""),
				(1, 'return result_valid_pieces;' if variant == "" else "" ),
				(1, 'return valid_pieces;' if variant == "Overwrite" else "" ),
				(0, "}"),
				])

		return output

	# ----- Fix one Piece
	def gen_FixPieces_function( self, only_signature=False ):
	
		output = []
		for variant in [ "", "Overwrite"]:
			output.extend( [
				(0, "t_piece_full * FixPieces"+variant+"("),
				(1, "p_bigpicture bigpicture,"),
				(1, "p_piece_full valid_pieces,"),
				(1, "uint64 piece_number,"),
				(1, "uint64 piece_space,"),
				(1, "uint64 piece_rotation"),
				] )

			if only_signature:
				output.extend( [ (1, ');'), ])
				continue
			else:

				output.extend( [
					(1, ") {"),
					(1, "uint64 space;"),
					(1, "uint64 piece_index, dst_piece_index;"),
					(1, "" ),
					(1, "t_piece_full tmp_valid_pieces[WH*WH*4];" if variant == "Overwrite" else "" ),
					(1, "t_piece_full * result_valid_pieces;" ),
					(1, ""),
					(1, 'if (valid_pieces == NULL) ' ),
					(2, 'return NULL;' ),
					(1, '' ),
					(1, "bigpicture->stats_fix_pieces ++;"),
					(1, '' ),
					(1, "result_valid_pieces = AllocateValidPieces(bigpicture);" if variant == "" else ""),
					(1, "result_valid_pieces = tmp_valid_pieces;" if variant == "Overwrite" else ""),
					(1, 'for (space=0; space<WH; space++) {' ),
					(1, '' ),
					(2, 'piece_index = space*WH*4;' ),
					(2, 'dst_piece_index = space*WH*4;' ),
					(2, 'while (valid_pieces[piece_index].u != 0xff) {' ),
					(3, 'if (space == piece_space) {' ),
					(4, 'if ((valid_pieces[piece_index].number == piece_number)&&(valid_pieces[piece_index].rotation == piece_rotation)) {' ),
					(5, 'result_valid_pieces[dst_piece_index] = valid_pieces[piece_index];' ), 
					(5, 'dst_piece_index++;' ), 
					(4, '}' ),
					(3, '} else {' ),
					(4, 'if (valid_pieces[piece_index].number != piece_number) {' ),
					(5, 'result_valid_pieces[dst_piece_index] = valid_pieces[piece_index];' ), 
					(5, 'dst_piece_index++;' ), 
					(4, '}' ),
					(3, '}' ),
					(3, 'piece_index++;' ),
					(2, '}' ),
					(2, 'if (dst_piece_index == space*WH*4) {' ),
					#(3, 'printf("Fix Piece has reached a deadend on space %lld\\n", space);' ),
					(3, "bigpicture->stats_fix_pieces_dead_end ++;"),
					(3, 'free(result_valid_pieces);' if variant == "" else "" ),
					(3, 'return NULL;' ),
					(2, '}' ),
					(2, '// Copy 0xff marker at the end of the list' ),
					(2, 'result_valid_pieces[dst_piece_index] = valid_pieces[piece_index];' ), 
					(1, '} // For space' ),
					(1, '' ),
					])

				output.extend( [
					(1, 'CopyValidPieces(bigpicture, result_valid_pieces, valid_pieces);' if variant == "Overwrite" else "" ),
					(1, 'result_valid_pieces = valid_pieces;' if variant == "Overwrite" else "" ),
					(1, ""),
					(1, 'return result_valid_pieces;' ),
					(0, "}"),
					])

		return output
	
	# ----- get the jobs
	def gen_getJobs_function( self, only_signature=False ):
		
		output = [ 
			(0, "p_job getJobs("),
			(1, "p_bigpicture bigpicture,"),
			(1, "p_piece_full valid_pieces,"),
			(1, "p_piece_fixed pre_fixed,"),
			(1, "uint64 max_width,"),
			(1, "uint64 max_height"),
			]

		if only_signature:
			output.extend( [ (1, ');'), ])
			return output

		output.extend( [
			(1, ") {"),
			(1, ""),
			(2, "t_piece_full * current_valid_pieces;" ),
			(2, "t_piece_full * new_valid_pieces;" ),
			(2, "uint64 i;"),
			(2, "uint64 depth;"),
			(2, "uint64 orientation;"),
			(2, "uint64 space;"),
			(2, "uint64 piece_index;"),
			(2, "uint64 new_column_width[16384];"),
			(2, "uint64 new_line_height[16384];"),
			(2, "uint64 new_column_position[16384];"),
			(2, "uint64 new_line_position[16384];"),
			(2, "uint64 width[WH+1];"),
			(2, "uint64 height[WH+1];"),
			(2, "t_job * all_jobs[WH+1];"),
			(2, "t_job first_job[2];"),
			(2, "uint64 jobs_index;"),
			(2, "uint64 previous_jobs_index;"),
			(2, "uint64 lowest_valid_pieces;"),
			(2, "uint64 best_space;"),
			(2, "uint64 len_valid_pieces;"),
			(2, "uint64 shift_x;"),
			(2, "uint64 shift_y;"),
			(1, ""),
			(1, 'FILE * output;' ),
			(1, 'uint8 was_allocated;' ),
			(1, 'uint8 TTF;' ),
			(1, ""),
			(1, 'was_allocated = 0;' ),
			(1, 'if (bigpicture == NULL) {' ),
			(2, 'bigpicture = (p_bigpicture)allocate_bigpicture();'), 
			(2, 'was_allocated = 1;' ),
			#(2, 'xorCommands(bigpicture, SHOW_STATS);' ),
			(1, '}'), 
 			#(2, "bigpicture->commands |= CLEAR_SCREEN;"),
 			(2, "bigpicture->commands |= SHOW_STATS;"),
			(1, ""),
			(1, 'TTF=0;' ),
			(1, '' ),
			(2, ""),
			(1, '// Output' ),
			(1, 'output = stdout;' ),
			#(1, 'if (thread_output_filename != NULL) {' ),
			#(2, 'output = fopen( thread_output_filename, "a" );' ),
			#(2, 'if (!output) { printf("Can\'t open %s\\n", thread_output_filename); return -1; }' ),
			#(1, '}' ),
			(1, ""),
			(1, ""),
			(2, 'if (valid_pieces == NULL) ' ),
			#(3, 'return NULL;' ),
			(3, 'valid_pieces = static_valid_pieces;' ),
			(1, ""),
			(1, ""),
			(2, "// Depth goes from -1 to WH, so we adjust with +1"),
			(2, "depth = "+str(len(self.puzzle.extra_fixed+self.puzzle.fixed))+";"), #TODO
			(2, "depth += 1;"),
			(2, '' ),
			(2, '// Starting point' ),
			(2, "first_job[0].x = 0;"),
			(2, "first_job[0].y = 0;"),
			(2, "first_job[0].valid_pieces = valid_pieces;"),
			(2, "first_job[1].x = 0xffffffff; // Marks the end of the list"),
			(2, "all_jobs[depth-1] = first_job;"),
			(2, "width[depth-1] = 1;"),
			(2, "height[depth-1] = 1;"),
			(2, ""),
			(2, ""),
			(2, "while ((depth < WH+1)&&!TTF) {"),
			(2, ""),
			(3, "orientation = depth % 2;"),
			(3, "width[depth] = 0;"),
			(3, "height[depth] = 0;"),
			(3, "all_jobs[depth] = (t_job *)(malloc(sizeof(t_job)*16384*16384));"),
			(3, "jobs_index = 0;"),
			(3, "for(i=0; i<16384; i++){"),
			(4, "new_column_width[i] = 1;"),
			(4, "new_line_height[i] = 1;"),
			(3, "}"),
			(3, ""),
			(3, "previous_jobs_index = 0;"),
			(3, "while ((all_jobs[depth-1][previous_jobs_index].x != 0xffffffff)&&!TTF) {"),
			(4, ""),
			(4, "if (bigpicture != NULL) {"),
			(5, 'if (bigpicture->check_commands) {'),
			(6, 'bigpicture->check_commands = 0;'),
			(6, 'fdo_commands(output, bigpicture);' ),
			(6, 'TTF = getTTF(bigpicture);' ),
			(5, "}"),
			(4, "}"),
			(4, ""),
			(4, "current_valid_pieces = all_jobs[depth-1][previous_jobs_index].valid_pieces;"),
			(4, "lowest_valid_pieces = WH*4;"),
			(4, "best_space = WH*4;"),
			(4, ""),
			(4, 'for (space=0; space<WH; space++) {' ),
			(5, 'piece_index = space*WH*4;' ),
			(5, 'while ((all_jobs[depth-1][previous_jobs_index].valid_pieces[piece_index].u != 0xff)&&!TTF) {' ),
			(6, "piece_index ++;"),
			(5, "}"),
			(5, 'len_valid_pieces = piece_index - space*WH*4;' ),
			(5, "if (len_valid_pieces > 1) {"),
			(6, "if (len_valid_pieces < lowest_valid_pieces) {"),
			(7, "lowest_valid_pieces = len_valid_pieces;"),
			(7, "best_space = space;"),
			(6, "}"),
			(5, "}"),
			(4, "}"),
			(4, "if (best_space == WH*4) {"),
			(5, 'printf("No best_space found, continuing\\n");'),
			(5, "continue; // While all_jobs"),
			(4, "}"),
			(4, ""),
			(4, "shift_x = 0;"),
			(4, "shift_y = 0;"),
			(4, 'piece_index = best_space*WH*4;' ),
			(4, 'while ((current_valid_pieces[piece_index].u != 0xff)&&!TTF) {' ),
			(5, "new_valid_pieces = FilterValidPiecesOverwrite( bigpicture, FixPieces( bigpicture, current_valid_pieces, current_valid_pieces[piece_index].number, best_space, current_valid_pieces[piece_index].rotation));"),
			(5, "if (new_valid_pieces != NULL) {"),
			(6, "all_jobs[depth][jobs_index].x = all_jobs[depth-1][previous_jobs_index].x;"),
			(6, "all_jobs[depth][jobs_index].y = all_jobs[depth-1][previous_jobs_index].y;"),
			(6, "all_jobs[depth][jobs_index].shift_x = shift_x;"),
			(6, "all_jobs[depth][jobs_index].shift_y = shift_y;"),
			(6, "all_jobs[depth][jobs_index].valid_pieces = new_valid_pieces;"),
			(6, "if (orientation == 0) {"),
			(7, "shift_x++;"),
			(7, "if (shift_x > new_column_width[ all_jobs[depth-1][previous_jobs_index].x ])"),
			(8, "new_column_width[ all_jobs[depth-1][previous_jobs_index].x ] = shift_x;"),
			(6, "} else {"),
			(7, "shift_y++;"),
			(7, "if (shift_y > new_line_height[ all_jobs[depth-1][previous_jobs_index].y ])"),
			(8, "new_line_height[ all_jobs[depth-1][previous_jobs_index].y ] = shift_y;"),
			(6, "}"),
			(6, "jobs_index++;"),
			(5, "} // new_valid_pieces"),
			(5, "piece_index ++;"),
			(4, "}"),
			(4, ""),
			(4, "previous_jobs_index ++;"),
			(3, "} // While all_jobs"),
			(3, ""),
			(3, ""),
			(3, "all_jobs[depth][jobs_index].x = 0xffffffff; // Marks the end of the list"),
			(3, ""),
			(3, "if (!TTF) {"),
			(4, "// Adjust the coordinates"),
			(4, "new_column_position[0] = 0;"),
			(4, "for (i=0; i<width[depth-1]; i++)"),
			(5, "new_column_position[i+1] = new_column_position[i]+new_column_width[i];"),
			(4, "width[depth] = new_column_position[i];"),
			(4, ""),
			(4, "new_line_position[0] = 0;"),
			(4, "for (i=0; i<height[depth-1]; i++)"),
			(5, "new_line_position[i+1] = new_line_position[i]+new_line_height[i];"),
			(4, "height[depth] = new_line_position[i];"),
			(4, ""),
			(4, "jobs_index = 0;"),
			(4, "while (all_jobs[depth][jobs_index].x != 0xffffffff) {"),
			(5, "all_jobs[depth][jobs_index].x = all_jobs[depth][jobs_index].shift_x + new_column_position[all_jobs[depth][jobs_index].x];"),
			(5, "all_jobs[depth][jobs_index].y = all_jobs[depth][jobs_index].shift_y + new_line_position[all_jobs[depth][jobs_index].y];"),
			(5, "jobs_index ++;"),
			(4, "}"),
			(4, ""),
			(4, 'printf("Depth %lld : Size of the jobs: %lld x %lld => %lld\\n", depth, width[depth], height[depth], jobs_index);' ),
			(4, ""),
			(4, "// If we have reached our target"),
			(4, "if ((width[depth] > max_width) && (height[depth] > max_height)) break;"),
			(3, "}"),
			(3, ""),
			(3, "depth ++;"),
			(2, "} // While Depth"),

			(1, 'if (output != stdout) {' ),
			(2, 'fclose(output);' ),
			(1, '}' ),

			(1, 'if (was_allocated) {'), 
			(2, 'free_bigpicture(bigpicture);'), 
			(2, 'bigpicture = NULL;'), 
			(1, '}'), 

			(2, 'return NULL;' ),
			(1, ""),
			(0, "}"),
			])

		return output

	# ----- 
	def getJobsinPython( self, valid_pieces, pre_fixed=[], max_width=1024, max_height=1024):

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
			(1, 'if (signal(SIGINT,  sig_handler) == SIG_ERR) printf("\\nUnable to catch SIGINT\\n");' ),
			(1, 'if (signal(SIGUSR1, sig_handler) == SIG_ERR) printf("\\nUnable to catch SIGUSR1\\n");' ),
			(1, 'if (signal(SIGUSR2, sig_handler) == SIG_ERR) printf("\\nUnable to catch SIGUSR2\\n");' ),
			(1, '' ),
			#(1, 'return solve(NULL, NULL);'), 
			(1, 'printf("Starting\\n");'), 
			(1, 'PrintValidPieces( static_valid_pieces );'), 
			(1, 'getJobs( global_bigpicture, static_valid_pieces, NULL, 1024, 1024 );'), 
			#(1, 'PrintValidPieces( FilterValidPieces( static_valid_pieces ) );'), 
			#(1, 'PrintValidPieces( FixPieces(static_valid_pieces,0,0,3) );'), 
			#(1, 'PrintValidPieces( FilterValidPieces( FixPieces(static_valid_pieces,0,0,3) ) );'), 
			#(1, 'PrintValidPieces( FilterValidPieces( FixPieces(static_valid_pieces,2,15,0) ) );'), 
			#(1, 'PrintValidPieces( FilterValidPieces( FixPieces(FilterValidPieces( FixPieces(static_valid_pieces,0,0,3) ),2,15,0) ) );'), 
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
		self.writeGen( gen, self.gen_AllocateValidPieces_function(only_signature=True) )
		self.writeGen( gen, self.gen_CopyValidPieces_function(only_signature=True) )
		self.writeGen( gen, self.gen_FilterValidPieces_function(only_signature=True) )
		self.writeGen( gen, self.gen_FixPieces_function(only_signature=True) )
		self.writeGen( gen, self.gen_PrintValidPieces_functions(only_signature=True) )
		self.writeGen( gen, self.gen_getJobs_function(only_signature=True) )
		self.writeGen( gen, self.gen_do_commands(only_signature=True) )
		self.writeGen( gen, self.gen_allocate_bigpicture_function( only_signature=True ) )
		self.writeGen( gen, self.gen_free_bigpicture_function( only_signature=True ) )
		self.writeGen( gen, self.gen_get_static_valid_pieces_function( only_signature=True ) )
		"""
		self.writeGen( gen, self.gen_set_blackwood_arrays_function( only_signature=True ) )
		self.writeGen( gen, self.gen_save_best_depth_seen_function( only_signature=True ) )
		self.writeGen( gen, self.gen_getSolutionURL_function( only_signature=True ) )
		self.writeGen( gen, self.gen_getBestDepthSeenHeartbeat_function( only_signature=True ) )

		self.writeGen( gen, self.gen_print_url_functions(only_signature=True) )

		
		self.writeGen( gen, self.gen_print_functions(only_signature=True) )
		self.writeGen( gen, self.gen_Filter_function( only_signature=True ) )
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
			self.writeGen( gen, self.gen_do_commands(only_signature=False ) )
			self.writeGen( gen, self.gen_allocate_bigpicture_function( only_signature=False ) )
			self.writeGen( gen, self.gen_free_bigpicture_function( only_signature=False ) )
			self.writeGen( gen, self.gen_get_static_valid_pieces_function( only_signature=False ) )
			"""
			self.writeGen( gen, self.gen_set_blackwood_arrays_function( only_signature=False ) )
			self.writeGen( gen, self.gen_save_best_depth_seen_function( only_signature=False) )
			self.writeGen( gen, self.gen_getSolutionURL_function( only_signature=False ) )
			self.writeGen( gen, self.gen_getBestDepthSeenHeartbeat_function( only_signature=False ) )
			self.writeGen( gen, self.gen_print_url_functions(only_signature=False) )
			self.writeGen( gen, self.gen_print_functions(only_signature=False) )
			"""


		elif macro_name == "generate":
			self.writeGen( gen, self.gen_AllocateValidPieces_function(only_signature=False) )
			self.writeGen( gen, self.gen_CopyValidPieces_function(only_signature=False) )
			self.writeGen( gen, self.gen_FilterValidPieces_function(only_signature=False) )
			self.writeGen( gen, self.gen_FixPieces_function(only_signature=False) )
			self.writeGen( gen, self.gen_PrintValidPieces_functions(only_signature=False) )
			self.writeGen( gen, self.gen_getJobs_function(only_signature=False) )
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
		# Start the solution thread
		myWFN = thread_wfn.Wait_For_Notification_Thread( self, self.puzzle )
		myWFN.start()

		# Start the locking thread
		myLCA = thread_lca.Leave_CPU_Alone_Thread( self, period=2, desktop=self.DESKTOP )
		#myLCA.start()
		"""

		# Start the input thread
		myInput = thread_bp_input.BigPicture_Input_Thread( self.command_handler, self, 0.1 )
		myInput.start()

		# Start the periodic thread
		myHB = thread_bp_hb.BigPicture_HeartBeat_Thread( self, period=1 )
		myHB.start()

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

		# Parameters
		bigpicture = self.global_bigpicture
		valid_pieces = None #self.LibExt.get_static_valid_pieces()
		#valid_pieces = self.LibExt.get_static_valid_pieces()
		pre_fixed = None
		max_width = 1024
		max_height = 1024

		# Call
		l = self.gen_getJobs_function( only_signature=True )
		args = []
		loc = locals()
		for pname in self.getParametersNamesFromSignature(l):
			print(pname)
			args.append( loc[ pname ] )
		print(args)
		self.LibExtWrapper( self.getFunctionNameFromSignature(l), args, timeit=True )

		
		"""
		l = self.gen_main_function( only_signature=True )
		args = []
		loc = locals()
		for pname in self.getParametersNamesFromSignature(l):
			args.append( loc[ pname ] )
		self.LibExtWrapper( self.getFunctionNameFromSignature(l), args, timeit=True )
		"""


		"""

		myLCA.stop_lca_thread = True	
		myWFN.stop_wfn_thread = True	
		"""
		myHB.stop_hb_thread = True	
		myInput.stop_input_thread = True	

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
