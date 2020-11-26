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
import thread_wfs
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

	current_blackwood = None

	MACROS_NAMES_A = [ "utils", "generate", "main" ]
	MACROS_NAMES_B = [ ]

	DEPTH_COLORS = {}

	COMMANDS = { 
				'NONE':				0,
				'CLEAR_SCREEN':			1<<1,
				'SHOW_TITLE':			1<<2,
				'SHOW_HEARTBEAT':		1<<3,
				'SHOW_SEED':			1<<4,

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
			[ "Wait for Solution",		"wait_for_solution",		"WFS" ],
			[ "Time Heartbeat",		"heartbeat",			"HB" ],
			[ "Check for Commands",		"check_commands",		"CheckCommands" ],
			[ "Commands for Interactivity",	"commands",			"Commands" ],
		]
	
	FILTERED_DEPTH = [ 40 ] #64, 92 ]
		
	def __init__( self, puzzle, extra_name="" ):

		self.name = "libblackwood"

		self.puzzle = puzzle
		
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

		# Allocate memory
		self.current_blackwood = self.LibExt.allocate_blackwood()


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
			print( "current_blackwood:", self.current_blackwood )
			for (c, n, s) in self.FLAGS:
				f = getattr( self.LibExt, "get"+s )
				print( "get"+s+" "+str(f( self.current_blackwood ))+" | "+c )

		command_not_found = False

		for command in commands:
			if command in [ "c", "cls", "clear_screen" ]:
				self.LibExt.xorCommands( self.current_blackwood, self.COMMANDS[ 'CLEAR_SCREEN' ] )

			elif command in [ "d", "dnc", "show_depth_nodes_count" ]:
				self.LibExt.xorCommands( self.current_blackwood, self.COMMANDS[ 'SHOW_DEPTH_NODES_COUNT' ] )
			elif command in [ "z", "zero", "zero_depth_nodes_count" ]:
				self.LibExt.xorCommands( self.current_blackwood, self.COMMANDS[ 'ZERO_DEPTH_NODES_COUNT' ] )

			elif command in [ "b", "best", "show_best_board", "url" ]:
				self.LibExt.xorCommands( self.current_blackwood, self.COMMANDS[ 'SHOW_BEST_BOARD_URL_ONCE' ] )
			elif command in [ "m", "max", "show_max_depth_seen" ]:
				self.LibExt.xorCommands( self.current_blackwood, self.COMMANDS[ 'SHOW_MAX_DEPTH_SEEN_ONCE' ] )
			elif command in [ "s", "save", "save_max_depth_seen" ]:
				self.LibExt.xorCommands( self.current_blackwood, self.COMMANDS[ 'SAVE_MAX_DEPTH_SEEN_ONCE' ] )

			elif command in [ "", "print", "cc", "check_commands" ]:
				self.LibExt.setCheckCommands( self.current_blackwood, 1 )

			elif command in [ "n", "next" ]:
				self.LibExt.setHB( self.current_blackwood, 10000000 )

			elif command in [ "0", "000" ]:
				self.LibExt.clearHB( self.current_blackwood )

			elif command in [ "hb", "heartbeat" ]:
				lca   = self.LibExt.getLCA( self.current_blackwood )
				pause = self.LibExt.getPause( self.current_blackwood )
				if (lca == 0) or (pause == 0):
					self.LibExt.incHB( self.current_blackwood )

			elif command in [ "p", "pause", "lca" ]:
				self.LibExt.togglePause( self.current_blackwood, 1 )
			elif command in [ "w", "wfs" ]:
				self.LibExt.setWFS( self.current_blackwood, 1 )
			elif command in [ "q", "quit", "exit" ]:
				self.LibExt.setTTF( self.current_blackwood, 1 )

			elif command in [ "h", "help", "?" ]:
				print(self.H1_OPEN+"List of commands"+self.H1_CLOSE)
				print(" > q|quit")
				print(" > p|pause")
				print(" > n|next")
				print(" > s|save")
			else:
				command_not_found = True

		if not command_not_found:
			self.LibExt.setCheckCommands( self.current_blackwood, 1 )

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

			output.append( (0 , "p_rotated_piece master_lists_of_rotated_pieces[ "+str(len(self.puzzle.master_lists_of_rotated_pieces))+" ];") )

			for d in self.FILTERED_DEPTH:
				output.append( (0 , "p_rotated_piece master_lists_of_rotated_pieces_filtered_after_depth_"+str(d)+"[ "+str(len(self.puzzle.master_lists_of_rotated_pieces))+" ];") )

			output.extend( [
				(0, "" ),
				(1, "// The Board" ),
				(1, "p_rotated_piece board[ WH ];"),
				(0, "" ),
				(1, "// Counters on each node" ),
				(1, "uint64 depth_nodes_count[ WH ];"),
				(0, "" ),
				(1, "// The deepest roots of the search tree" ),
				(1, "uint64 max_depth_seen;"),
				(0, "" ),
				(1, "// Maximum number of heartbeats before death of the search tree" ),
				(1, "uint64	heartbeat_limit;"),
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

	# ----- Generate the solution into a string for WFS
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
			(1, "p_blackwood b,"),
			(1, "uint64 seed") 
			] )

		if only_signature:
			output.append( (1, ');') )
		else:
			output.append( (1, ") {") )
			output.append( (1, "if (b)") )
			output.append( (2, "b->seed = seed;") )
			output.append( (1, "else") )
			output.append( (2, 'DEBUG_PRINT(("set_blackwood_seed NULL pointer\\n"));') )
			output.append( (0, "}") )


		# Set master_indexes
		for name,array in self.puzzle.master_index.items():
			output.extend( [ 
				(0, "void set_blackwood_master_index_"+name+"("),
				(1, "p_blackwood b,"),
				(1, "uint64p array")
				] )

			if only_signature:
				output.append( (1, ');') )
			else:
				output.append( (1, ") {") )
				output.append( (1, "uint64 i;") )
				output.append( (1, "if (b)") )
				output.append( (2, "for(i=0; i<"+str(len(array))+"; i++) b->master_index_"+name+"[i] = array[i];") )
				output.append( (1, "else") )
				output.append( (2, 'DEBUG_PRINT(("set_blackwood_master_index_'+name+' NULL pointer\\n"));') )
				output.append( (0, "}") )


		# Set master_indexes
		output.extend( [ 
			(0, "void set_blackwood_master_lists_of_rotated_pieces("),
			(1, "p_blackwood b,"),
			(1, "uint64p array")
			] )

		if only_signature:
			output.append( (1, ');') )
		else:
			output.append( (1, ") {") )
			output.append( (1, "uint64 i;") )
			output.append( (1, "if (b) {") )
			output.append( (2, "for(i=0; i<"+str(len(self.puzzle.master_lists_of_rotated_pieces))+"; i++)") )
			output.append( (3, "if (array[i] != 0xffff)") )
			output.append( (4, "b->master_lists_of_rotated_pieces[i] = &(master_all_rotated_pieces[array[i]]);") )
			output.append( (3, "else") )
			output.append( (4, "b->master_lists_of_rotated_pieces[i] = NULL;") )
			output.append( (1, "} else") )
			output.append( (2, 'DEBUG_PRINT(("set_blackwood_master_index_'+name+' NULL pointer\\n"));') )
			output.append( (0, "}") )

		return output

	# ----- Copy to p_blackwood struct
	def copy_new_arrays_to_current_blackwood( self ):

		b = self.current_blackwood
	
		# Get a new random order of pieces lists
		seed = random.randint(0, sys.maxsize)
		if os.environ.get('SEED') != None:
			seed = int(os.environ.get('SEED'))
			if self.DEBUG > 0:
				self.info(" * Env Seed for Prepare Pieces : "+str(seed) )
		( master_index, master_lists_of_rotated_pieces, master_all_rotated_pieces ) = self.puzzle.prepare_pieces(local_seed=seed)

		# Set Seed
		self.LibExt.set_blackwood_seed( b, seed )

		# Set master_indexes
		for name,master_array in master_index.items():
			array = multiprocessing.RawArray(ctypes.c_uint64, len(master_array))
			for i in range(len(master_array)):
				if (master_array[ i ] != None):
					array[i] = master_array[ i ]
				else:
					array[i] = 0xffff

			f = getattr( self.LibExt, "set_blackwood_master_index_"+name )
			f( b, array )


		# Set master_lists_of_rotated_pieces
		array = multiprocessing.RawArray(ctypes.c_uint64, len(master_lists_of_rotated_pieces))
		for i in range(len(master_lists_of_rotated_pieces)):
			if  (master_lists_of_rotated_pieces[ i ] != None):
				array[i] = master_lists_of_rotated_pieces[ i ]
			else:
				array[i] = 0xffff
		
		self.LibExt.set_blackwood_master_lists_of_rotated_pieces(b, array)


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

		pf_str += "?puzzle="+self.puzzle.getFileFriendlyName(self.puzzle.name)
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

		pf_str += "&motifs_order=jblackwood"
		
		pf_str += "&seed=%llu"
		pf_args += "b->seed,"

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
				(1, 'uint64 i, s, piece;'), 
				(1, 'uint8 patterns[ WH * 4 ];'), 
				(1, 'uint8 url_pieces[ WH ];'), 
				(1, "p_rotated_piece * board;"),
				])

			output.extend( [
				(1, "board = b->board;"),
				(0, ""),
				(1, "for(i=0; i<WH*4; i++) patterns[i] = 0 + \'a\';"),
				])

			output.extend( [
				(1, "for(s=0; s<WH; s++) {"),
				(2, "if (board[ spaces_board_sequence[s] ] != NULL) {"),

				(3, "if ((pieces[board[ spaces_board_sequence[s] ]->p].u == board[ spaces_board_sequence[s] ]->u)&&"),
				(3, "    (pieces[board[ spaces_board_sequence[s] ]->p].r == board[ spaces_board_sequence[s] ]->r)) {"),
				(4, "url_pieces[ spaces_patterns_sequence[s] ] = board[ spaces_board_sequence[s] ]->p;"),
				(4, "patterns[ (spaces_patterns_sequence[s])*4 + 0 ] = pieces[board[ spaces_board_sequence[s] ]->p].u + \'a\'; // Up"),
				(4, "patterns[ (spaces_patterns_sequence[s])*4 + 1 ] = pieces[board[ spaces_board_sequence[s] ]->p].r + \'a\'; // Right"),
				(4, "patterns[ (spaces_patterns_sequence[s])*4 + 2 ] = pieces[board[ spaces_board_sequence[s] ]->p].d + \'a\'; // Down"),
				(4, "patterns[ (spaces_patterns_sequence[s])*4 + 3 ] = pieces[board[ spaces_board_sequence[s] ]->p].l + \'a\'; // Left"),
				(3, "} else"),

				(3, "if ((pieces[board[ spaces_board_sequence[s] ]->p].r == board[ spaces_board_sequence[s] ]->u)&&"),
				(3, "    (pieces[board[ spaces_board_sequence[s] ]->p].d == board[ spaces_board_sequence[s] ]->r)) {"),
				(4, "url_pieces[ spaces_patterns_sequence[s] ] = board[ spaces_board_sequence[s] ]->p;"),
				(4, "patterns[ (spaces_patterns_sequence[s])*4 + 0 ] = pieces[board[ spaces_board_sequence[s] ]->p].r + \'a\'; // Up"),
				(4, "patterns[ (spaces_patterns_sequence[s])*4 + 1 ] = pieces[board[ spaces_board_sequence[s] ]->p].d + \'a\'; // Right"),
				(4, "patterns[ (spaces_patterns_sequence[s])*4 + 2 ] = pieces[board[ spaces_board_sequence[s] ]->p].l + \'a\'; // Down"),
				(4, "patterns[ (spaces_patterns_sequence[s])*4 + 3 ] = pieces[board[ spaces_board_sequence[s] ]->p].u + \'a\'; // Left"),
				(3, "} else"),

				(3, "if ((pieces[board[ spaces_board_sequence[s] ]->p].d == board[ spaces_board_sequence[s] ]->u)&&"),
				(3, "    (pieces[board[ spaces_board_sequence[s] ]->p].l == board[ spaces_board_sequence[s] ]->r)) {"),
				(4, "url_pieces[ spaces_patterns_sequence[s] ] = board[ spaces_board_sequence[s] ]->p;"),
				(4, "patterns[ (spaces_patterns_sequence[s])*4 + 0 ] = pieces[board[ spaces_board_sequence[s] ]->p].d + \'a\'; // Up"),
				(4, "patterns[ (spaces_patterns_sequence[s])*4 + 1 ] = pieces[board[ spaces_board_sequence[s] ]->p].l + \'a\'; // Right"),
				(4, "patterns[ (spaces_patterns_sequence[s])*4 + 2 ] = pieces[board[ spaces_board_sequence[s] ]->p].u + \'a\'; // Down"),
				(4, "patterns[ (spaces_patterns_sequence[s])*4 + 3 ] = pieces[board[ spaces_board_sequence[s] ]->p].r + \'a\'; // Left"),
				(3, "} else"),

				(3, "if ((pieces[board[ spaces_board_sequence[s] ]->p].l == board[ spaces_board_sequence[s] ]->u)&&"),
				(3, "    (pieces[board[ spaces_board_sequence[s] ]->p].u == board[ spaces_board_sequence[s] ]->r)) {"),
				(4, "url_pieces[ spaces_patterns_sequence[s] ] = board[ spaces_board_sequence[s] ]->p;"),
				(4, "patterns[ (spaces_patterns_sequence[s])*4 + 0 ] = pieces[board[ spaces_board_sequence[s] ]->p].l + \'a\'; // Up"),
				(4, "patterns[ (spaces_patterns_sequence[s])*4 + 1 ] = pieces[board[ spaces_board_sequence[s] ]->p].u + \'a\'; // Right"),
				(4, "patterns[ (spaces_patterns_sequence[s])*4 + 2 ] = pieces[board[ spaces_board_sequence[s] ]->p].r + \'a\'; // Down"),
				(4, "patterns[ (spaces_patterns_sequence[s])*4 + 3 ] = pieces[board[ spaces_board_sequence[s] ]->p].d + \'a\'; // Left"),

				(3, "} else {"),
				(4, "url_pieces[ spaces_patterns_sequence[s] ] = 0;"),
				(4, "patterns[ (spaces_patterns_sequence[s])*4 + 0 ] = 1 + \'a\';"),
				(4, "patterns[ (spaces_patterns_sequence[s])*4 + 1 ] = 1 + \'a\';"),
				(4, "patterns[ (spaces_patterns_sequence[s])*4 + 2 ] = 1 + \'a\';"),
				(4, "patterns[ (spaces_patterns_sequence[s])*4 + 3 ] = 1 + \'a\';"),
				(3, "}"),

				(2, "} else {"),
				(3, "url_pieces[ spaces_patterns_sequence[s] ] = 0;"),
				(3, "patterns[ (spaces_patterns_sequence[s])*4 + 0 ] = 0 + \'a\';"),
				(3, "patterns[ (spaces_patterns_sequence[s])*4 + 1 ] = 0 + \'a\';"),
				(3, "patterns[ (spaces_patterns_sequence[s])*4 + 2 ] = 0 + \'a\';"),
				(3, "patterns[ (spaces_patterns_sequence[s])*4 + 3 ] = 0 + \'a\';"),
				(2, "}"),
				(1, "}"),
				])

			output.extend( [
				(1, prefix+'printf('), 
				(2, "url," if prefix == "s" else ""), 
				(2, "f," if prefix == "f" else ""), 
				(2, '"'+pf_str+'\\n",'), 
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






	# ----- Generate filter function
	def gen_filter_function( self, only_signature=False ):

		output = []

		for d in self.FILTERED_DEPTH:
			dd = str(d)
			output.extend([ 
				(0, "void filter_depth_"+dd+"("),
				(1, "p_blackwood b,"),
				(1, "uint8 * pieces_used"),
				])

			if only_signature:
				output.extend( [ (1, ');'), ])
			else:
				output.extend( [
					(1, ") {"),
					(0, ''), 
					(1, 'uint64 src, dst;'), 
					] )

				#output.append( (1, 'DEBUG_PRINT(("Filtering_depth_'+dd+'\\n"));' ) )
				output.append( (1, "dst = 0;" ) )
				output.append( (1, "for(src = 0; src < "+str(len(self.puzzle.master_lists_of_rotated_pieces))+"; src++) {" ) )
				output.append( (2, "if (b->master_lists_of_rotated_pieces[src] != NULL) { " ) )
				output.append( (3, "if (pieces_used[b->master_lists_of_rotated_pieces[src]->p] == 0) { " ) )
				output.append( (4, "b->master_lists_of_rotated_pieces_filtered_after_depth_"+dd+"[dst] = b->master_lists_of_rotated_pieces[src];" ) )
				output.append( (4, "dst++;" ) )
				output.append( (3, "}" ) )
				output.append( (2, "} else {" ) )
				output.append( (3, "b->master_lists_of_rotated_pieces_filtered_after_depth_"+dd+"[dst] = NULL;" ) )
				output.append( (3, "dst = src+1;") )
				output.append( (2, "}" ) )
				output.append( (1, "}" ) )
				output.append( (0, "}" ) )

		return output



	# ----- Generate Scoriste function
	def gen_solve_function( self, only_signature=False):

		output = []

		output.extend( [ 
			(0, "int solve("),
			(1, "charp thread_output_filename,"),
			(1, "p_blackwood current_blackwood"),
			] )

		if only_signature:
			output.append( (1, ');') )
			return output


		output.append( (1, ") {") )
		output.extend( [
			(1, 'uint64 i, turn, previous_score;' ),
			(1, 'FILE * output;' ),

			(1, 'uint8 was_allocated;' ),
			(1, 'uint8 pieces_used[WH];' ),
			(1, 'uint8 cumulative_heuristic_side_count[WH];' ),
			(1, 'uint8 cumulative_breaks_count[WH];' ),
			(1, 'uint16 piece_index_to_try_next[WH];' ),
			(1, 'uint64 depth_nodes_count[WH];' ),
			(1, 'uint64 piece_candidates;' ),
			(1, 'uint8 breaks_this_turn;' ),
			(1, 't_rotated_piece * current_rotated_piece;' ),
			(1, 't_rotated_piece * board['+str(self.puzzle.board_wh)+'];' ),
			(1, '' ),
			
			(1, 'was_allocated = 0;' ),
			(1, 'if (current_blackwood == NULL) {' ),
			#(2, 'DEBUG_PRINT(("Allocating Memory\\n"));'), 
			(2, 'current_blackwood = (p_blackwood)allocate_blackwood();'), 
			(2, 'was_allocated = 1;' ),
			(1, '}'), 
			(1, 'global_blackwood = current_blackwood;'), 

			(1, '' ),

			#(1, '// Seeding'), 
			#(1, 'srand(time(NULL)+getpid());'), 
			] )

		output.append( (1, "// Clear blackwood structure") )
		for (c, n, s) in self.FLAGS:
			output.append( (1, "current_blackwood->"+n+" = 0;") )

		output.extend( [
			(1, "current_blackwood->max_depth_seen = 0;"),
			(1, "current_blackwood->heartbeat_limit = heartbeat_time_bonus[ 0 ];"),
			(1, "current_blackwood->commands = CLEAR_SCREEN | SHOW_TITLE | SHOW_SEED | SHOW_HEARTBEAT | SHOW_DEPTH_NODES_COUNT | SHOW_MAX_DEPTH_SEEN | SHOW_BEST_BOARD_URL | ZERO_DEPTH_NODES_COUNT;" if self.DEBUG > 0 else ""),
			(1, "current_blackwood->commands = SHOW_HEARTBEAT;" if self.DEBUG == 0 else ""),
			(1, 'for(i=0;i<WH;i++) current_blackwood->board[i] = NULL;' ),
			(1, 'for(i=0;i<WH;i++) current_blackwood->depth_nodes_count[i] = 0;' ),
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
			(2, 'cumulative_breaks_count[i] = 0;' ),
			(2, 'piece_index_to_try_next[i] = 0xffff;' ),
			(2, 'depth_nodes_count[i] = 0;' ),
			(2, 'board[i] = NULL;' ),
			(1, '}' ),
			(1, '' ),
			(1, 'DEBUG_PRINT(("x-]'+self.XTermInfo+'  Starting Solve  '+self.XTermNormal+'[-x\\n"));' ),
			(1, '' ),
			])

		#for (c, n, s) in self.FLAGS:
		#	output.append( (1, 'DEBUG_PRINT(("'+c+': %llu\\n", current_blackwood->'+n+'));') )

		master_lists_of_rotated_pieces = "master_lists_of_rotated_pieces"

		# this goes from 0....255; we ve solved #0 already, so start at #1.
		for depth in range(0,self.puzzle.board_wh+1):
			d=str(depth)

			output.extend( [
				(1, "// ==--==--==--==--[ Reaching depth "+d+" ]--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--== "),
				(1, '' ),
				(1, 'depth'+d+":  // Labels are ugly, don't do this at home" ),
				] )

			#if depth in self.FILTERED_DEPTH:
			#	output.append( (2, '// We filter the lists to keep only the pieces that are left' ) )
			#	output.append( (2, 'filter_depth_'+d+'(current_blackwood, pieces_used);' ) )
			#	output.append( (0, '' ) )
			#	master_lists_of_rotated_pieces = "master_lists_of_rotated_pieces_filtered_after_depth_"+d

			#if depth > 249: #252:
			if depth >= 252:
				output.append( (2, 'if (current_blackwood->max_depth_seen < '+d+') {' if depth <256 else '') )
				output.append( (3, 'current_blackwood->max_depth_seen = '+d+';') )
				output.append( (3, 'current_blackwood->commands |= SAVE_MAX_DEPTH_SEEN_ONCE;' ) )
				output.append( (3, 'current_blackwood->commands |= SHOW_MAX_DEPTH_SEEN_ONCE;' ) )
				output.append( (3, 'current_blackwood->commands |= SHOW_BEST_BOARD_URL_ONCE;' if depth>=254 else '' ) )
				output.append( (3, 'current_blackwood->heartbeat_limit += heartbeat_time_bonus[ '+d+' ];') )
				output.append( (3, 'for(i=0;i<WH;i++) current_blackwood->board[i] = board[i];') )
				output.append( (3, 'fdo_commands(output, current_blackwood);' ) )
				output.append( (2, '}' if depth<256 else '') )
			if depth == self.puzzle.board_wh:
				output.append( (2, '// We have a complete puzzle !!' ) )
				output.append( (2, 'setWFS(current_blackwood, 1);' ) )
				output.append( (2, 'sleep(60); // Wait for the WFS thread' ) )
				output.append( (0, '' ) )
				# followed immediately by depth_end
				break


			(col, row) = self.puzzle.searchSequence[ depth ]
			space = row * self.puzzle.board_w + col
			srow = str(row)
			scol = str(col)
			sspace = str(space)

			output.append( (2, 'current_blackwood->depth_nodes_count['+sspace+'] ++;' if self.DEBUG > 0 else "") )

			output.append( (2, '' ) )
			if depth in [ 140 ] if self.DEBUG == 0 else [ 64, 92, 128, 144 ]:
				output.append( (2, 'if (current_blackwood->check_commands) {') )
				output.append( (3, 'clearCheckCommands(current_blackwood);' ), )
				output.append( (0, '' ) )
				output.append( (3, 'if (getTTF(current_blackwood)) goto depth_end;' ) )
				output.append( (0, '' ) )
				output.append( (3, 'if (current_blackwood->heartbeat > current_blackwood->heartbeat_limit) goto depth_end;' ) )
				output.append( (0, '' ) )
				output.append( (3, 'fdo_commands(output, current_blackwood);' ), )
				output.append( (0, '' ) )
				output.append( (3, 'if (getLCA(current_blackwood) || getPause(current_blackwood))' ) )
				output.append( (4, 'while ((getLCA(current_blackwood) || getPause(current_blackwood)) && !getTTF(current_blackwood)) {' ) )
				output.append( (5, 'fdo_commands(output, current_blackwood);' ), )
				output.append( (5, 'sleep(1);' ), )
				output.append( (4, '}' ), )
				output.append( (2, '}' ), )



			output.extend( [
				(2, 'if (board['+sspace+'] != NULL) {' ),
				(3, 'pieces_used[board['+sspace+']->p] = 0;' ),
				(3, 'board['+sspace+'] = NULL;' ),
				(2, '}' ),
				] )

			breaks = "" 
			if depth >= min(self.puzzle.break_indexes_allowed):
				breaks = "_breaks"
			else:
				if row == 15 and col != 15 and col != 0:
					breaks = "_breaks"


			leftSide = "0" if col==0 else "board[ "+sspace+" - 1 ]->r";
			upSide   = "0" if row==0 else "board[ "+sspace+" - "+str(self.puzzle.board_w)+" ]->u";

			if row == 0:
				if col == 15 or col == 0:
					master_piece_name = "corner"
				else:
					master_piece_name = "border_d"

			elif row == 15:
				if col == 15 or col == 0:
					master_piece_name = "corner"
				else:
					master_piece_name = "border_u" + breaks
			    
			else:
				if col == 15:
					master_piece_name = "border_r" + breaks
				elif col == 0:
					master_piece_name = "border_l"

				else:
					if row == 7:
						if col == 7:
							master_piece_name = "fixed"
						elif col == 6:
							master_piece_name = "fixed_west"
						else:
							master_piece_name = "center" + breaks

					elif row == 6:
						if col == 7:
							master_piece_name = "fixed_south"
						else:
							master_piece_name = "center" + breaks

					else:
						master_piece_name = "center" + breaks
					
				
			output.append( (2, "piece_candidates = current_blackwood->master_index_"+master_piece_name+"[ ("+leftSide+"<< EDGE_SHIFT_LEFT) + "+upSide+" ];" ) )
			output.append( (2, "") )

			
			output.append( (2, "if ((piece_candidates != 0xffff) && (current_blackwood->"+master_lists_of_rotated_pieces+"[ piece_candidates ] != NULL)) {"))
			if breaks != "":
				break_array = [ x for x in self.puzzle.break_indexes_allowed if x<depth ]
				output.append( (3, "breaks_this_turn = "+ str(len(break_array))+ " - cumulative_breaks_count["+d+"-1]; //"+str(break_array)))

			output.append( (3, "if ( piece_index_to_try_next["+d+"] != 0xffff ) piece_candidates = piece_index_to_try_next["+d+"];"))
	
			output.append( (3, "while (current_blackwood->"+master_lists_of_rotated_pieces+"[ piece_candidates ] != NULL) {"))
			
			
			output.append( (4, "current_rotated_piece = current_blackwood->"+master_lists_of_rotated_pieces+"[ piece_candidates ];" ))
			if breaks != "":
				output.append( (4, "if ((current_rotated_piece->heuristic_side_and_break_count & 1) > breaks_this_turn) break;"))
			
			output.append( (4, "if (pieces_used[ current_rotated_piece->p ] == 0) {"))

			if depth > 0 and depth <= self.puzzle.max_heuristic_index: 
				output.append( (5, "if ((cumulative_heuristic_side_count["+d+"-1] + (current_rotated_piece->heuristic_side_and_break_count >> 1)) < "+str(self.puzzle.heuristic_array[depth])+" ) break;"))
			
			output.append( (5, "board["+sspace+"] = current_rotated_piece;"))
			output.append( (5, 'pieces_used[current_rotated_piece->p] = 1;' ) )
			if breaks != "":
				output.append( (5, "cumulative_breaks_count["+d+"] = cumulative_breaks_count["+d+"-1] + (current_rotated_piece->heuristic_side_and_break_count & 1);"))
			if depth == 0: 
				output.append( (5, "cumulative_heuristic_side_count["+d+"] = (current_rotated_piece->heuristic_side_and_break_count >> 1);"))
			elif depth <= self.puzzle.max_heuristic_index: 
				output.append( (5, "cumulative_heuristic_side_count["+d+"] = cumulative_heuristic_side_count["+d+"-1] + (current_rotated_piece->heuristic_side_and_break_count >> 1);"))
			
			output.append( (5, "piece_index_to_try_next["+d+"] = piece_candidates+1;"))
			output.append( (5, "goto depth"+str(depth+1)+";"))
			output.append( (4, "}"))
			#output.append( (4, 'else current_blackwood->depth_nodes_count['+sspace+'] ++; // number of attempts on each node' ) )
			output.append( (4, "piece_candidates ++;"))
			output.append( (3, "}"))
			output.append( (2, "}"))
			output.append( (2, "piece_index_to_try_next["+d+"] = 0xffff;"))
			output.append( (2, "goto depth"+str(depth-1)+";" if depth>1 else "goto depth_end;"))

		output.extend( [
			(1, '// Where we find ourselves again' ),
			(1, 'depth_end:' ),
			(1, 'DEBUG_PRINT(("x-]'+self.XTermInfo+'  End of Solve  '+self.XTermNormal+'[-x\\n"));' ),
			] )


		output.extend( [
			(1, 'fdo_commands(output, current_blackwood);' ),
			(1, 'if (output != stdout) {' ),
			(2, 'fclose(output);' ),
			(1, '}' ),

			(1, 'if (was_allocated) {'), 
			(1, 'DEBUG_PRINT(("Free Memory\\n"));'), 
			(2, 'current_blackwood = free_blackwood(current_blackwood);'), 
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
		self.writeGen( gen, self.gen_filter_function( only_signature=True ) )
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
			self.writeGen( gen, self.gen_filter_function( only_signature=False ) )
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
		myWFS = thread_wfs.Wait_For_Solution_Thread( self, self.puzzle )
		myWFS.start()

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

		current_blackwood = self.current_blackwood
		self.copy_new_arrays_to_current_blackwood()

		l = self.gen_solve_function( only_signature=True )
		args = []
		loc = locals()
		for pname in self.getParametersNamesFromSignature(l):
			args.append( loc[ pname ] )
		self.LibExtWrapper( self.getFunctionNameFromSignature(l), args, timeit=True )

		myLCA.stop_lca_thread = True	
		myWFS.stop_wfs_thread = True	
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

