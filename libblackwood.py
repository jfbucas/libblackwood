# Global Libs
import os
import sys
import ctypes
import multiprocessing
import itertools
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


#if (sys.version_info[0] < 3) or (sys.version_info[1] < 6):
#    raise Exception("Python 3.6 or a more recent version is required.")


class LibBlackwood( external_libs.External_Libs ):
	"""Blackwood generation library"""

	cb = None

	MACROS_NAMES_A = [ "utils", "generate", "main" ]
	MACROS_NAMES_B = [ ]

	DEPTH_COLORS = {}

	COMMANDS = {}
	COMMANDS_LIST = [
				'CLEAR_SCREEN',
				'SHOW_TITLE',
				'SHOW_HEARTBEAT',
				'SHOW_ADAPTATIVE_FILTER',
				'SHOW_SEED',
				'SHOW_HELP',

				'SHOW_BEST_BOARD_URL',
				'SHOW_BEST_BOARD_URL_ONCE',

				'SHOW_MAX_DEPTH_SEEN',
				'SHOW_MAX_DEPTH_SEEN_ONCE',

				'SAVE_MAX_DEPTH_SEEN_ONCE',

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
			[ "Max Depth Seen",		"max_depth_seen",		"MaxDepthSeen" ],
			[ "Seed",			"seed",				"Seed" ],
		]

	STATS =	[
			("StatsNodesCount", "stats_nodes_count", "nodes", "STATS_NODES_COUNT"),
			("StatsPiecesTriedCount", "stats_pieces_tried_count", "pieces tried", "STATS_PIECES_TRIED_COUNT"),
			("StatsPiecesUsedCount", "stats_pieces_used_count", "pieces already in use", "STATS_PIECES_USED_COUNT"),
			("StatsHeuristicPatternsBreakCount", "stats_heuristic_patterns_break_count", "heuristic patterns breaks", "STATS_HEURISTIC_PATTERNS_BREAK_COUNT"),
			("StatsHeuristicConflictsBreakCount", "stats_heuristic_conflicts_break_count", "heuristic conflicts breaks", "STATS_HEURISTIC_CONFLICTS_BREAK_COUNT"),
			("StatsAdaptativeFilterCount", "stats_adaptative_filter_count", "adaptative filters", "STATS_ADAPTATIVE_FILTER_COUNT"),
		]

	ARRAYS = STATS + [
			("NodesHeartbeat", "nodes_heartbeat", "heartbeats", "NODES_HEARTBEAT"),
		]

	def __init__( self, puzzle, extra_name="", skipcompile=False ):

		self.name = "libblackwood"

		self.puzzle = puzzle
		
		self.xffff = format(len(self.puzzle.master_lists_of_rotated_pieces)-1, '6')



		# Add to the commands the arrays
		for (fname, vname, uname, flag)  in self.ARRAYS:
			self.COMMANDS_LIST.append( "SHOW_"+flag )
			self.COMMANDS_LIST.append( "ZERO_"+flag )


		self.COMMANDS[ "NONE" ] = 0
		i = 0
		for c in self.COMMANDS_LIST:
			self.COMMANDS[ c ] = 1<<i
			i += 1

		#self.DEPTH_COLORS[0]= "" 
		for i in range(190,253):
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
		self.modules_optimize = [ "generate" ]

		external_libs.External_Libs.__init__( self, skipcompile )

		# Allocate memory for current_blackwood
		self.cb = self.LibExt.allocate_blackwood()


	# ----- Load the C library
	def load( self ):

		self.LibExt = ctypes.cdll.LoadLibrary( self.getNameSO() )

		signatures = []
		signatures.extend( self.gen_getter_setter_function( only_signature=True ) )
		signatures.extend( self.gen_allocate_blackwood_function( only_signature=True ) )
		signatures.extend( self.gen_getSolutionURL_function( only_signature=True ) )
		signatures.extend( self.gen_getMaxDepthSeenHeartbeat_function( only_signature=True ) )
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

		command_found = False

		for command in commands:
			if command in [ "c", "cls", "clear_screen" ]:
				self.LibExt.xorCommands( self.cb, self.COMMANDS[ 'CLEAR_SCREEN' ] )
				command_found = True
			elif command in [ "seed", "show_seed" ]:
				self.LibExt.xorCommands( self.cb, self.COMMANDS[ 'SHOW_SEED' ] )
				command_found = True
			elif command in [ "b", "best", "show_best_board", "url" ]:
				self.LibExt.xorCommands( self.cb, self.COMMANDS[ 'SHOW_BEST_BOARD_URL_ONCE' ] )
				command_found = True
			elif command in [ "m", "max", "show_max_depth_seen" ]:
				self.LibExt.xorCommands( self.cb, self.COMMANDS[ 'SHOW_MAX_DEPTH_SEEN' ] )
				command_found = True
			elif command in [ "s", "save", "save_max_depth_seen" ]:
				self.LibExt.xorCommands( self.cb, self.COMMANDS[ 'SAVE_MAX_DEPTH_SEEN_ONCE' ] )
				command_found = True
			elif command in [ "", "print", "cc", "check_commands" ]:
				self.LibExt.setCheckCommands( self.cb, 1 )
				command_found = True
			elif command in [ "n", "next" ]:
				self.LibExt.setHB( self.cb, 10000000 )
				command_found = True
			elif command in [ "0", "000" ]:
				self.LibExt.clearHB( self.cb )
				command_found = True
			elif command in [ "hb", "heartbeat" ]:
				lca   = self.LibExt.getLCA( self.cb )
				pause = self.LibExt.getPause( self.cb )
				if (lca == 0) or (pause == 0):
					self.LibExt.incHB( self.cb )
				command_found = True
			elif command in [ "p", "pause", "lca" ]:
				self.LibExt.togglePause( self.cb, 1 )
				command_found = True
			elif command in [ "w", "sfn" ]:
				self.LibExt.setSFN( self.cb, 1 )
				command_found = True
			elif command in [ "q", "quit", "exit" ]:
				self.LibExt.setTTF( self.cb, 1 )
				command_found = True

			elif command in [ "h", "help", "?" ]:
				self.LibExt.xorCommands( self.cb, self.COMMANDS[ 'SHOW_HELP' ] )
				command_found = True

			if not command_found:
				for (fname, vname, uname, flag)  in self.ARRAYS:
					if command in  [ "SHOW_"+flag, "ZERO_"+flag ]:
						self.LibExt.xorCommands( self.cb, self.COMMANDS[ command ] )
						command_found = True

		if command_found:
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
				(2, prefix+'printf( '+out+' "\\n' + self.H1_OPEN + self.puzzle.TITLE_STR + self.H1_CLOSE + '\\n\\n" );' ),
				(0, '' ),

				(1, 'if (b->commands & SHOW_SEED)' ),
				(2, prefix+'printf( '+out+' "Seed: %llu\\n", b->seed);' ),
				(0, '' ),
				(1, 'if (b->commands & SHOW_HEARTBEAT)' ),
				(2, prefix+'printf( '+out+' "Heartbeats: %llu/%llu\\n", b->heartbeat, b->heartbeat_limit);' ),
				(0, '' ),
				(1, 'if (b->commands & SHOW_ADAPTATIVE_FILTER)' ),
				(2, prefix+'printf( '+out+' "Adaptative Filter Depth: %llu '+ ("(filtered=%llu)" if self.DEBUG>0 else "")+ '\\n", b->adaptative_filter_depth'+ (', b->stats_last_adaptative_filter_rejected' if self.DEBUG>0 else "") + ');' ),
				(0, '' ),
				] )

			for (fname, vname, uname, flag)  in self.STATS:
				vtname = vname.replace("stats_", "stats_total_")

				output.extend( [
				(1, 'if (b->commands & SHOW_'+flag+')' ),
				(2, prefix+'print'+fname+'( '+out+' b );' ),
				(0, '' ),

				(1, 'if (b->commands & ZERO_'+flag+')' ),
				(2, 'for(i=0;i<WH;i++) { b->'+vtname+' += b->'+vname+'[i]; b->'+vname+'[i] = 0; }' ),
				(0, '' ),
				] )



			output.extend( [
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
				(2, prefix+'printf( '+out+' " > w  | send notification\\n");'),
				(2, prefix+'printf( '+out+' " > b  | show best board\\n");'),
				(2, prefix+'printf( '+out+' " > m  | show max depth\\n");'),
				(2, prefix+'printf( '+out+' " > s  | save best board\\n");'),
				(2, prefix+'printf( '+out+' " > n  | next\\n");'),
				(2, prefix+'printf( '+out+' " > p  | pause\\n");'),
				(2, prefix+'printf( '+out+' " > n  | next\\n");'),
				(2, prefix+'printf( '+out+' " > s  | save\\n");'),
				(2, prefix+'printf( '+out+' " > q  | quit\\n");'),

				(2, (prefix+'printf( '+out+' "\\n Stats:\\n'+ "".join([ "  > "+format("SHOW_"+flag, "45")+"  > "+format("ZERO_"+flag, "45")+"\\n" for (fname, vname, uname, flag) in self.ARRAYS])+'\\n");') if self.DEBUG_STATS > 0 or self.DEBUG_PERF > 0 else ""),
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

			for name,array in self.puzzle.master_index.items():
				output.append( (1 , "uint16 master_index_"+name+"[ "+str(len(array))+" ];") )
			output.append( (1 , "uint16 * spaces_master_index[ WH ];") )

			output.append( (1 , "t_union_rotated_piece master_lists_of_union_rotated_pieces[ "+str(len(self.puzzle.master_lists_of_rotated_pieces))+" ];") )
			output.append( (1 , "t_union_rotated_piece master_lists_of_union_rotated_pieces_for_adaptative_filter[ "+str(len(self.puzzle.master_lists_of_rotated_pieces))+" ];") )
			output.append( (1 , "uint64 adaptative_filter_depth;"), )

			output.extend( [
				(0, "" ),
				(1, "// The Board" ),
				(1, "t_union_rotated_piece board[ WH ];"),
				(0, "" ),
				(1, "// Time keeping on nodes" ),
				(1, "uint16 nodes_heartbeat[ WH ];"),
				(0, "" ),
				(1, "// Records at what heartbeat the max_depth_seen have been found" ),
				(1, "uint16 max_depth_seen_heartbeat[ WH ];"),
				(0, "" ),
				] )


			for (fname, vname, uname, flag)  in self.STATS:
				vtname = vname.replace("stats_", "stats_total_")
				output.extend( [
				(1, "// Statistics "+uname ),
				(1, "uint64 "+vtname+";"),
				(1, "uint64 "+vname+"[ WH ];"),
				(0, "" ),
				] )

			output.extend( [
				(1, "uint64 stats_last_adaptative_filter_rejected;"),
				(0, "" ),
				] )

			output.extend( [
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
			output.append( (0 , "extern p_blackwood global_blackwood;") )
			output.append( (0 , "") )
		else:
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
		for (c, n, s) in self.FLAGS + [ (uname, vname.replace("stats_", "stats_total_"), fname ) for (fname, vname, uname, flag)  in self.STATS ]:

			output.append( (0, "// "+c+" functions"), )

			# ---------------------------------------
			output.append( (0, "void clear"+s+"("), )
			output.append( (1, "voidp b"), )
			if only_signature:
				output.append( (1, ');') )
			else:
				output.append( (1, ') {'), ) 
				output.append( (2, 'if (b) ((p_blackwood)b)->'+n+' = 0;'), ) 
				output.append( (2, 'else DEBUG_PRINT(("NULL on clear'+s+'\\n" ));'), )
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

	# ----- Generate the solution into a string for WFN
	def gen_getMaxDepthSeenHeartbeat_function( self, only_signature=False ):

		output = [ 
			(0, "uint64 getMaxDepthSeenHeartbeat("),
			(1, "voidp b,"),
			(1, "uint64 index"),
			]

		if only_signature:
			output.extend( [ (1, ');'), ])
			return output

		output.extend( [
			(1, ") {"),
			(2, 'return ((p_blackwood)b)->max_depth_seen_heartbeat[index];' ),
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

		for name,array in self.puzzle.master_index.items():
			output.append( (1 , "for(i=0; i<"+str(len(array))+"; i++) b->master_index_"+name+"[i] = master_index_"+name+"[i];") )

		for space in range(self.puzzle.board_wh):
			output.append( (1 , "b->spaces_master_index["+str(space)+"] = b->master_index_"+self.puzzle.scenario.get_index_piece_name(space)+";") )

		output.append( (1 , "for(i=0; i<"+str(len(self.puzzle.master_lists_of_rotated_pieces))+"; i++) b->master_lists_of_union_rotated_pieces[i] = master_lists_of_union_rotated_pieces[i];") )

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
			output.append( (3, "cb->master_lists_of_union_rotated_pieces[i].value = 0;") )
			output.append( (3, "if (array[i] != "+self.xffff+")") )
			output.append( (4, "cb->master_lists_of_union_rotated_pieces[i] = MAURP[array[i]];") )
			output.append( (3, "}") )
			output.append( (1, "} else") )
			output.append( (2, 'DEBUG_PRINT(("set_blackwood_master_index_'+name+' NULL pointer\\n"));') )
			output.append( (0, "}") )

		return output

	# ----- Copy to p_blackwood struct
	def copy_new_arrays_to_cb( self ):

		cb = self.cb
	
		# Get a new random order of pieces lists
		seed = self.puzzle.scenario.next_seed()
		( master_index, master_lists_of_rotated_pieces, master_all_rotated_pieces ) = self.puzzle.prepare_pieces()

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
		self.LibExt.setSeed(cb, seed )


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

		
		pf_str += "&motifs_order="+self.puzzle.motifs_order

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
				(1, 'uint16 url_pieces[ WH ];'), 
				])

			output.extend( [
				(0, ""),
				(1, "for(i=0; i<WH*4; i++) patterns[i] = 0;"),
				(1, "for(i=0; i<WH; i++) url_pieces[i] = 0;"),
				])

			output.extend( [
				(1, "for(space=0; space<WH; space++) {"),
				(2, "if (b->board[ space ].value == 0) continue;"),
				] )

			(u_unshift, r_unshift, d_unshift, l_unshift) = self.puzzle.scenario.edges_unshift_from_references()

			if self.puzzle.upside_down:
				output.extend( [
					(2, "// Insert the piece upside-down"),
					(2, "url_pieces[ WH-1-space ] = b->board[ space ].info.p+1;"), # Real pieces are numbered from 1 
					(2, "patterns[ (WH-1-space)*4 + 0 ] = b->board[ space ].info.d"+d_unshift+"; // Down"),
					(2, "patterns[ (WH-1-space)*4 + 1 ] = b->board[ space ].info.l"+l_unshift+"; // Left"),
					(2, "patterns[ (WH-1-space)*4 + 2 ] = b->board[ space ].info.u"+u_unshift+"; // Up"),
					(2, "patterns[ (WH-1-space)*4 + 3 ] = b->board[ space ].info.r"+r_unshift+"; // Right"),
					] )
			else:
				output.extend( [
					(2, "// Insert the piece"),
					(2, "url_pieces[ space ] = b->board[ space ].info.p+1;"), # Real pieces are numbered from 1 
					(2, "patterns[ space*4 + 0 ] = b->board[ space ].info.u"+u_unshift+"; // Up"),
					(2, "patterns[ space*4 + 1 ] = b->board[ space ].info.r"+r_unshift+"; // Right"),
					(2, "patterns[ space*4 + 2 ] = b->board[ space ].info.d"+d_unshift+"; // Down"),
					(2, "patterns[ space*4 + 3 ] = b->board[ space ].info.l"+l_unshift+"; // Left"),
					] )

			output.extend( [
				(1, "} // For"),
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

		for (prefix, (fname, vname, uname, flag))  in itertools.product([ "", "s", "f" ], self.ARRAYS):

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
					(1, "uint64 x, y;"),
					(1, "int64 count, total;"),
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
						(3, 'if (count <= 0) {' ),
						(4, prefix+'printf( '+out+'"  . " );' ),
						] )
					"""
					y = ""
					z = ""
					for x in range(0,16):
						output.extend( [
							(3, '} else if (count < 1'+y+') {' ),
							(4, prefix+'printf( '+out+'"'+self.rainbow[x] +"%3llu"+self.XTermNormal+' ", count/1'+z+');' ),
							] )
						y += "0"
						z += "000" if x % 3 == 2 else ""
					"""

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
						#(1, prefix+'printf( '+out+'"Total: %llu '+uname+'\\n\\n", total );' ),
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
						(1, prefix+'printf( '+out+'"Total: %llu '+uname+'/s\\n", total );' ),
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

		#for d in self.puzzle.scenario.depth_filters:
		#	dd = str(d)
		output.extend([ 
			(0, "void do_adaptative_filter("),
			(1, "p_blackwood b,"),
			(1, 'p_union_rotated_piece board' ),
			])

		if only_signature:
			output.extend( [ (1, ');'), ])
		else:
			output.extend( [
				(1, ") {"),
				(0, ''), 
				(1, 'uint64 src, dst, depth;'), 
				(1, 't_union_rotated_piece p;'),
				(1, 'uint8 pieces_used[WH];' ),
				(0, '' ),
				] )

			output.extend( [
				(1, 'b->stats_last_adaptative_filter_rejected = 0;' if self.DEBUG > 0 else "" ),
				(0, '' ),
				(1, '// Clear the pieces used' ),
				(1, 'for(depth=0; depth < WH; depth++) pieces_used[depth] = 0;' ),
				(0, '' ),
				(1, '// Find the most recent depth older than 1 heartbeat' ),
				(1, 'for(depth=0; depth < WH/2; depth++) {' ),
				(2, 'if ( b->nodes_heartbeat[depth] == 0 ) continue;' ),
				(2, 'if (b->nodes_heartbeat[depth] < b->heartbeat-1) {' ),
				(3, 'b->adaptative_filter_depth = depth;' ),
				(2, '} else {' ),
				(3, 'break;' ),
				(2, '}' ),
				(1, '}' ),
				(0, '' ),
				(1, '// Mark the pieces used up to then' ),
				(1, 'if ( b->adaptative_filter_depth < WH ) {' ),
				(2, 'for(depth=0; depth <= b->adaptative_filter_depth; depth++) {' ),
				(3, 'pieces_used[ board[ spaces_sequence[ depth ] ].info.p ] = 1;' ),
				(2, '}' ),
				(1, '}' ),
				(0, '' ),
				] )

			output.extend( [
				#(1, 'DEBUG_PRINT(("Filtering from depth %llu\\n", b->adaptative_filter_depth));' ),
				(1, "if (b->adaptative_filter_depth < WH) {" ),
				(2, "dst = 0;" ),
				(2, "for(src = 0; src < "+str(len(self.puzzle.master_lists_of_rotated_pieces))+"; src++) {" ),
				(3, "p = b->master_lists_of_union_rotated_pieces[src];" ),
				(3, "if (p.value != 0) { " ),
				(4, "if (pieces_used[p.info.p] == 0) { " ),
				(5, "b->master_lists_of_union_rotated_pieces_for_adaptative_filter[dst] = p;" ),
				(5, "dst++;" ),
				(4, "}" + (" else { b->stats_last_adaptative_filter_rejected ++; }" if self.DEBUG > 0 else "") ),
				(3, "} else {" ),
				(4, "b->master_lists_of_union_rotated_pieces_for_adaptative_filter[dst].value = 0;" ),
				(4, "dst = src+1;"),
				(3, "}" ),
				(2, "}" ),
				(1, "} else {" ),
				(2, "for(src = 0; src < "+str(len(self.puzzle.master_lists_of_rotated_pieces))+"; src++)" ),
				(3, "b->master_lists_of_union_rotated_pieces_for_adaptative_filter[src] = b->master_lists_of_union_rotated_pieces[src];" ),
				(1, "}" ),
				#(1, 'DEBUG_PRINT(("Filtering from depth %llu used=%llu rejected=%llu\\n", b->adaptative_filter_depth, used, rejected));' ),
				(0, " " ),
				] )

			output.append( (0, "}" ) )

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
			(1, 'uint64 i, index, previous_score;' ),
			(1, 'FILE * output;' ),
			(1, 'uint8 was_allocated;' ),
			(1, 'uint8 pieces_used[WH];' ),
			] )

		for i in range(5):
			if sum(self.puzzle.scenario.heuristic_patterns_count[i]) > 0:
				output.append( (1, "uint8 local_cumulative_heuristic_patterns_count_"+str(i)+";" ) )
				output.append( (1, "uint8 cumulative_heuristic_patterns_count_"+str(i)+"[WH];" ) )

		output.extend( [
			(1, 'uint8 cumulative_heuristic_conflicts_count[WH];' ),
			(1, 'p_union_rotated_piece piece_to_try_next[WH];' ),
			(1, 't_union_rotated_piece current_piece;' ),
			(1, 't_union_rotated_piece board['+str(WH)+'];' ),
			(1, '' ),
			
			(1, 'was_allocated = 0;' ),
			(1, 'if (cb == NULL) {' ),
			#(2, 'DEBUG_PRINT(("Allocating Memory\\n"));'), 
			(2, 'cb = (p_blackwood)allocate_blackwood();'), 
			(2, 'was_allocated = 1;' ),
			(1, '}'), 
			(1, 'global_blackwood = cb;'), 
			(1, '' ),
			] )

		output.append( (1, "// Clear blackwood structure") )
		for (c, n, s) in self.FLAGS:
			if c == "Seed":
				continue
			output.append( (1, "cb->"+n+" = 0;") )

		output.extend( [
			(1, "cb->heartbeat = 1; // We start at 1 for the adaptative filter "),
			(1, "cb->heartbeat_limit = heartbeat_time_bonus[ 0 ];"),
			] )

		if self.DEBUG > 0:
 			output.extend( [
			(1, "cb->commands |= CLEAR_SCREEN;"),
			(1, "cb->commands |= SHOW_TITLE;"),
			(1, "cb->commands |= SHOW_SEED;"),
			(1, "cb->commands |= SHOW_HEARTBEAT;"),
			(1, "cb->commands |= SHOW_ADAPTATIVE_FILTER;"),
			(1, "cb->commands |= SHOW_STATS_NODES_COUNT;"),
			(1, "cb->commands |= ZERO_STATS_NODES_COUNT;"),
			(1, "cb->commands |= SHOW_STATS_PIECES_TRIED_COUNT;"),
			(1, "cb->commands |= ZERO_STATS_PIECES_TRIED_COUNT;"),
			#(1, "cb->commands |= SHOW_STATS_PIECES_USED_COUNT;"),
			#(1, "cb->commands |= ZERO_STATS_PIECES_USED_COUNT;"),
			#(1, "cb->commands |= SHOW_STATS_HEURISTIC_PATTERNS_BREAK_COUNT;"),
			#(1, "cb->commands |= ZERO_STATS_HEURISTIC_PATTERNS_BREAK_COUNT;"),
			#(1, "cb->commands |= SHOW_STATS_HEURISTIC_CONFLICTS_BREAK_COUNT;"),
			#(1, "cb->commands |= ZERO_STATS_HEURISTIC_CONFLICTS_BREAK_COUNT;"),
			(1, "cb->commands |= SHOW_STATS_ADAPTATIVE_FILTER_COUNT;"),
			(1, "cb->commands |= ZERO_STATS_ADAPTATIVE_FILTER_COUNT;"),
			#(1, "cb->commands |= SHOW_NODES_HEARTBEAT;"),
			#(1, "cb->commands |= ZERO_NODES_HEARTBEAT;"),
			(1, "cb->commands |= SHOW_MAX_DEPTH_SEEN;"),
			(1, "cb->commands |= SHOW_BEST_BOARD_URL;"),
			] )

		output.extend( [
			(1, 'for(i=0;i<WH;i++) cb->board[i].value = 0;' ),
			(1, 'for(i=0;i<WH;i++) cb->nodes_heartbeat[i] = 0;' ),
			(1, 'for(i=0;i<WH;i++) cb->max_depth_seen_heartbeat[i] = 0;' ),
			(1, 'cb->adaptative_filter_depth = WH;' ),
			(2, ""),
			] )

		for (fname, vname, uname, flag)  in self.STATS:
			vtname = vname.replace("stats_", "stats_total_")
			output.extend( [
				(1, 'cb->'+vtname+" = 0;"),
				(1, 'for(i=0;i<WH;i++) cb->'+vname+'[i] = 0;' ),
				(0, "" ),
				] )


		output.extend( [
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
			] )

		for i in range(5):
			if sum(self.puzzle.scenario.heuristic_patterns_count[i]) > 0:
				output.append( (2, 'cumulative_heuristic_patterns_count_'+str(i)+'[i] = 0;' ) )

		output.extend( [
			(2, 'cumulative_heuristic_conflicts_count[i] = 0;' ),
			(2, 'piece_to_try_next[i] = &(cb->master_lists_of_union_rotated_pieces['+self.xffff+']);' ),
			(2, 'board[i].value = 0;' ),
			(1, '}' ),
			(1, '' ),
			(1, 'DEBUG_PRINT(("x-]'+self.XTermInfo+'  Starting Solve  '+self.XTermNormal+'[-x\\n"));' ),
			(1, '' ),
			])

		#for (c, n, s) in self.FLAGS:
		#	output.append( (1, 'DEBUG_PRINT(("'+c+': %llu\\n", cb->'+n+'));') )
		
		# this goes from 0....255; we have solved #0 already, so start at #1.
		for depth in range(0,WH+1):
			d=str(depth)

			output.extend( [
				(1, "// ==--==--==--==--[ Reaching depth "+d+" ]--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--== "),
				(1, '' ),
				(1, 'asm("# depth '+d+'");' ),
				(1, 'depth'+d+":  // Labels are ugly, don't do this at home" ),
				] )

			if ((self.DEBUG > 0 and depth > WH//2) or (depth > self.puzzle.scenario.depth_first_notification-7)) and depth < self.puzzle.scenario.depth_first_notification:
				output.append( (2, 'if (cb->max_depth_seen < '+d+') {') )
				output.append( (3, 'cb->max_depth_seen = '+d+';') )
				output.append( (3, 'cb->max_depth_seen_heartbeat['+d+'] = cb->heartbeat;') )
				if self.DEBUG > 0:
					output.append( (3, 'for(i=0;i<WH;i++) cb->board[i] = board[i];') )
				output.append( (2, '}' ))

			if depth >= self.puzzle.scenario.depth_first_notification:
				output.append( (2, 'if (cb->max_depth_seen < '+d+') {' if depth < WH else '') )
				output.append( (3, 'cb->max_depth_seen = '+d+';') )
				output.append( (3, 'cb->max_depth_seen_heartbeat['+d+'] = cb->heartbeat;' if depth < WH else '') )
				output.append( (3, 'cb->heartbeat_limit += heartbeat_time_bonus[ '+d+' ];') )
				output.append( (3, 'for(i=0;i<WH;i++) cb->board[i] = board[i];') )
				output.append( (3, 'cb->wait_for_notification = 1;' ) )
				output.append( (3, 'cb->commands |= SAVE_MAX_DEPTH_SEEN_ONCE;' ) )
				output.append( (3, 'cb->commands |= SHOW_MAX_DEPTH_SEEN_ONCE;' ) )
				output.append( (3, 'cb->commands |= SHOW_BEST_BOARD_URL_ONCE;' if depth>=WH-2 else '' ) )
				output.append( (3, 'fdo_commands(output, cb);' ) )
				output.append( (2, '}' if depth<WH else '') )

			if depth == WH:
				output.append( (2, '// We have a complete puzzle !!' ) )
				output.append( (2, 'cb->wait_for_notification = 1;' ) )
				output.append( (2, 'for(i=0;(i<3000000) && (!cb->time_to_finish);i++) {') )
				output.append( (3, 'fdo_commands(output, cb);' ) )
				output.append( (3, 'sleep(1); // Wait for the WFN thread' ) )
				output.append( (2, '}' ) )
				output.append( (0, '' ) )
				output.append( (2, "goto depth_end;"))
				break


			if depth > 0:
				previous_space = self.puzzle.scenario.spaces_sequence[ depth-1 ]
				sprevious_space = str(previous_space)

			space = self.puzzle.scenario.spaces_sequence[ depth ]
			sspace = str(space)

			output.append( (2, 'cb->stats_nodes_count['+sspace+'] ++;' if self.DEBUG_STATS > 0 else "") )
			output.append( (2, 'cb->stats_total_nodes_count ++;' if self.DEBUG_PERF > 0 else "") )
			output.append( (2, '' ), )

			output.append( (2, 'cb->nodes_heartbeat['+d+'] = cb->heartbeat;' if (self.DEBUG > 0) or (depth < (WH//2)) else "") )
			if self.puzzle.scenario.use_adaptative_filter_depth and depth < (WH//2):
				output.append( (2, "// if we backtrack further than the current adaptative_filter_depth, we reset" ) )
				output.append( (2, "if (cb->adaptative_filter_depth > "+d+") {") )
				output.append( (3, 'cb->adaptative_filter_depth = WH;'), )
				output.append( (3, 'cb->stats_adaptative_filter_count['+sspace+'] ++;' if self.DEBUG_STATS > 0 else "") )
				output.append( (3, 'cb->stats_total_adaptative_filter_count ++;' if self.DEBUG_PERF > 0 else "") )
				output.append( (3, 'do_adaptative_filter(cb, board);') )
				output.append( (2, '}'), )
				output.append( (2, '' ), )

			output.append( (2, '' ) )
			if depth in (range(0, WH, W*4) if self.DEBUG == 0 else range(0, WH, W*2)):
				output.append( (2, 'if (cb->check_commands) {') )
				#output.append( (3, 'DEBUG_PRINT(("'+" "*depth+' Space '+sspace+' - checking commands : %llx \\n", cb->commands ))'  if self.DEBUG > 1 else "" ))
				output.append( (3, 'cb->check_commands = 0;' ), )
				output.append( (0, '' ) )
				output.append( (3, 'if (cb->time_to_finish) goto depth_end;' ) )
				output.append( (0, '' ) )
				output.append( (3, 'if (cb->heartbeat > cb->heartbeat_limit) goto depth_timelimit;' ) )
				output.append( (0, '' ) )
				if self.puzzle.scenario.use_adaptative_filter_depth:
					output.append( (3, '// Adaptive Filter when a command is received, usually the heartbeat' ) )
					output.append( (3, 'cb->stats_adaptative_filter_count['+sspace+'] ++;' if self.DEBUG_STATS > 0 else "") )
					output.append( (3, 'cb->stats_total_adaptative_filter_count ++;' if self.DEBUG_PERF > 0 else "") )
					output.append( (3, 'do_adaptative_filter(cb, board);') )
					output.append( (0, '' ) )
				output.append( (3, 'fdo_commands(output, cb);' ), )
				output.append( (0, '' ) )
				output.append( (3, 'while ((cb->leave_cpu_alone || cb->pause) && !cb->time_to_finish) {' ) )
				output.append( (4, 'fdo_commands(output, cb);' ), )
				output.append( (4, 'sleep(1);' ), )
				output.append( (3, '}' ), )
				output.append( (0, '' ), )
				output.append( (3, 'if (cb->send_a_notification) {' ), )
				output.append( (4, 'if (cb->max_depth_seen == 0) for(i=0;i<WH;i++) cb->board[i] = board[i];') )
				output.append( (4, 'cb->wait_for_notification = 1;' ) )
				output.append( (4, 'cb->send_a_notification = 0;' ), )
				output.append( (3, '}' ), )
				output.append( (2, '}' ), )
				output.append( (0, '' ), )


			
			Side = {}
			Side["u"] = "0" if space < W          else "board["+sspace+"-W].info.d";
			Side["r"] = "0" if space % W == W-1   else "board["+sspace+"+1].info.l";
			Side["d"] = "0" if space >= WH-W      else "board["+sspace+"+W].info.u";
			Side["l"] = "0" if space % W == 0     else "board["+sspace+"-1].info.r";

			for_ref = self.puzzle.scenario.spaces_references[ space ]
			if len(for_ref) == 0:
				ref = "0"
				strref = "0, 0"
			elif len(for_ref) == 1:
				ref = Side[for_ref[0]]
				strref = Side[for_ref[0]]+ ", 0"
			elif len(for_ref) == 2:
				ref = "("+Side[for_ref[0]]+" << EDGE_SHIFT_LEFT) | "+Side[for_ref[1]]
				if len(self.puzzle.scenario.possible_references) == 1:
					ref = Side[for_ref[0]]+" | "+Side[for_ref[1]]
				strref = Side[for_ref[0]]+" , "+Side[for_ref[1]]
			elif len(for_ref) == 3:
				ref = "((("+Side[for_ref[0]]+" << EDGE_SHIFT_LEFT) | "+Side[for_ref[1]]+") << EDGE_SHIFT_LEFT) | "+Side[for_ref[2]]
				strref = "0, 0"
			elif len(for_ref) == 4:
				ref = "((("+Side[for_ref[0]]+" << EDGE_SHIFT_LEFT) | "+Side[for_ref[1]]+") << EDGE_SHIFT_LEFT) | "+Side[for_ref[2]]
				strref = "0, 0"

			total_hp = ""
			for i in range(5):
				if sum(self.puzzle.scenario.heuristic_patterns_count[i]) > 0:
					total_hp += 'cumulative_heuristic_patterns_count_'+str(i)+'['+d+'-1] + '

			# Unlikely we need the master_lists_of_union_rotated_pieces_hp before reaching the max_index
			index_piece_name = self.puzzle.scenario.get_index_piece_name(depth)
			#output.append( (2, "piece_to_try_next["+d+"] = &(cb->"+master_lists_of_union_rotated_pieces+"[cb->master_index_"+index_piece_name+"[ "+ref+" ] ]);" ) )
			if self.puzzle.scenario.use_adaptative_filter_depth:
				output.append( (2, "index = cb->master_index_"+index_piece_name+"[ "+ref+" ];" ) )
				#output.append( (2, "if ( "+d+" >= cb->adaptative_filter_depth ) {" ) )
				output.append( (2, "piece_to_try_next["+d+"] = &(cb->master_lists_of_union_rotated_pieces_for_adaptative_filter[index]);" ) )
				#output.append( (2, "} else {" ) )
				#output.append( (3, "piece_to_try_next["+d+"] = &(cb->master_lists_of_union_rotated_pieces[index]);" ) )
				#output.append( (2, "}" ) )
			else:
				output.append( (2, "index = cb->master_index_"+index_piece_name+"[ "+ref+" ];" ) )
				output.append( (2, "piece_to_try_next["+d+"] = &(cb->master_lists_of_union_rotated_pieces[index]);" ) )


			output.append( (2, "") )
			output.append( (2, 'asm("# depth_backtrack '+d+'");' ) )
			output.append( (2, 'depth'+d+"_backtrack:" ) )
	
			#if conflicts != "":
			#output.append( (2, 'DEBUG_PRINT(("'+" "*depth+' Space '+sspace+' - trying index : %p %d %d\\n", piece_to_try_next['+d+'], '+strref+' ))'  if self.DEBUG > 0 else "" ))
			#output.append( (2, 'DEBUG_PRINT(("'+ " "*depth +str(depth)+'\\n"))' ))
			output.append( (2, "while ( piece_to_try_next["+d+"]->value != 0 ) {"))
			
			output.append( (3, 'cb->stats_pieces_tried_count['+sspace+'] ++;' if self.DEBUG_STATS > 0 else "") )
			output.append( (3, 'cb->stats_total_pieces_tried_count ++;' if self.DEBUG_PERF > 0 else "") )
			
			output.append( (3, "current_piece = *(piece_to_try_next["+d+"]);" ))
			output.append( (3, "piece_to_try_next["+d+"] ++;"))
			#output.append( (3, 'DEBUG_PRINT(("'+" " * depth+' Trying piece : %d\\n", current_piece.info.p))' ))
			if depth > 0:
				for i in range(5):
					if sum(self.puzzle.scenario.heuristic_patterns_count[i][depth:]) > 0:
						output.append( (3, "local_cumulative_heuristic_patterns_count_"+str(i)+" = cumulative_heuristic_patterns_count_"+str(i)+"["+d+"-1] + current_piece.info.heuristic_patterns_"+str(i)+";"))
						if self.puzzle.scenario.heuristic_patterns_count[i][depth] > 0: 
							output.append( (3, "if (local_cumulative_heuristic_patterns_count_"+str(i)+" < "+str(self.puzzle.scenario.heuristic_patterns_count[i][depth])+" ) { "))
							output.append( (4, "cb->stats_heuristic_patterns_break_count[ "+sspace+"]++; " if self.DEBUG_STATS > 0 else "" ))
							output.append( (4, "cb->stats_total_heuristic_patterns_break_count ++; " if self.DEBUG_PERF > 0 else "" ))
							output.append( (4, "break;"))
							output.append( (3, "}"))


			if sum(self.puzzle.scenario.heuristic_conflicts_count) > 0:
				conflicts_allowed = self.puzzle.scenario.heuristic_conflicts_count[space]
				if conflicts_allowed > 0:
					if self.puzzle.scenario.heuristic_conflicts_count[previous_space] != conflicts_allowed:
						# if there is an increment in the heuristic, no need to test, it will always pass the test
						pass
					else:
						output.append( (3, "if (current_piece.info.heuristic_conflicts + cumulative_heuristic_conflicts_count["+d+"-1] > "+str(conflicts_allowed)+ ") { "))
						output.append( (4, "cb->stats_heuristic_conflicts_break_count[ "+sspace+"]++; " if self.DEBUG_STATS > 0 else "" ))
						output.append( (4, "cb->stats_total_heuristic_conflicts_break_count ++; " if self.DEBUG_PERF > 0 else "" ))
						output.append( (4, "break;" ))
						output.append( (3, "} // "+str(conflicts_allowed)))
			
			output.append( (3, "if (pieces_used[ current_piece.info.p ] != 0) {"))
			output.append( (4, 'cb->stats_pieces_used_count['+sspace+'] ++;' if self.DEBUG_STATS > 0 else "") )
			output.append( (4, 'cb->stats_total_pieces_used_count ++;' if self.DEBUG_PERF > 0 else "") )
			output.append( (4, "continue;"))
			output.append( (3, "}"))
			
			output.append( (3, "board["+sspace+"] = current_piece;"))
			#output.append( (3, 'DEBUG_PRINT(("'+" "*depth+' Space '+sspace+' - inserting piece : %d \\n", board['+sspace+'].info.p ))'  if self.DEBUG > 1 else "" ))
			output.append( (3, "pieces_used[ current_piece.info.p ] = 1;" ) )

			for i in range(5):
				if sum(self.puzzle.scenario.heuristic_patterns_count[i][depth:]) > 0:
					#cumul = "" if depth == 0 else "cumulative_heuristic_patterns_count_"+str(i)+"["+d+"-1] +" 
					#if depth <= self.puzzle.scenario.max_index(self.puzzle.scenario.heuristic_patterns_count[i]): 
					#output.append( (3, "cumulative_heuristic_patterns_count_"+str(i)+"["+d+"] = "+cumul+" current_piece.info.heuristic_patterns_"+str(i)+";"))
					if depth == 0:
						output.append( (3, "cumulative_heuristic_patterns_count_"+str(i)+"["+d+"] = current_piece.info.heuristic_patterns_"+str(i)+";"))
					else:
						output.append( (3, "cumulative_heuristic_patterns_count_"+str(i)+"["+d+"] = local_cumulative_heuristic_patterns_count_"+str(i)+";"))

			if sum(self.puzzle.scenario.heuristic_conflicts_count) > 0:
				conflicts_allowed = self.puzzle.scenario.heuristic_conflicts_count[space]
				if conflicts_allowed > 0:
					cumul = "" if depth == self.puzzle.scenario.conflicts_indexes_allowed[0] else "cumulative_heuristic_conflicts_count["+d+"-1] + "
					output.append( (3, "cumulative_heuristic_conflicts_count["+d+"] = "+cumul+" current_piece.info.heuristic_conflicts;"))
			
			output.append( (3, "goto depth"+str(depth+1)+";"))
			output.append( (2, "}"))

			output.append( (2, 'pieces_used[ board['+sprevious_space+'].info.p ] = 0;' if depth > 0 else "" ))
			#output.append( (2, 'board['+sprevious_space+'].value = 0;' if depth > 0 else "" ))
			output.append( (2, ""))
			output.append( (2, "goto depth"+str(depth-1)+"_backtrack;" if depth > 0 else "goto depth_end;" ))

		output.extend( [
			(1, 'depth_timelimit:' ),
			(2, 'DEBUG_PRINT(("x-]'+self.XTermInfo+'  Time Limit Reached  '+self.XTermNormal+'[-x\\n"));' ),
			] )
		if os.environ.get('NOTIFY_END') != None:
			output.extend( [
			(2, 'cb->wait_for_notification = 1;' ),
			(2, 'sleep(5); // Wait for the WFN thread' ),
			] )

		output.extend( [
			(1, '// Where we find ourselves again' ),
			(1, 'depth_end:' ),
			(2, 'DEBUG_PRINT(("x-]'+self.XTermInfo+'  End of Solve  '+self.XTermNormal+'[-x\\n"));' ),
			] )

		#if self.DEBUG_STATS > 0 or self.DEBUG_PERF > 0:
		#	if os.environ.get('STRUCT') != None:
		#		output.extend( [ (2, 'printf("'+str(self.LibDep['arrays'].getStruct())+'\\n");'), ] )
		#	for (fname, vname, uname, flag) in self.STATS:
		#		vtname = vname.replace("stats_", "stats_total_")
		#		output.extend( [ (2, 'if (cb->'+vtname+' > 0) { printf("%llu '+uname+'\\n", cb->'+vtname+' / cb->heartbeat); }'), ] )

		output.extend( [
			(1, 'fdo_commands(output, cb);' ),
			(1, 'if (output != stdout) {' ),
			(2, 'fclose(output);' ),
			(1, '}' ),
			] )

		output.extend( [
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
		self.writeGen( gen, self.gen_getMaxDepthSeenHeartbeat_function( only_signature=True ) )

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
			self.writeGen( gen, self.gen_getMaxDepthSeenHeartbeat_function( only_signature=False ) )
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
		self.top("selftest")

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

		top = self.top("selftest", unit=False)
		if not self.QUIET:
			print()
			print( "Self-Test execution time: ", top )

		if self.DEBUG_STATS > 0 or self.DEBUG_PERF > 0:
			#if os.environ.get('STRUCT') != None:
			print(self.LibDep['arrays'].getStruct())
			for (fname, vname, uname, flag) in self.STATS:
				#vtname = vname.replace("stats_", "stats_total_")
				f = getattr( self.LibExt, "get"+fname )
				a = f( cb )
				if a > 0:
					print( int(a/float(top)), uname + '/s =>', a, 'in', top, 'seconds' )

		return False


if __name__ == "__main__":
	import data

	p = data.loadPuzzle()
	if p != None:

		lib = LibBlackwood( p )
		while lib.SelfTest():
			pass

