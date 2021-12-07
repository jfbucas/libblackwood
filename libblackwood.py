# Global Libs
import os
import sys
import ctypes
import random
import multiprocessing
import itertools
import time
import math
import signal

# Local Libs
import thread_hb
import thread_lca
import thread_wfn
import thread_input
import external_libs


#
# Generates Joshua Blackwood algorithm, unrolled in C
# and a few other helper functions
#


if (sys.version_info[0] < 3) or (sys.version_info[1] < 6):
    raise Exception("Python 3.6 or a more recent version is required.")


class LibBlackwood( external_libs.External_Libs ):
	"""Blackwood generation library"""

	cb = None

	MACROS_NAMES_A = [ "utils", "generate", "main" ]
	MACROS_NAMES_B = [ ]

	DEPTH_COLORS = {}

	COMMANDS = { 
				'NONE':				0,
				'CLEAR_SCREEN':			1<<1,
				'SHOW_TITLE':			1<<2,
				'SHOW_HEARTBEAT':		1<<3,
				'SHOW_SEED':			1<<4,
				'SHOW_HELP':			1<<5,

				'SHOW_DEPTH_NODES_COUNT':	1<<8,
				'ZERO_DEPTH_NODES_COUNT':	1<<9,

				'SHOW_BEST_BOARD_URL':		1<<10,
				'SHOW_BEST_BOARD_URL_ONCE':	1<<11,

				'SHOW_MAX_DEPTH_SEEN':		1<<14,
				'SHOW_MAX_DEPTH_SEEN_ONCE':	1<<15,

				'SAVE_MAX_DEPTH_SEEN_ONCE':	1<<16,

				'LEAVE_CPU_ALONE':		1<<30,
				'TIME_TO_FINISH':		1<<31,

			}


	FLAGS = [
			[ "Time to finish",		"time_to_finish",		"TTF" ],
			[ "Leave CPU alone",		"leave_cpu_alone",		"LCA" ],
			[ "Pause",			"pause",			"Pause" ],
			[ "Wait for Notification",	"wait_for_notification",	"WFN" ],
			[ "Time Heartbeat",		"heartbeat",			"HB" ],
			[ "Max number of heartbeats",	"heartbeat_limit", 		"HBLimit" ],
			[ "Check for Commands",		"check_commands",		"CheckCommands" ],
			[ "Commands for Interactivity",	"commands",			"Commands" ],
			[ "Show help",			"help",				"Help" ],
			[ "Max Depth Seen",		"max_depth_seen",		"MaxDepthSeen" ],
		]

	def __init__( self, puzzle, extra_name="" ):

		self.name = "libblackwood"

		self.puzzle = puzzle
		
		self.xffff = format(len(self.puzzle.master_lists_of_rotated_pieces)-1, '6')

		#self.DEPTH_COLORS[0]= "" 
		for i in [249, 250, 251, 252]:
			self.DEPTH_COLORS[i] = self.rougeoie

		self.DEPTH_COLORS[253] = self.orangeoie 
		self.DEPTH_COLORS[254] = self.jaunoie 
		self.DEPTH_COLORS[255] = self.verdoie 
		self.DEPTH_COLORS[256] = self.bleuoie 


		# Params for External_Libs
		#self.EXTRA_NAME = extra_name
		self.GCC_EXTRA_PARAMS = ""
		self.dependencies = [ "defs", "arrays" ]
		self.modules_names = self.MACROS_NAMES_A + self.MACROS_NAMES_B

		external_libs.External_Libs.__init__( self )

		# Allocate memory for current_blackwood
		self.cb = self.LibExt.allocate_blackwood()


	# ----- Load the C library
	def load( self ):

		self.LibExt = ctypes.cdll.LoadLibrary( self.getNameSO() )

		signatures = []
		signatures.extend( self.gen_getter_setter_function( only_signature=True ) )
		signatures.extend( self.gen_allocate_blackwood_function( only_signature=True ) )
		signatures.extend( self.gen_getSolutionURL_function( only_signature=True ) )
		signatures.extend( self.gen_solve_function(only_signature=True) )
		signatures.extend( self.gen_do_commands(only_signature=True ) )
		signatures.extend( self.gen_set_blackwood_arrays_function(only_signature=True ) )
		
		self.defineFunctionsArgtypesRestype( signatures )


	# ----- Handles commands given on STDIN
	def command_handler( self, commands ):
		if self.DEBUG > 2:
			print( "Commands received: ]", commands, "[" )
			print( "cb:", self.cb )
			for (c, n, s) in self.FLAGS:
				f = getattr( self.LibExt, "get"+s )
				print( "get"+s+" "+str(f( self.cb ))+" | "+c )

		command_not_found = False

		for command in commands:
			if command in [ "c", "cls", "clear_screen" ]:
				self.LibExt.xorCommands( self.cb, self.COMMANDS[ 'CLEAR_SCREEN' ] )

			elif command in [ "d", "dnc", "show_depth_nodes_count" ]:
				self.LibExt.xorCommands( self.cb, self.COMMANDS[ 'SHOW_DEPTH_NODES_COUNT' ] )
			elif command in [ "z", "zero", "zero_depth_nodes_count" ]:
				self.LibExt.xorCommands( self.cb, self.COMMANDS[ 'ZERO_DEPTH_NODES_COUNT' ] )

			elif command in [ "b", "best", "show_best_board", "url" ]:
				self.LibExt.xorCommands( self.cb, self.COMMANDS[ 'SHOW_BEST_BOARD_URL_ONCE' ] )
			elif command in [ "m", "max", "show_max_depth_seen" ]:
				self.LibExt.xorCommands( self.cb, self.COMMANDS[ 'SHOW_MAX_DEPTH_SEEN_ONCE' ] )
			elif command in [ "s", "save", "save_max_depth_seen" ]:
				self.LibExt.xorCommands( self.cb, self.COMMANDS[ 'SAVE_MAX_DEPTH_SEEN_ONCE' ] )

			elif command in [ "", "print", "cc", "check_commands" ]:
				self.LibExt.setCheckCommands( self.cb, 1 )

			elif command in [ "n", "next" ]:
				self.LibExt.setHB( self.cb, 10000000 )

			elif command in [ "0", "000" ]:
				self.LibExt.clearHB( self.cb )

			elif command in [ "hb", "heartbeat" ]:
				lca   = self.LibExt.getLCA( self.cb )
				pause = self.LibExt.getPause( self.cb )
				if (lca == 0) or (pause == 0):
					self.LibExt.incHB( self.cb )

			elif command in [ "p", "pause", "lca" ]:
				self.LibExt.togglePause( self.cb, 1 )
			elif command in [ "w", "wfn" ]:
				self.LibExt.setWFN( self.cb, 1 )
			elif command in [ "q", "quit", "exit" ]:
				self.LibExt.setTTF( self.cb, 1 )

			elif command in [ "h", "help", "?" ]:
				self.LibExt.xorCommands( self.cb, self.COMMANDS[ 'SHOW_HELP' ] )
			else:
				command_not_found = True

		if not command_not_found:
			self.LibExt.setCheckCommands( self.cb, 1 )

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
				(1, "p_blackwood b"),
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
				(2, prefix+'printf( '+out+' "\\n' + self.H1_OPEN + self.TITLE_STR + self.H1_CLOSE + '\\n\\n" );' ),
				(0, '' ),

				(1, 'if (b->commands & SHOW_HEARTBEAT)' ),
				(2, prefix+'printf( '+out+' "Heartbeats: %llu/%llu\\n", b->heartbeat, b->heartbeat_limit );' ),
				(0, '' ),

				(1, 'if (b->commands & SHOW_SEED)' ),
				(2, prefix+'printf( '+out+' "Seed: %llu\\n\\n", b->seed );' ),
				(0, '' ),


				# SHOW/ZERO NODES_COUNT
				(1, 'if (b->commands & SHOW_DEPTH_NODES_COUNT)' ),
				(2, prefix+'printDepthNodeCount( '+out+' b );' ),
				(0, '' ),

				(1, 'if (b->commands & ZERO_DEPTH_NODES_COUNT)' ),
				(2, 'for(i=0;i<WH;i++) b->depth_nodes_count[i] = 0;' ),
				(0, '' ),


				# SHOW BEST_BOARD
				(1, 'if (b->commands & (SHOW_BEST_BOARD_URL | SHOW_BEST_BOARD_URL_ONCE) ) {' ),
				(2, 'if (b->max_depth_seen > 0)' ),
				(3, prefix+'printBoardURL( '+out+' b);' ),
				(2, 'b->commands &= ~SHOW_BEST_BOARD_URL_ONCE;' ),
				(1, '}' ),
				(0, '' ),


				# SHOW/SAVE MAX_DEPTH
				(1, 'if (b->commands & (SHOW_MAX_DEPTH_SEEN | SHOW_MAX_DEPTH_SEEN_ONCE) ) {' ),
				(2, "".join( [ 'if (b->max_depth_seen == '+str(k)+' ) '+prefix+'printf( '+out+' "Max Depth Seen = '+self.DEPTH_COLORS[k]+str(k)+self.XTermNormal+'\\n\\n'+'");' for k in self.DEPTH_COLORS] ) ),
				(2, 'b->commands &= ~SHOW_MAX_DEPTH_SEEN_ONCE;' ),
				(1, '}' ),
				(0, '' ),

				(1, 'if (b->commands & SAVE_MAX_DEPTH_SEEN_ONCE) {' ),
				(2, ''.join( [ 'if (b->max_depth_seen == '+str(k)+' ) save_max_depth_seen_'+str(k)+'(b);' for k in self.DEPTH_COLORS] ) ),
				(2, 'b->commands &= ~SAVE_MAX_DEPTH_SEEN_ONCE;' ),
				(1, '}' ),
				(0, '' ),

				# HELP
				(1, 'if (b->commands & SHOW_HELP) {' ),
				(2, prefix+'printf( '+out+' "\\n");'),
				(2, prefix+'printf( '+out+' "'+self.H1_OPEN+"List of commands"+self.H1_CLOSE+'\\n");'),
				(2, prefix+'printf( '+out+' " > 0  | reset heartbeat\\n");'),
				(2, prefix+'printf( '+out+' " > hb | one heartbeat\\n");'),
				(2, prefix+'printf( '+out+' " > c  | cls\\n");'),
				(2, prefix+'printf( '+out+' " > d  | nodes count\\n");'),
				(2, prefix+'printf( '+out+' " > z  | zero nodes count\\n");'),
				(2, prefix+'printf( '+out+' " > b  | show best board\\n");'),
				(2, prefix+'printf( '+out+' " > m  | show max depth\\n");'),
				(2, prefix+'printf( '+out+' " > s  | save best board\\n");'),
				(2, prefix+'printf( '+out+' " > n  | next\\n");'),
				(2, prefix+'printf( '+out+' " > p  | pause\\n");'),
				(2, prefix+'printf( '+out+' " > n  | next\\n");'),
				(2, prefix+'printf( '+out+' " > s  | save\\n");'),
				(2, prefix+'printf( '+out+' " > q  | quit\\n");'),
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



	# ----- generate definitions
	def getDefinitions( self, only_signature=False ):
		output = []

		if only_signature:
			output.append( (0, '// Command flags' ), )
			for (n,v) in self.COMMANDS.items():
				output.append( (0, '#define '+str(n)+' '+str(v) ), )
			output.append( (0 , "") )

		if only_signature:

			output.extend( [
				(0, "// Structure Blackwood"),
				(0, "struct st_blackwood {"),
				(0, "" ),
				] )

			output.append( (1 , "uint64 seed;") )
			
			for name,array in self.puzzle.master_index.items():
				output.append( (1 , "uint64 master_index_"+name+"[ "+str(len(array))+" ];") )

			output.append( (1 , "p_rotated_piece master_lists_of_rotated_pieces[ "+str(len(self.puzzle.master_lists_of_rotated_pieces))+" ];") )


			output.extend( [
				(0, "" ),
				(1, "// The Board" ),
				(1, "p_rotated_piece board[ WH ];"),
				(0, "" ),
				(1, "// Counters on each node" ),
				(1, "uint64 depth_nodes_count[ WH ];"),
				(0, "" ),
				(0, "" ),
				(1, "// ----- Flags -------" ),
				] )

			for (c, n, s) in self.FLAGS:
				output.extend( [
					(1, "// "+c+" -- "+s+" for short"),
					(1, "uint64	"+n+";"),
					(0, "" ),
					] )

			output.extend( [
				(0, ""),
				(0 , "};"),
				(0, ""),
				] )

			output.append( (0 , "") )
			output.append( (0 , "typedef struct st_blackwood   t_blackwood;") )
			output.append( (0 , "typedef t_blackwood *         p_blackwood;") )
			output.append( (0 , "") )
			output.append( (0 , "") )

			output.append( (0 , "// A global pointer") )
			output.append( (0 , "p_blackwood global_blackwood;") )
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
			(1, 'if (signo == SIGINT) { printf( "Ctrl-C received. Interrupting.\\n"); setCheckCommands(global_blackwood, 1); setTTF(global_blackwood, 1); }'),
			(1, 'if (signo == SIGUSR1) { incHB(global_blackwood); setCheckCommands(global_blackwood, 1); }'),
			(1, 'if (signo == SIGUSR2) { togglePause(global_blackwood); setCheckCommands(global_blackwood, 1); }'),
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
				output.append( (2, 'if (b) ((p_blackwood)b)->'+n+' = 0;'), ) 
				output.append( (2, 'else DEBUG_PRINT(("NULL on set'+s+'\\n" ));'), )
				output.append( (1, '}'), ) 

			# ---------------------------------------
			output.append( (0, "uint64 get"+s+"("), )
			output.append( (1, "voidp b"), )
			if only_signature:
				output.append( (1, ');') )
			else:
				output.append( (1, ') {'), ) 
				output.append( (2, 'if (b) return ((p_blackwood)b)->'+n+';'), ) 
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
				output.append( (2, 'if (b) ((p_blackwood)b)->'+n+' = v;'), ) 
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
				output.append( (2, 'if (b) ((p_blackwood)b)->'+n+' |= v;'), ) 
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
				output.append( (2, 'if (b) ((p_blackwood)b)->'+n+' ^= v;'), ) 
				output.append( (2, 'else DEBUG_PRINT(("NULL on xor'+s+'\\n" ));'), )
				output.append( (1, '}'), ) 
			
			# ---------------------------------------
			output.append( (0, "void inc"+s+"("), )
			output.append( (1, "voidp b"), )
			if only_signature:
				output.append( (1, ');') )
			else:
				output.append( (1, ') {'), ) 
				output.append( (2, 'if (b) ((p_blackwood)b)->'+n+' ++;'), ) 
				output.append( (2, 'else DEBUG_PRINT(("NULL on inc'+s+'\\n" ));'), )
				output.append( (1, '}'), ) 
			
			# ---------------------------------------
			output.append( (0, "void dec"+s+"("), )
			output.append( (1, "voidp b"), )
			if only_signature:
				output.append( (1, ');') )
			else:
				output.append( (1, ') {'), ) 
				output.append( (2, 'if (b) ((p_blackwood)b)->'+n+' --;'), ) 
				output.append( (2, 'else DEBUG_PRINT(("NULL on dec'+s+'\\n" ));'), )
				output.append( (1, '}'), ) 
			
			# ---------------------------------------
			output.append( (0, "void toggle"+s+"("), )
			output.append( (1, "voidp b"), )
			if only_signature:
				output.append( (1, ');') )
			else:
				output.append( (1, ') {'), ) 
				output.append( (2, 'if (b) ((p_blackwood)b)->'+n+' = ~((p_blackwood)b)->'+n+';'), ) 
				output.append( (2, 'else DEBUG_PRINT(("NULL on toggle'+s+'\\n" ));'), )
				output.append( (1, '}'), ) 
			
		return output

	# ----- Generate the solution into a string for WFN
	def gen_getSolutionURL_function( self, only_signature=False ):

		output = [ 
			(0, "void getSolutionURL("),
			(1, "p_blackwood b,"),
			(1, "charp url"),
			]

		if only_signature:
			output.extend( [ (1, ');'), ])
			return output

		output.extend( [
			(1, ") {"),
			(1, "// If we have a solution we return the url string"),
			(2, 'sprintBoardURL(url, b);' ),
			(0, "}"),
			])

		return output

	# ----- Allocate blackwood memory
	def gen_allocate_blackwood_function( self, only_signature=False ):

		output = [ 
			(0, "p_blackwood allocate_blackwood("),
			]

		if only_signature:
			output.append( (1, ');') )
			return output

		output.append( (1, ") {") )
		output.append( (1, "p_blackwood b;") )
		output.append( (1, "uint64 i;") )
		output.append( (0, "") )
		#output.append( (1, 'DEBUG3_PRINT(("Allocate Blackwood\\n" ));'), )
		output.append( (1, 'b = (p_blackwood)calloc(1, sizeof(t_blackwood));') )

		output.append( (1 , "b->seed = seed;") )

		for name,array in self.puzzle.master_index.items():
			output.append( (1 , "for(i=0; i<"+str(len(array))+"; i++) b->master_index_"+name+"[i] = master_index_"+name+"[i];") )

		output.append( (1 , "for(i=0; i<"+str(len(self.puzzle.master_lists_of_rotated_pieces))+"; i++) b->master_lists_of_rotated_pieces[i] = master_lists_of_rotated_pieces[i];") )

		for (c, n, s) in self.FLAGS:
			output.append( (1, "b->"+n+" = 0;") )

		output.extend( [
			(1, 'return b;'), 
			(0, '}' ),
			] )
			
		return output

	# ----- Free blackwood memory
	def gen_free_blackwood_function( self, only_signature=False ):

		output = [ 
			(0, "p_blackwood free_blackwood("),
			(1, "p_blackwood b"),
			]

		if only_signature:
			output.append( (1, ');') )
			return output

		output.append( (1, ") {") )
		output.append( (1, 'free(b);') )
		output.append( (1, 'return NULL;') )
		output.append( (0, '}') )
		return output


	# ----- Define arrays in p_blackwood structure
	def gen_set_blackwood_arrays_function( self, only_signature=False ):

		output = []
		
		# Set seed
		output.extend( [ 
			(0, "void set_blackwood_seed("),
			(1, "p_blackwood cb,"),
			(1, "uint64 seed") 
			] )

		if only_signature:
			output.append( (1, ');') )
		else:
			output.append( (1, ") {") )
			output.append( (1, "if (cb)") )
			output.append( (2, "cb->seed = seed;") )
			output.append( (1, "else") )
			output.append( (2, 'DEBUG_PRINT(("set_blackwood_seed NULL pointer\\n"));') )
			output.append( (0, "}") )


		# Set master_indexes
		for name,array in self.puzzle.master_index.items():
			output.extend( [ 
				(0, "void set_blackwood_master_index_"+name+"("),
				(1, "p_blackwood cb,"),
				(1, "uint64p array")
				] )

			if only_signature:
				output.append( (1, ');') )
			else:
				output.append( (1, ") {") )
				output.append( (1, "uint64 i;") )
				output.append( (1, "if (cb)") )
				output.append( (2, "for(i=0; i<"+str(len(array))+"; i++) cb->master_index_"+name+"[i] = array[i];") )
				output.append( (1, "else") )
				output.append( (2, 'DEBUG_PRINT(("set_blackwood_master_index_'+name+' NULL pointer\\n"));') )
				output.append( (0, "}") )


		# Set master_indexes
		output.extend( [ 
			(0, "void set_blackwood_master_lists_of_rotated_pieces("),
			(1, "p_blackwood cb,"),
			(1, "uint64p array")
			] )

		if only_signature:
			output.append( (1, ');') )
		else:
			output.append( (1, ") {") )
			output.append( (1, "uint64 i;") )
			output.append( (1, "if (cb) {") )
			output.append( (2, "for(i=0; i<"+str(len(self.puzzle.master_lists_of_rotated_pieces))+"; i++) {") )
			output.append( (3, "cb->master_lists_of_rotated_pieces[i] = NULL;") )
			output.append( (3, "if (array[i] != "+self.xffff+")") )
			output.append( (4, "cb->master_lists_of_rotated_pieces[i] = &(master_all_rotated_pieces[array[i]]);") )
			output.append( (3, "}") )
			output.append( (1, "} else") )
			output.append( (2, 'DEBUG_PRINT(("set_blackwood_master_index_'+name+' NULL pointer\\n"));') )
			output.append( (0, "}") )

		return output

	# ----- Copy to p_blackwood struct
	def copy_new_arrays_to_cb( self ):

		cb = self.cb
	
		# Get a new random order of pieces lists
		seed = random.randint(0, sys.maxsize)
		if os.environ.get('SEED') != None:
			seed = int(os.environ.get('SEED'))
			if self.DEBUG > 0:
				self.info(" * Env Seed for Prepare Pieces : "+str(seed) )
		( master_index, master_lists_of_rotated_pieces, master_all_rotated_pieces ) = self.puzzle.prepare_pieces(local_seed=seed)

		# Set Seed
		self.LibExt.set_blackwood_seed( cb, seed )

		# Set master_indexes
		for name,master_array in master_index.items():
			array = multiprocessing.RawArray(ctypes.c_uint64, len(master_array))
			for i in range(len(master_array)):
				if (master_array[ i ] != None):
					array[i] = master_array[ i ]
				else:
					array[i] = len(self.puzzle.master_lists_of_rotated_pieces)-1

			f = getattr( self.LibExt, "set_blackwood_master_index_"+name )
			f( cb, array )


		# Set master_lists_of_rotated_pieces
		array = multiprocessing.RawArray(ctypes.c_uint64, len(master_lists_of_rotated_pieces))
		for i in range(len(master_lists_of_rotated_pieces)):
			if  (master_lists_of_rotated_pieces[ i ] != None):
				array[i] = master_lists_of_rotated_pieces[ i ]
			else:
				array[i] = len(self.puzzle.master_lists_of_rotated_pieces)-1
		
		self.LibExt.set_blackwood_master_lists_of_rotated_pieces(cb, array)


	# ----- Save best results
	def gen_save_max_depth_seen_function( self, only_signature=False ):

		output = [] 
		for k in self.DEPTH_COLORS.keys():
			output.extend( [ 
				(0, "void save_max_depth_seen_"+str(k)+"("),
				(1, "p_blackwood b"),
				] )

			if only_signature:
				output.append( (1, ');') )
				continue

			output.append( (1, ") {") )
			output.extend( [
				(1, 'FILE * output;' ),
				(0, '' ),
				(1, 'mkdir("results/", 0755);' ),
				(1, 'output = fopen( "results/'+str(k)+'", "a" );' ),
				(1, "fprintBoardURL(output, b);"),
				(1, 'fclose(output);' ),
				(0, '}' ),
				] )
				
		return output



	# ----- Generate Args for Printf
	def getURLPrintfArgs( self ):
		pf_str = ""
		pf_args = ""

		pf_str += "https://e2.bucas.name/"
		pf_str += "#puzzle="+self.puzzle.getFileFriendlyName(self.puzzle.name)
		pf_str += "&board_w="+str(self.puzzle.board_w)
		pf_str += "&board_h="+str(self.puzzle.board_h)

		pf_str += "&board_pieces="
		for s in range(self.puzzle.board_wh):
			pf_str += "%03d"
			pf_args += "url_pieces["+str(s)+"],"

		pf_str += "&board_edges="
		for s in range(self.puzzle.board_wh*4):
			pf_str += "%c"
			pf_args += "patterns["+str(s)+"],"

		
		pf_str += "&seed=%llu"
		pf_args += "b->seed,"

		pf_str += "&motifs_order=jef"

		pf_args = pf_args.rstrip(',')
		return (pf_str, pf_args)

	# ----- Generate URL {,s,f}printf functions
	def gen_print_url_functions( self, only_signature=False ):

		output = []

		for prefix in [ "", "s", "f" ]:
			output.extend([ 
				(0, "void "+prefix+"printBoardURL("),
				(1, "charp url,"  if (prefix == "s") else "" ),
				(1, "FILE   * f," if (prefix == "f") else "" ),
				(1, "p_blackwood b"),
				])

			if only_signature:
				output.extend( [ (1, ');'), ])
				continue
			
			( pf_str, pf_args ) = self.getURLPrintfArgs()

			output.extend( [
				(1, ") {"),
				(1, 'uint64 i, d, piece, space;'), 
				(1, 'uint8 patterns[ WH * 4 ];'), 
				(1, 'uint8 l, u, temp;'), 
				(1, 'uint8 url_pieces[ WH ];'), 
				(1, "p_rotated_piece * board;"),
				])

			output.extend( [
				(1, "board = b->board;"),
				(0, ""),
				(0, ""),
				(1, "for(i=0; i<WH*4; i++) patterns[i] = 0;"),
				])

			output.extend( [
				(1, "for(d=0; d<WH; d++) {"),
				(2, "space = spaces_sequence[d];"),
				(2, "url_pieces[ space ] = 0;"),
				(2, "if (board[ space ] != NULL) {"),

				(3, "// Insert the piece"),
				(3, "url_pieces[ space ] = board[ space ]->p;"),
				(3, "patterns[ space*4 + 0 ] = pieces[board[ space ]->p].u; // Up"),
				(3, "patterns[ space*4 + 1 ] = pieces[board[ space ]->p].r; // Right"),
				(3, "patterns[ space*4 + 2 ] = pieces[board[ space ]->p].d; // Down"),
				(3, "patterns[ space*4 + 3 ] = pieces[board[ space ]->p].l; // Left"),

				(3, "// Rotate the piece to match the right and down"),
				(3, "i = 0;"),
				(3, "l = 0;"),
				(3, "u = 0;"),
				(3, "if (space % W != 0) l = board[ space-1 ]->r;"),
				(3, "if (space     >= W) u = board[ space-W ]->d;"),
				(3, "while ("),
				(3, "   (((int)(patterns[ space*4 + 0 ] == u) +"),
				(3, "     (int)(patterns[ space*4 + 1 ] == board[ space ]->r) +"),
				(3, "     (int)(patterns[ space*4 + 2 ] == board[ space ]->d) +"),
				(3, "     (int)(patterns[ space*4 + 3 ] == l)) < 3) "),
				(3, "       && (i < 8)) {"),
				(4, "temp = patterns[ space*4 + 0 ];"),
				(4, "patterns[ space*4 + 0 ] = patterns[ space*4 + 3 ];"),
				(4, "patterns[ space*4 + 3 ] = patterns[ space*4 + 2 ];"),
				(4, "patterns[ space*4 + 2 ] = patterns[ space*4 + 1 ];"),
				(4, "patterns[ space*4 + 1 ] = temp;"),
				(4, "i++;"),
				(3, "}"),
				(2, "}"),
				(1, "}"),
				(0, ""),
				(1, "for(i=0; i<WH*4; i++) patterns[i] += \'a\';"),
				])

			output.extend( [
				(1, prefix+'printf('), 
				(2, "url," if prefix == "s" else ""), 
				(2, "f," if prefix == "f" else ""), 
				(2, '"'+pf_str+('\\n' if prefix != "s" else "")+'",'), 
				(2, pf_args), 
				(2, ');'), 
				(1, 'fflush(stdout);' if prefix == "" else ""), 
				(0, "}"),
				])

		return output


	# ----- Generate print functions
	def gen_print_functions( self, only_signature=False ):

		output = []

		for (prefix, (fname, vname, uname))  in itertools.product([ "", "s", "f" ], [ ("DepthNodeCount", "depth_nodes_count", "nodes/s") ]):

			if prefix == "":
				out = ""
			elif prefix == "s":
				out = "s_out,"
			elif prefix == "f":
				out = "f_out,"

			# ----------------------------------
			for dest in [ "", "_for_stats" ]:

				output.extend( [ 
					(0, "void "+prefix+"print"+fname+dest+"("),
					(1, "charp s_out,"  if (prefix == "s") else "" ),
					(1, "FILE   * f_out," if (prefix == "f") else "" ),
					(1, "p_blackwood b"),
					] )

				if only_signature:
					output.extend( [ (1, ');'), ])
					continue
					
				output.extend( [
					(1, ") {"),
					(1, "uint64 x, y, count, total;"),
					(0, ''), 
					(1, 'total = 0;' ),
					(0, ''), 
					] )

				if dest == "":
					output.extend( [
						(1, 'for (y = 0; y < '+str(self.puzzle.board_h)+'; y++) {' ),
						(2, 'for (x = 0; x < '+str(self.puzzle.board_w)+'; x++) {' ),
						(3, 'count = b->'+vname+'[ x+(y*'+str(self.puzzle.board_w)+') ];' ),
						(3, 'total += count;' ),
						(3, 'if (count == 0) {' ),
						(4, prefix+'printf( '+out+'"  . " );' ),
						(3, '} else if (count < 1000) {' ),
						(4, prefix+'printf( '+out+'"'+self.verdoie +"%3llu"+self.XTermNormal+' ", count/1);' ),
						(3, '} else if (count < 1000000) {' ),
						(4, prefix+'printf( '+out+'"'+self.jaunoie +"%3llu"+self.XTermNormal+' ", count/1000);' ),
						(3, '} else if (count < 1000000000) {' ),
						(4, prefix+'printf( '+out+'"'+self.rougeoie+"%3llu"+self.XTermNormal+' ", count/1000000);' ),
						(3, '} else if (count < 1000000000000) {' ),
						(4, prefix+'printf( '+out+'"'+self.violoie +"%3llu"+self.XTermNormal+' ", count/1000000000);' ),
						(3, '} else if (count < 1000000000000000) {' ),
						(4, prefix+'printf( '+out+'"'+self.bleuoie +"%3llu"+self.XTermNormal+' ", count/1000000000000);' ),
						(3, '} else {' ),
						(4, prefix+'printf( '+out+'"%3llu ", count);' ),
						(3, '}' ),
						(2, '} // x' ),
						(2, prefix+'printf( '+out+'"\\n" );' ),
						(1, '} // y' ),
						(1, prefix+'printf( '+out+'"\\n" );' ),
						(1, prefix+'printf( '+out+'"Total: %llu '+uname+'\\n\\n", total );' ),
						])
				else:
					output.extend( [
						(1, 'for (y = 0; y < '+str(self.puzzle.board_h)+'; y++) {' ),
						(2, 'for (x = 0; x < '+str(self.puzzle.board_w)+'; x++) {' ),
						(3, 'count = b->'+vname+'[ x+(y*'+str(self.puzzle.board_w)+') ];' ),
						(3, 'total += count;' ),
						(3, prefix+'printf( '+out+'"%llu ", count);' ),
						(2, '} // x' ),
						(1, '} // y' ),
						(1, prefix+'printf( '+out+'"\\n" );' ),
						(1, prefix+'printf( '+out+'"Total: %llu '+uname+'\\n", total );' ),
						])


				output.extend( [
					(1, 'fflush(stdout);' if prefix == "" else ""), 
					(0, '}' ),
					(0, ''), 
					] )


		return output








	# ----- Generate Scoriste function
	def gen_solve_function( self, only_signature=False):

		output = []

		output.extend( [ 
			(0, "int solve("),
			(1, "charp thread_output_filename,"),
			(1, "p_blackwood cb"),
			] )

		if only_signature:
			output.append( (1, ');') )
			return output

		W=self.puzzle.board_w
		H=self.puzzle.board_h
		WH=self.puzzle.board_wh

		output.append( (1, ") {") )
		output.extend( [
			(1, 'uint64 i, turn, previous_score;' ),
			(1, 'FILE * output;' ),

			(1, 'uint8 was_allocated;' ),
			(1, 'uint8 pieces_used[WH];' ),
			(1, 'uint8 cumulative_heuristic_side_count[WH];' ),
			(1, 'uint8 cumulative_heuristic_conflicts_count[WH];' ),
			(1, 'uint16 piece_index_to_try_next[WH];' ),
			(1, 'uint64 depth_nodes_count[WH];' ),
			(1, 'uint64 piece_candidates;' ),
			(1, 'uint8 conflicts_allowed_this_turn;' ),
			(1, 't_rotated_piece * current_rotated_piece;' ),
			(1, 't_rotated_piece * board['+str(WH)+'];' ),
			(1, '' ),
			
			(1, 'was_allocated = 0;' ),
			(1, 'if (cb == NULL) {' ),
			#(2, 'DEBUG_PRINT(("Allocating Memory\\n"));'), 
			(2, 'cb = (p_blackwood)allocate_blackwood();'), 
			(2, 'was_allocated = 1;' ),
			(1, '}'), 
			(1, 'global_blackwood = cb;'), 

			(1, '' ),

			#(1, '// Seeding'), 
			#(1, 'srand(time(NULL)+getpid());'), 
			] )

		output.append( (1, "// Clear blackwood structure") )
		for (c, n, s) in self.FLAGS:
			output.append( (1, "cb->"+n+" = 0;") )

		output.extend( [
			(1, "cb->max_depth_seen = 0;"),
			(1, "cb->heartbeat_limit = heartbeat_time_bonus[ 0 ];"),
			(1, "cb->commands = CLEAR_SCREEN | SHOW_TITLE | SHOW_SEED | SHOW_HEARTBEAT | SHOW_DEPTH_NODES_COUNT | SHOW_MAX_DEPTH_SEEN | SHOW_BEST_BOARD_URL | ZERO_DEPTH_NODES_COUNT;" if self.DEBUG > 0 else ""),
			#(1, "cb->commands = 0;" if self.DEBUG > 0 else ""),
			#(1, "cb->commands = SHOW_MAX_DEPTH_SEEN | ZERO_DEPTH_NODES_COUNT;" if self.DEBUG > 1 else ""),
			(1, "cb->commands = SHOW_HEARTBEAT;" if self.DEBUG == 0 else ""),
			(1, 'for(i=0;i<WH;i++) cb->board[i] = NULL;' ),
			(1, 'for(i=0;i<WH;i++) cb->depth_nodes_count[i] = 0;' ),
			(2, ""),

			(1, '// Output' ),
			(1, 'output = stdout;' ),
			(1, 'if (thread_output_filename != NULL) {' ),
			(2, 'output = fopen( thread_output_filename, "a" );' ),
			(2, 'if (!output) { printf("Can\'t open %s\\n", thread_output_filename); return -1; }' ),
			(1, '}' ),
			(1, '' ),
			(1, '// Local variables' ),
			(1, 'for(i=0;i<WH;i++){' ),
			(2, 'pieces_used[i] = 0;' ),
			(2, 'cumulative_heuristic_side_count[i] = 0;' ),
			(2, 'cumulative_heuristic_conflicts_count[i] = 0;' ),
			(2, 'piece_index_to_try_next[i] = '+self.xffff+';' ),
			(2, 'depth_nodes_count[i] = 0;' ),
			(2, 'board[i] = NULL;' ),
			(1, '}' ),
			(1, '' ),
			(1, 'DEBUG_PRINT(("x-]'+self.XTermInfo+'  Starting Solve  '+self.XTermNormal+'[-x\\n"));' ),
			(1, '' ),
			])

		#for (c, n, s) in self.FLAGS:
		#	output.append( (1, 'DEBUG_PRINT(("'+c+': %llu\\n", cb->'+n+'));') )

		master_lists_of_rotated_pieces = "master_lists_of_rotated_pieces"

		# this goes from 0....255; we have solved #0 already, so start at #1.
		for depth in range(0,WH+1):
			d=str(depth)

			output.extend( [
				(1, "// ==--==--==--==--[ Reaching depth "+d+" ]--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--== "),
				(1, '' ),
				(1, 'depth'+d+":  // Labels are ugly, don't do this at home" ),
				] )

			if self.DEBUG > 0 and depth >= 64:
				output.append( (2, 'if (cb->max_depth_seen < '+d+') {') )
				output.append( (3, 'cb->max_depth_seen = '+d+';') )
				output.append( (3, 'for(i=0;i<WH;i++) cb->board[i] = board[i];') )
				output.append( (2, '}' ))

			if depth >= 249: #252:
			#if depth >= 252:
				output.append( (2, 'if (cb->max_depth_seen < '+d+') {' if depth <256 else '') )
				output.append( (3, 'setWFN(cb, 1);' ) )
				output.append( (3, 'cb->max_depth_seen = '+d+';') )
				output.append( (3, 'cb->commands |= SAVE_MAX_DEPTH_SEEN_ONCE;' ) )
				output.append( (3, 'cb->commands |= SHOW_MAX_DEPTH_SEEN_ONCE;' ) )
				output.append( (3, 'cb->commands |= SHOW_BEST_BOARD_URL_ONCE;' if depth>=254 else '' ) )
				output.append( (3, 'cb->heartbeat_limit += heartbeat_time_bonus[ '+d+' ];') )
				output.append( (3, 'for(i=0;i<WH;i++) cb->board[i] = board[i];') )
				output.append( (3, 'fdo_commands(output, cb);' ) )
				output.append( (2, '}' if depth<256 else '') )
			if depth == WH:
				output.append( (2, '// We have a complete puzzle !!' ) )
				output.append( (2, 'setWFN(cb, 1);' ) )
				output.append( (2, 'sleep(600); // Wait for the WFN thread' ) )
				output.append( (0, '' ) )
				# followed immediately by depth_end
				break


			if depth > 0:
				previous_space = self.puzzle.scenario.spaces_sequence[ depth-1 ]
				sprevious_space = str(previous_space)

			space = self.puzzle.scenario.spaces_sequence[ depth ]
			sspace = str(space)

			output.append( (2, 'cb->depth_nodes_count['+sspace+'] ++;' if self.DEBUG > 0 else "") )

			output.append( (2, '' ) )
			if depth in ([ 140 ] if self.DEBUG == 0 else range(0, WH, W*2)):
				output.append( (2, 'if (cb->check_commands) {') )
				#output.append( (3, 'DEBUG_PRINT(("'+" "*depth+' Space '+sspace+' - checking commands : %llx \\n", cb->commands ))'  if self.DEBUG > 1 else "" ))
				output.append( (3, 'clearCheckCommands(cb);' ), )
				output.append( (0, '' ) )
				output.append( (3, 'if (getTTF(cb)) goto depth_end;' ) )
				output.append( (0, '' ) )
				output.append( (3, 'if (cb->heartbeat > cb->heartbeat_limit) goto depth_timelimit;' ) )
				output.append( (0, '' ) )
				output.append( (3, 'fdo_commands(output, cb);' ), )
				output.append( (0, '' ) )
				output.append( (3, 'if (getLCA(cb) || getPause(cb))' ) )
				output.append( (4, 'while ((getLCA(cb) || getPause(cb)) && !getTTF(cb)) {' ) )
				output.append( (5, 'fdo_commands(output, cb);' ), )
				output.append( (5, 'sleep(1);' ), )
				output.append( (4, '}' ), )
				output.append( (2, '}' ), )


			index_piece_name = self.puzzle.scenario.get_index_piece_name(depth)
			conflicts = "_conflicts" if index_piece_name.endswith("_conflicts") else ""
			
			uSide = "0" if space < W          else "board["+sspace+"-W]->d";
			rSide = "0" if (space+1) % W != 0 else "board["+sspace+"+1]->l";
			dSide = "0" if space > WH-W       else "board["+sspace+"+W]->u";
			lSide = "0" if space % W == 0     else "board["+sspace+"-1]->r";

			output.append( (2, "piece_index_to_try_next["+d+"] = cb->master_index_"+index_piece_name+"[ ("+lSide+" << EDGE_SHIFT_LEFT) + "+uSide+" ];" ) )
			output.append( (2, "") )

			
			if conflicts != "":
				conflicts_array = [ x for x in self.puzzle.scenario.conflicts_indexes_allowed if x < depth ]
				output.append( (2, "conflicts_allowed_this_turn = "+ str(len(conflicts_array))+ " - cumulative_heuristic_conflicts_count["+d+"-1]; //"+str(conflicts_array)))

			output.append( (2, 'depth'+d+"_backtrack:" ) )
	
			#output.append( (2, 'DEBUG_PRINT(("'+" "*depth+' Space '+sspace+' - trying index : %d %d %d\\n", piece_index_to_try_next['+d+'], '+lSide+', '+uSide+' ))'  if self.DEBUG > 0 else "" ))
			output.append( (2, "while (cb->"+master_lists_of_rotated_pieces+"[ piece_index_to_try_next["+d+"] ] != NULL) {"))
			
			
			output.append( (3, "current_rotated_piece = cb->"+master_lists_of_rotated_pieces+"[ piece_index_to_try_next["+d+"] ];" ))
			#output.append( (3, 'DEBUG_PRINT(("'+" " * depth+' Trying piece : %d\\n", current_rotated_piece->p))' ))
			if conflicts != "":
				#output.append( (3, "if ((current_rotated_piece->heuristic_side_and_conflicts_count & 1) > conflicts_allowed_this_turn) break;"))
				output.append( (3, "if (current_rotated_piece->heuristic_conflicts > conflicts_allowed_this_turn) break;"))
			
			output.append( (3, "piece_index_to_try_next["+d+"] ++;"))
			output.append( (3, "if (pieces_used[ current_rotated_piece->p ] != 0) continue;"))
			if depth > 0 and depth <= self.puzzle.scenario.heuristic_patterns_max_index and self.puzzle.scenario.heuristic_patterns_count[depth] > 0: 
				#output.append( (3, "if ((cumulative_heuristic_side_count["+d+"-1] + (current_rotated_piece->heuristic_side_and_conflicts_count >> 1)) < "+str(self.puzzle.scenario.heuristic_patterns_count[depth])+" ) break;"))
				output.append( (3, "if ((cumulative_heuristic_side_count["+d+"-1] + current_rotated_piece->heuristic_side) < "+str(self.puzzle.scenario.heuristic_patterns_count[depth])+" ) break;"))
			
			output.append( (3, "board["+sspace+"] = current_rotated_piece;"))
			#output.append( (3, 'DEBUG_PRINT(("'+" "*depth+' Space '+sspace+' - inserting piece : %d \\n", board['+sspace+']->p ))'  if self.DEBUG > 1 else "" ))
			output.append( (3, 'pieces_used[current_rotated_piece->p] = 1;' ) )
			if conflicts != "":
				#output.append( (3, "cumulative_heuristic_conflicts_count["+d+"] = cumulative_heuristic_conflicts_count["+d+"-1] + (current_rotated_piece->heuristic_side_and_conflicts_count & 1);"))
				output.append( (3, "cumulative_heuristic_conflicts_count["+d+"] = cumulative_heuristic_conflicts_count["+d+"-1] + current_rotated_piece->heuristic_conflicts;"))
			if depth == 0: 
				#output.append( (3, "cumulative_heuristic_side_count["+d+"] = (current_rotated_piece->heuristic_side_and_conflicts_count >> 1);"))
				output.append( (3, "cumulative_heuristic_side_count["+d+"] = current_rotated_piece->heuristic_side;"))
			elif depth <= self.puzzle.scenario.heuristic_patterns_max_index: 
				#output.append( (3, "cumulative_heuristic_side_count["+d+"] = cumulative_heuristic_side_count["+d+"-1] + (current_rotated_piece->heuristic_side_and_conflicts_count >> 1);"))
				output.append( (3, "cumulative_heuristic_side_count["+d+"] = cumulative_heuristic_side_count["+d+"-1] + current_rotated_piece->heuristic_side;"))
			
			output.append( (3, "goto depth"+str(depth+1)+";"))
			output.append( (2, "}"))

			output.append( (2, 'pieces_used[board['+sprevious_space+']->p] = 0;' if depth > 0 else "" ))
			output.append( (2, 'board['+sprevious_space+'] = NULL;' if depth > 0 else "" ))
			output.append( (2, ""))
			output.append( (2, "goto depth"+str(depth-1)+"_backtrack;" if depth>0 else "goto depth_end;" ))

		output.extend( [
			(1, 'depth_timelimit:' ),
			(2, 'DEBUG_PRINT(("x-]'+self.XTermInfo+'  Time Limit Reached  '+self.XTermNormal+'[-x\\n"));' ),
			(2, 'setWFN(cb, 1);' ),
			(2, 'sleep(5); // Wait for the WFN thread' ),
			] )

		output.extend( [
			(1, '// Where we find ourselves again' ),
			(1, 'depth_end:' ),
			(2, 'DEBUG_PRINT(("x-]'+self.XTermInfo+'  End of Solve  '+self.XTermNormal+'[-x\\n"));' ),
			] )


		output.extend( [
			(1, 'fdo_commands(output, cb);' ),
			(1, 'if (output != stdout) {' ),
			(2, 'fclose(output);' ),
			(1, '}' ),

			(1, 'if (was_allocated) {'), 
			(1, 'DEBUG_PRINT(("Free Memory\\n"));'), 
			(2, 'cb = free_blackwood(cb);'), 
			(2, 'global_blackwood = NULL;'), 
			(1, '}'), 

			(0, '}' ),
			] )

		return output


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
			(1, 'return solve(NULL, NULL);'), 
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
		self.writeGen( gen, self.gen_allocate_blackwood_function( only_signature=True ) )
		self.writeGen( gen, self.gen_free_blackwood_function( only_signature=True ) )
		self.writeGen( gen, self.gen_set_blackwood_arrays_function( only_signature=True ) )
		self.writeGen( gen, self.gen_save_max_depth_seen_function( only_signature=True ) )
		self.writeGen( gen, self.gen_getSolutionURL_function( only_signature=True ) )

		self.writeGen( gen, self.gen_print_url_functions(only_signature=True) )


		self.writeGen( gen, self.gen_do_commands(only_signature=True) )
		self.writeGen( gen, self.gen_print_functions(only_signature=True) )
		self.writeGen( gen, self.gen_solve_function(only_signature=True) )

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
			self.writeGen( gen, self.gen_allocate_blackwood_function( only_signature=False ) )
			self.writeGen( gen, self.gen_free_blackwood_function( only_signature=False ) )
			self.writeGen( gen, self.gen_set_blackwood_arrays_function( only_signature=False ) )
			self.writeGen( gen, self.gen_save_max_depth_seen_function( only_signature=False) )
			self.writeGen( gen, self.gen_getSolutionURL_function( only_signature=False ) )
			self.writeGen( gen, self.gen_print_url_functions(only_signature=False) )
			self.writeGen( gen, self.gen_print_functions(only_signature=False) )
			self.writeGen( gen, self.gen_do_commands(only_signature=False ) )



		elif macro_name == "generate":
			self.writeGen( gen, self.gen_solve_function(only_signature=False) )


		elif macro_name == "main":

			self.writeGen( gen, self.gen_main_function(only_signature=False) )


		self.writeGen( gen, self.getFooterC() )

	# ----- Self test
	def SelfTest( self ):

		sys.stdout.flush()
		

		# Start the chrono
		startTime = time.time()

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


		signal.signal(signal.SIGINT, self.LibExt.sig_handler)
		signal.signal(signal.SIGUSR1, self.LibExt.sig_handler)
		signal.signal(signal.SIGUSR2, self.LibExt.sig_handler)


		#thread_output_filename = ctypes.c_char_p("/tmp/test".encode('utf-8'))
		thread_output_filename = None

		cb = self.cb
		self.copy_new_arrays_to_cb()

		l = self.gen_solve_function( only_signature=True )
		args = []
		loc = locals()
		for pname in self.getParametersNamesFromSignature(l):
			args.append( loc[ pname ] )
		self.LibExtWrapper( self.getFunctionNameFromSignature(l), args, timeit=True )

		myLCA.stop_lca_thread = True	
		myWFN.stop_wfn_thread = True	
		myHB.stop_hb_thread = True	
		myInput.stop_input_thread = True	

		print()
		print( "Execution time: ", time.time() - startTime )

		return False


if __name__ == "__main__":
	import data

	p = data.loadPuzzle()
	if p != None:

		lib = LibBlackwood( p )
		while lib.SelfTest():
			pass

