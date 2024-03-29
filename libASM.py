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

	MACROS_NAMES_A = [ "utils", "generate", "funky_asm", "main" ]
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
			[ "Max Depth Seen",		"best_depth_seen",		"BestDepth" ],
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
		signatures.extend( self.gen_getBestDepthHeartbeat_function( only_signature=True ) )
		#signatures.extend( self.gen_solve_function(only_signature=True) )
		signatures.extend( self.gen_solve_funky_bootstrap_c(only_signature=True) )
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
			elif command in [ "m", "max", "show_best_depth_seen" ]:
				self.LibExt.xorCommands( self.cb, self.COMMANDS[ 'SHOW_MAX_DEPTH_SEEN' ] )
				command_found = True
			elif command in [ "s", "save", "save_best_depth_seen" ]:
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
				if self.DEBUG > 0:
					print("=[ TTF ]=")
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
				(1, 'if (b->commands & SHOW_'+flag+') {' ),
				(2, prefix+'print'+fname+'( '+out+' b );' ),
				(2, 'printf( "Total '+vname+' = %llu\\n", b->'+vtname+' );' ),
				(1, '}' ),
				(0, '' ),

				(1, 'if (b->commands & ZERO_'+flag+')' ),
				#(2, 'for(i=0;i<WH;i++) { b->'+vtname+' += b->'+vname+'[i]; b->'+vname+'[i] = 0; }' ),
				(2, 'for(i=0;i<WH;i++) { b->'+vname+'[i] = 0; }' ),
				(0, '' ),
				] )



			output.extend( [
				# SHOW BEST_BOARD
				(1, 'if (b->commands & (SHOW_BEST_BOARD_URL | SHOW_BEST_BOARD_URL_ONCE) ) {' ),
				(2, 'if (b->best_depth_seen > 0)' ),
				(3, prefix+'printBoardURL( '+out+' b);' ),
				(2, 'b->commands &= ~SHOW_BEST_BOARD_URL_ONCE;' ),
				(1, '}' ),
				(0, '' ),


				# SHOW/SAVE MAX_DEPTH
				(1, 'if (b->commands & (SHOW_MAX_DEPTH_SEEN | SHOW_MAX_DEPTH_SEEN_ONCE) ) {' ),
				(2, "".join( [ 'if (b->best_depth_seen == '+str(k)+' ) '+prefix+'printf( '+out+' "Max Depth Seen = '+self.DEPTH_COLORS[k]+str(k)+self.XTermNormal+'\\n\\n'+'");' for k in self.DEPTH_COLORS] ) ),
				(2, 'b->commands &= ~SHOW_MAX_DEPTH_SEEN_ONCE;' ),
				(1, '}' ),
				(0, '' ),

				(1, 'if (b->commands & SAVE_MAX_DEPTH_SEEN_ONCE) {' ),
				(2, ''.join( [ 'if (b->best_depth_seen == '+str(k)+' ) save_best_depth_seen_'+str(k)+'(b);' for k in self.DEPTH_COLORS] ) ),
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

				(2, (prefix+'printf( '+out+' "\\n Stats:\\n'+ "".join([ "  > "+format("SHOW_"+flag, "45")+"  > "+format("ZERO_"+flag, "45")+"\\n" for (fname, vname, uname, flag) in self.ARRAYS])+'\\n");') if self.puzzle.scenario.STATS > 0 or self.puzzle.scenario.PERF > 0 else ""),
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

		# Blackwood
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
				(1, "// The Board Pieces" ),
				(1, "t_piece board_pieces[ WH ];"),
				(0, "" ),
				(1, "// Time keeping on nodes" ),
				(1, "uint16 nodes_heartbeat[ WH ];"),
				(0, "" ),
				(1, "// Records at what heartbeat the best_depth_seen have been found" ),
				(1, "uint16 best_depth_seen_heartbeat[ WH ];"),
				(0, "" ),
				] )


			for (fname, vname, uname, flag)  in self.STATS:
				vtname = vname.replace("stats_", "stats_total_")
				output.extend( [
				(1, "// Statistics "+uname ),
				(1, "uint64 "+vtname+";"),
				(0, "" ),
				] )

			for (fname, vname, uname, flag)  in self.STATS:
				output.extend( [
				(1, "// Statistics "+uname ),
				(1, "uint64 "+vname+"[ WH ];"),
				(0, "" ),
				] )

			output.extend( [
				(1, "uint64 stats_last_adaptative_filter_rejected;"),
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
	def gen_getBestDepthHeartbeat_function( self, only_signature=False ):

		output = [ 
			(0, "uint64 getBestDepthHeartbeat("),
			(1, "voidp b,"),
			(1, "uint64 index"),
			]

		if only_signature:
			output.extend( [ (1, ');'), ])
			return output

		output.extend( [
			(1, ") {"),
			(2, 'return ((p_blackwood)b)->best_depth_seen_heartbeat[index];' ),
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
			output.append( (1 , "b->spaces_master_index["+str(space)+"] = b->master_index_"+self.puzzle.scenario.get_index_piece_name(space=space)+";") )

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
	def gen_save_best_depth_seen_function( self, only_signature=False ):

		output = [] 
		for k in self.DEPTH_COLORS.keys():
			output.extend( [ 
				(0, "void save_best_depth_seen_"+str(k)+"("),
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
			(1, 'for(i=0;i<WH;i++) cb->best_depth_seen_heartbeat[i] = 0;' ),
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
				output.append( (2, 'if (cb->best_depth_seen < '+d+') {') )
				output.append( (3, 'cb->best_depth_seen = '+d+';') )
				output.append( (3, 'cb->best_depth_seen_heartbeat['+d+'] = cb->heartbeat;') )
				if self.DEBUG > 0:
					output.append( (3, 'for(i=0;i<WH;i++) cb->board[i] = board[i];') )
				output.append( (2, '}' ))

			if depth >= self.puzzle.scenario.depth_first_notification:
				output.append( (2, 'if (cb->best_depth_seen < '+d+') {' if depth < WH else '') )
				output.append( (3, 'cb->best_depth_seen = '+d+';') )
				output.append( (3, 'cb->best_depth_seen_heartbeat['+d+'] = cb->heartbeat;' if depth < WH else '') )
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

			output.append( (2, 'cb->stats_nodes_count['+sspace+'] ++;' if self.puzzle.scenario.STATS > 0 else "") )
			output.append( (2, 'cb->stats_total_nodes_count ++;' if self.puzzle.scenario.PERF > 0 else "") )
			output.append( (2, '' ), )

			output.append( (2, 'cb->nodes_heartbeat['+d+'] = cb->heartbeat;' if (self.DEBUG > 0) or (depth < (WH//2)) else "") )
			if self.puzzle.scenario.use_adaptative_filter_depth and depth < (WH//2):
				output.append( (2, "// if we backtrack further than the current adaptative_filter_depth, we reset" ) )
				output.append( (2, "if (cb->adaptative_filter_depth > "+d+") {") )
				output.append( (3, 'cb->adaptative_filter_depth = WH;'), )
				output.append( (3, 'cb->stats_adaptative_filter_count['+sspace+'] ++;' if self.puzzle.scenario.STATS > 0 else "") )
				output.append( (3, 'cb->stats_total_adaptative_filter_count ++;' if self.puzzle.scenario.PERF > 0 else "") )
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
					output.append( (3, 'cb->stats_adaptative_filter_count['+sspace+'] ++;' if self.puzzle.scenario.STATS > 0 else "") )
					output.append( (3, 'cb->stats_total_adaptative_filter_count ++;' if self.puzzle.scenario.PERF > 0 else "") )
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
				output.append( (4, 'if (cb->best_depth_seen == 0) for(i=0;i<WH;i++) cb->board[i] = board[i];') )
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
			index_piece_name = self.puzzle.scenario.get_index_piece_name(depth=depth)
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
			
			output.append( (3, 'cb->stats_pieces_tried_count['+sspace+'] ++;' if self.puzzle.scenario.STATS > 0 else "") )
			output.append( (3, 'cb->stats_total_pieces_tried_count ++;' if self.puzzle.scenario.PERF > 0 else "") )
			
			output.append( (3, "current_piece = *(piece_to_try_next["+d+"]);" ))
			output.append( (3, "piece_to_try_next["+d+"] ++;"))
			#output.append( (3, 'DEBUG_PRINT(("'+" " * depth+' Trying piece : %d\\n", current_piece.info.p))' ))
			if depth > 0:
				for i in range(5):
					if sum(self.puzzle.scenario.heuristic_patterns_count[i][depth:]) > 0:
						output.append( (3, "local_cumulative_heuristic_patterns_count_"+str(i)+" = cumulative_heuristic_patterns_count_"+str(i)+"["+d+"-1] + current_piece.info.heuristic_patterns_"+str(i)+";"))
						if self.puzzle.scenario.heuristic_patterns_count[i][depth] > 0: 
							output.append( (3, "if (local_cumulative_heuristic_patterns_count_"+str(i)+" < "+str(self.puzzle.scenario.heuristic_patterns_count[i][depth])+" ) { "))
							output.append( (4, "cb->stats_heuristic_patterns_break_count[ "+sspace+"]++; " if self.puzzle.scenario.STATS > 0 else "" ))
							output.append( (4, "cb->stats_total_heuristic_patterns_break_count ++; " if self.puzzle.scenario.PERF > 0 else "" ))
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
						output.append( (4, "cb->stats_heuristic_conflicts_break_count[ "+sspace+"]++; " if self.puzzle.scenario.STATS > 0 else "" ))
						output.append( (4, "cb->stats_total_heuristic_conflicts_break_count ++; " if self.puzzle.scenario.PERF > 0 else "" ))
						output.append( (4, "break;" ))
						output.append( (3, "} // "+str(conflicts_allowed)))
			
			output.append( (3, "if (pieces_used[ current_piece.info.p ] != 0) {"))
			output.append( (4, 'cb->stats_pieces_used_count['+sspace+'] ++;' if self.puzzle.scenario.STATS > 0 else "") )
			output.append( (4, 'cb->stats_total_pieces_used_count ++;' if self.puzzle.scenario.PERF > 0 else "") )
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

		#if self.puzzle.scenario.STATS > 0 or self.puzzle.scenario.PERF > 0:
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



	# ----- Generate Funky functions
	def gen_registers( self, pushpop, with_rax=True, xmm_reg="rax", indent=3):

		output = []
		registers = [ "rax", "rbx", "rcx", "rdx", "rsi", "rdi", "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15" ]
		xmmregisters = [ "xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7", "xmm8", "xmm9", "xmm10", "xmm11", "xmm12", "xmm13", "xmm14", "xmm15" ]

		start = 0
		if not with_rax:
			start = 1

		if pushpop == "push":
			for r in registers[start:]:
				output.append( (indent, pushpop+" "+r ))
			for r in xmmregisters:
				output.append( (indent, "movq "+xmm_reg+", "+r ))
				output.append( (indent, pushpop+" "+xmm_reg ))
		elif pushpop == "pop":
			for r in reversed(xmmregisters):
				output.append( (indent, pushpop+" "+xmm_reg ))
				output.append( (indent, "movq "+r+", "+xmm_reg ))
			for r in reversed(registers[start:]):
				output.append( (indent, pushpop+" "+r ))

		return output


	# ----- Generate Funky functions
	def gen_solve_funky_functions( self, only_signature=False):

		insert_into_board = False

		W=self.puzzle.board_w
		H=self.puzzle.board_h
		WH=self.puzzle.board_wh

		output = []

		# https://renenyffenegger.ch/notes/development/languages/assembler/x86/registers/index
		# rax tmp
		# rbx tmp
		#  cl heuristic patterns  count
		#  ch heuristic conflicts count
		#  dl best_depth_seen
		#  dh heuristic for current depth
		# rsi board[WH]
		# rdi 
		# r8  pieces_used[0]
		# r9  pieces_used[1] 
		# r10 pieces_used[2] 
		# r11 pieces_used[3]
		# r12 patterns_down[0-7]
		# r13 patterns_down[8-15]
		# r14 first_function address 
		# r15 &(cf->check_commands)
		# xmm0 0
		# xmm1 1
		# xmm2 stats_total_nodes_count
		# xmm3 stats_pieces_tried_count
		# xmm4 stats_total_heuristic_patterns_break_count 
		# xmm5 stats_total_heuristic_conflicts_break_count
		# xmm6 stats_pieces_used_count 
		# xmm7 &(cf->stats_total_nodes_count)
		# xmm8
		# xmm9
		# xmm10
		# xmm11
		# xmm12
		# xmm13
		# xmm14
		# xmm15 cf->


		
		MARP = []
		tmp = sorted(self.puzzle.master_all_rotated_pieces.keys())
		for t in tmp:
			MARP.append(self.puzzle.master_all_rotated_pieces[t])
		
		"""
		
		rpl_lists = []
		for (index_piece_name, array) in self.puzzle.master_index.items():
			for index in array:
				if index == None:
					continue

				rpl = []
				i = index
				while i != None and self.puzzle.master_lists_of_rotated_pieces[i] != None:
					rpi = self.puzzle.master_lists_of_rotated_pieces[i]
					rpl.append( MARP[rpi] )
					i += 1

				rpl_lists.append( (index, rpl) )
				#print( (index, rpl) )
					
				#index = self.puzzle.master_index[index_piece_name][ ref ]
		exit()



		for (index, rpl) in rpl_lists:
			for patterns_down_reg in [ "r12", "r13" ]:
			funk_name = "try_pieces_list_with_"+pattern_down_reg+"_"+format(index, "05")

			if only_signature:
				# Signature for .h file
				output.append( (0, "void "+funk_name+"();") )
				continue

			output.extend( [
				(0, ".globl  "+funk_name ),
				(0, ".type   "+funk_name+", @function"),
				(0, funk_name+":"),
				(0, ".cfi_startproc"),
				(0, "# PARAMETERS: RDI = base address for calling next step"),
				] )

			# No piece? => function is empty
			if len(rpl) == 0:
				print("ERROR RPL")
				exit()

			#output.append( (2, 'cf->stats_nodes_count['+sspace[""]+'] ++;' if self.puzzle.scenario.STATS > 0 else "") )
			output.append( (2, 'paddq xmm2, xmm1 # cf->stats_total_nodes_count ++;' if self.puzzle.scenario.PERF > 0 else "") )

			# The piece scoring ensure pieces are sorted by conflict, then by pattern
			# We only check heuristic patterns when the piece doesn't contribute
			heuristic_patterns_already_checked_once = False
			heuristic_conflicts_already_checked_once = False
			piece_index = 0
			for rp in rpl:
				output.append( (2, "# "+ str(rp) ) )

				if heuristic_patterns and not heuristic_patterns_already_checked_once:
					if (rp.heuristic_patterns_count[0] == 0):
						output.append( (2, "# if (cf->cumulative_heuristic_patterns_count < "+str(self.puzzle.scenario.heuristic_patterns_count[0][depth])+" ) { "))
						output.append( (2, "cmp cl, dh # "+str(self.puzzle.scenario.heuristic_patterns_count[0][depth])+" #  Heuristic patterns count"))
						output.append( (2, "jae "+funk_name+"__heuristic_patterns_ok"))
						#output.append( (3, "cf->stats_heuristic_patterns_break_count[ "+sspace[""]+" ]++; " if self.puzzle.scenario.STATS > 0 else "" ))
						output.append( (3, "paddq xmm4, xmm1 # cf->stats_total_heuristic_patterns_break_count ++; " if self.puzzle.scenario.PERF > 0 else "" ))
						output.append( (3, "ret" ))
						output.append( (2, funk_name+"__heuristic_patterns_ok:"))

						heuristic_patterns_already_checked_once = True

				if heuristic_conflicts and not heuristic_conflicts_already_checked_once:
					conflicts_allowed = self.puzzle.scenario.heuristic_conflicts_count[space[""]]
					if self.puzzle.scenario.heuristic_conflicts_count[space["previous"]] != conflicts_allowed:
						# if there is an increment in the heuristic, no need to test, it will always pass the test
						pass
					else:
						output.append( (2, "# if (cf->cumulative_heuristic_conflicts_count > "+str(conflicts_allowed)+" ) { "))
						output.append( (2, "cmp ch, dh # "+str(conflicts_allowed)+" #  Heuristic conflicts count"))
						output.append( (2, "jae "+funk_name+"__heuristic_conflicts_ok"))
						#output.append( (3, "cf->stats_heuristic_patterns_break_count[ "+sspace[""]+" ]++; " if self.puzzle.scenario.STATS > 0 else "" ))
						output.append( (3, "paddq xmm5, xmm1 # cf->stats_total_heuristic_conflicts_break_count ++; " if self.puzzle.scenario.PERF > 0 else "" ))
						output.append( (3, "ret" ))
						output.append( (2, funk_name+"__heuristic_conflicts_ok:"))

						heuristic_conflicts_already_checked_once = True


				mask_index = rp.p // 64
				mask_reg = "r"+str(8+mask_index)
				output.append( (2, 'paddq xmm3, xmm1 # cf->stats_total_pieces_tried_count ++;' if self.puzzle.scenario.PERF > 0 else "") )
				output.append( (2, "# Test if the piece is already in use" ))
				output.append( (2, "bt "+mask_reg+", "+str(rp.masks_bit_index[mask_index]) ))
				output.append( (2, "jc "+funk_name+"__skip_piece_"+str(piece_index) ))
				output.append( (3, "bts "+mask_reg+", "+str(rp.masks_bit_index[mask_index]) ))
				
				output.append( (3, "# Store the piece in the board[WH]" ))
				output.append( (3, "mov dword ptr [rsi + "+sspace[""]+"*4 ], 0x"+"{:02X}".format(rp.l)+"{:02X}".format(rp.d)+"{:02X}".format(rp.r)+"{:02X}".format(rp.u) ))
				#output.append( (3, "mov dword ptr [rsi + "+sspace[""]+"*4 ], 0x01020304" ))
				
				if depth != WH-1:
					output.append( (3, "# cf->patterns_down[ "+x[""]+"] = "+str(rp.d)+";" ))
					#output.append( (3, "ror "+patterns_down_reg[""]+", "+patterns_down_rotate[""] ) )
					output.append( (3, "movb "+patterns_down_reg[""]+"b, "+str(rp.d) ) )
					#output.append( (3, "rol "+patterns_down_reg[""]+", "+patterns_down_rotate[""] ) )

					output.append( (3, "inc cl # cf->cumulative_heuristic_patterns_count ++;" if heuristic_patterns and rp.heuristic_patterns_count[0] > 0 else "" ))
					output.append( (3, "inc cl # cf->cumulative_heuristic_patterns_count ++;" if heuristic_patterns and rp.heuristic_patterns_count[0] > 1 else "" ))
					output.append( (3, "inc ch # cf->cumulative_heuristic_conflicts_count ++;" if rp.conflicts_count > 0 else "" ))

					output.append( (3, "# Call the next function by calculating its address" ))
					output.append( (3, "movq rbx, "+patterns_down_reg["next"] ) )
					output.append( (3, "ror rbx, "+patterns_down_rotate["next"] ) )
					output.append( (3, "movzx rax, bl" ) )
					output.append( (3, "shl  ax, "+str(self.EDGE_SHIFT_LEFT) ))
					output.append( (3, "add  ax, "+str(rp.l) ))
					output.append( (3, "shl  eax, "+str(align_shift["next"]) ))
					# We should be doing the following call, but the linker doesn't get the right value for the function address
					#output.append( (3, "call [ "+funk_name_next+"@PLT + rax ]" if depth < 1 else "")) 
					# So we have to calculate it ourselves
					output.append( (3, "add rax, "+funk_name_next+"-"+first_funk_name))
					output.append( (3, "add rax, r14"))
					output.append( (3, "call rax" ))

					output.append( (3, "dec ch # cf->cumulative_heuristic_conflicts_count --;" if rp.conflicts_count > 0 else "" ))
					output.append( (3, "dec cl # cf->cumulative_heuristic_patterns_count --;" if heuristic_patterns and rp.heuristic_patterns_count[0] > 0 else "" ))
					output.append( (3, "dec cl # cf->cumulative_heuristic_patterns_count --;" if heuristic_patterns and rp.heuristic_patterns_count[0] > 1 else "" ))
				else:
					output.extend( self.gen_registers("push") )
					output.append( (3, "# rdi pointing to cf->" ))
					output.append( (3, "movq rdi, xmm15" ))
					output.append( (3, "# rsi is already pointing to board[WH]" ))
					output.append( (3, "call [ "+funk_name_next+"@PLT ]" ))
					output.extend( self.gen_registers("pop") )

				output.append( (3, "btr "+mask_reg+", "+str(rp.masks_bit_index[mask_index]) ))

				output.append( (2, "jmp "+funk_name+"__end_piece_"+str(piece_index) if self.puzzle.scenario.PERF > 0 else "" ))
				#output.append( (2, "} else {" if self.puzzle.scenario.STATS + self.puzzle.scenario.PERF > 0 else ""))
				output.append( (2, funk_name+"__skip_piece_"+str(piece_index)+":" ))
				#output.append( (3, 'cf->stats_pieces_used_count['+sspace[""]+'] ++;' if self.puzzle.scenario.STATS > 0 else "") )
				output.append( (3, 'paddq xmm6, xmm1  # cf->stats_total_pieces_used_count ++;' if self.puzzle.scenario.PERF > 0 else "") )
				output.append( (2, funk_name+"__end_piece_"+str(piece_index)+":" ))

				piece_index += 1


			# Restore the previous patterns_down
			output.append( (2, "# cf->patterns_down[ "+x[""]+"] = "+str(ref_up)+";" ))
			output.append( (2, "ror "+patterns_down_reg[""]+", "+patterns_down_rotate[""] ) )
			output.append( (2, "movb "+patterns_down_reg[""]+"b, "+str(ref_up) ) )
			output.append( (2, "rol "+patterns_down_reg[""]+", "+patterns_down_rotate[""] ) )

			output.append( (2, funk_name+"__end:" ))
			output.append( (2, "ret") )
			output.append( (0, ".cfi_endproc") )
			output.append( (0, ".size "+funk_name+", .-"+funk_name ))
			output.append( (0, ".align "+str(1 << align_shift[""]) ))





		"""





























		# Get the lists for each space and each references
		rpl_lists_space = []
		for depth in range(WH):
			space = self.puzzle.scenario.spaces_sequence[ depth ]
			rpl_lists = {}
			for ref_up, ref_right in itertools.product(self.puzzle.colors, self.puzzle.colors):
				index_piece_name = self.puzzle.scenario.get_index_piece_name(space=space)
				ref = (ref_up << self.EDGE_SHIFT_LEFT) | ref_right
				index = self.puzzle.master_index[index_piece_name][ ref ]

				rpl = []
				while index != None and self.puzzle.master_lists_of_rotated_pieces[index] != None:
					rpi = self.puzzle.master_lists_of_rotated_pieces[index]
					rpl.append( MARP[rpi] )
					index += 1

				rpl_lists[ format(ref_up,"02")+"_"+format(ref_right,"02") ] = rpl


			longest = 0
			for (key, rpl) in rpl_lists.items():
				if len(rpl) > longest:
					longest = len(rpl)
			rpl_lists_space.append( (rpl_lists, longest) )


		# Print the list longest
		for space in range(WH):
			(r, l) = rpl_lists_space[space]
			print(format(l, "2"), end=" ")
			if space % W == W-1:
				print()
		print()
		

		first_funk_name = None

		for depth in range(WH):
		#for depth in range(WH-W*2,WH-W):
			
			space = {}
			space[ "" ]         = self.puzzle.scenario.spaces_sequence[ depth   ]
			if depth > 0:
				space[ "previous" ] = self.puzzle.scenario.spaces_sequence[ depth-1 ]
			else:
				space[ "previous" ] = None
			if depth < WH-1:
				space[ "next" ]     = self.puzzle.scenario.spaces_sequence[ depth+1 ]
			else:
				space[ "next" ]     = None

			space[ "u" ]        = self.puzzle.static_space_up[ space[""] ]
			space[ "r" ]        = self.puzzle.static_space_right[ space[""] ]
			space[ "d" ]        = self.puzzle.static_space_down[ space[""] ]
			space[ "l" ]        = self.puzzle.static_space_left[ space[""] ]

			sspace = {}
			for k in space.keys():
				sspace[ k ] = str(space[ k ])

			x = {}
			for k in space.keys():
				if space[ k ] != None:
					x[ k ] = str(space[ k ] % W)
			
			# List of pieces and alignment required
			rpl_lists = {}
			longest = {}
			align_shift = {}
			for k in space.keys():
				if space[ k ] != None:
					(rpl_lists[k], longest[k]) = rpl_lists_space[ space[k] ]

					if longest[k] in [ 1, 2 ]:
						align_shift[k] = 8
					elif longest[k] in [ 3, 4, 5 ]:
						align_shift[k] = 9
					elif longest[k] in [ 6, 7, 8, 9, 10, 11 ]:
						align_shift[k] = 10
					elif longest[k] in [ 12 ]:
						align_shift[k] = 11
					elif longest[k] in [ 96 ]:
						align_shift[k] = 13
					else:
						align_shift[k] = 14


			# Storing the patterns_down into 2x 64bits reg
			patterns_down_reg = {}
			#patterns_down_rotate = {}
			for k in space.keys():
				if space[ k ] != None:
					if int(x[k]) in [0,1,2,3,4,5,6,7]:
						patterns_down_reg[k] = "r12"
						#patterns_down_rotate[k] = str(int(x[k])*8)
					elif int(x[k]) in [8,9,10,11,12,13,14,15]:
						patterns_down_reg[k] = "r13"
						#patterns_down_rotate[k] = str((int(x[k])-8)*8)
				


			heuristic_patterns  = heuristic_conflicts = False

			heuristic_patterns  = self.puzzle.scenario.heuristic_patterns_count[0][depth] > 0
			if sum(self.puzzle.scenario.heuristic_conflicts_count) > 0:
				heuristic_conflicts = self.puzzle.scenario.heuristic_conflicts_count[depth] > 0

			#output.append((0, "# ---------------------------------------------------------------------" ))
			#output.append((0, "# patterns:"+str(self.puzzle.scenario.heuristic_patterns_count[0][depth])+"  conflicts:"+str(self.puzzle.scenario.heuristic_conflicts_count[depth]) ))

			# Get all the possible sides around the current space
			Side = {}
			for d in [ "u", "r", "d", "l" ]:
				Side[ d ] = []
				if space[d] == None:
					Side[d] = [ 0 ]
				else:
					Side[d] = self.puzzle.colors_center
					if self.puzzle.static_spaces_type[ space[d] ] in [ "corner", "border" ]:
						if self.puzzle.static_spaces_type[ space[""] ] in [ "corner", "border" ]:
							Side[d] = self.puzzle.colors_border_no_edge
					
			#print(space[""], Side)


			for_ref = self.puzzle.scenario.spaces_references[ space[""] ]
			"""
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
			"""


			#for ref_up, ref_right in itertools.product(Side["d"], Side["l"]):
			#for ref_up, ref_right in itertools.product(self.puzzle.colors, self.puzzle.colors):
			for ref_right, ref_up in itertools.product(range(32), range(32)):

				if depth != WH-1:
					funk_name_next = "solve_funky_space_"+format(space["next"], "03")+"_ref_up_"+format(0,"02")+"_ref_right_"+format(0,"02")
				else:
					funk_name_next = "solve_funky_we_have_a_solution_c"
				funk_name = "solve_funky_space_"+format(space[""], "03")+"_ref_up_"+format(ref_up,"02")+"_ref_right_"+format(ref_right,"02")
				if first_funk_name == None:
					first_funk_name = funk_name

				if only_signature:
					# Signature for .h file
					output.append( (0, "void "+funk_name+"();") )
					continue

				output.extend( [
					(0, ".globl  "+funk_name ),
					(0, ".type   "+funk_name+", @function"),
					(0, funk_name+":"),
					(0, ".cfi_startproc"),
					] )

				rpl = []
				if format(ref_up,"02")+"_"+format(ref_right,"02") in rpl_lists[""].keys():
					rpl = rpl_lists[""][ format(ref_up,"02")+"_"+format(ref_right,"02") ]

				# No piece? => function is empty
				if len(rpl) == 0:
					output.append( (2, "ret") )
					output.append( (0, ".cfi_endproc") )
					output.append( (0, ".size "+funk_name+", .-"+funk_name ))
					output.append( (0, ".align "+str(1 << align_shift[""]) ))
					continue

				if depth > 35:
					output.append( (2, "mov rbx, 0x"+"{:02X}".format(depth)+"{:02X}".format(space[""])+"{:02X}".format(ref_up)+"{:02X}".format(ref_right) if self.DEBUG > 0 else "" ))
					output.append( (2, "call solve_funky_trace@PLT" if self.DEBUG > 0 else "" ))

				if ((self.DEBUG > 0 and depth > WH//2) or (depth > self.puzzle.scenario.depth_first_notification-7)) and depth < self.puzzle.scenario.depth_first_notification:
					output.append( (2, "cmp dl, "+str(depth) ) )
					output.append( (2, "ja "+funk_name+"__end") )
					#output.append( (2, "jae "+funk_name+"__end") )
					output.append( (2, "mov dl, "+str(depth)) )
					output.append( (2, "call solve_funky_best_depth_seen@PLT") )
					output.append( (2, "mov rbx, 0x"+"{:02X}".format(depth)+"{:02X}".format(space[""])+"{:02X}".format(ref_up)+"{:02X}".format(ref_right) if self.DEBUG > 0 else "" ))
					output.append( (2, "call solve_funky_trace@PLT" if self.DEBUG > 0 else "" ))
					output.append( (2, funk_name+"__not_best_depth_seen:"))

				if depth in (range(0, WH, W*4) if self.DEBUG == 0 else range(0, WH, W*2)):
				#if depth in (range(0, WH, W*4) if self.DEBUG == 0 else range(0, WH)):
					output.append( (2, "call solve_funky_check_commands@PLT") )
					output.append( (2, "bt rax, 0  # We set the carry if TTF") )
					output.append( (2, "jc "+funk_name+"__end # TTF") )

				#output.append( (2, 'cf->stats_nodes_count['+sspace[""]+'] ++;' if self.puzzle.scenario.STATS > 0 else "") )
				output.append( (2, 'paddq xmm2, xmm1 # cf->stats_total_nodes_count ++;' if self.puzzle.scenario.PERF > 0 else "") )

				# The piece scoring ensure pieces are sorted by conflict, then by pattern
				# We only check heuristic patterns when the piece doesn't contribute
				heuristic_patterns_already_checked_once = False
				heuristic_conflicts_already_checked_once = False
				piece_index = 0
				for rp in rpl:
					output.append( (2, "#-------[ Try piece "+str(piece_index)+" ]-----------------" ) )
					output.append( (2, funk_name+"__piece_"+str(piece_index)+":" ))
					output.append( (2, "# "+ str(rp) ) )

					if heuristic_patterns and not heuristic_patterns_already_checked_once:
						if (rp.heuristic_patterns_count[0] == 0):
							output.append( (2, "# if (cf->cumulative_heuristic_patterns_count < "+str(self.puzzle.scenario.heuristic_patterns_count[0][depth])+" ) { "))
							output.append( (2, "cmp cl, "+str(self.puzzle.scenario.heuristic_patterns_count[0][depth])+" #  Heuristic patterns count"))
							output.append( (2, "jae "+funk_name+"__heuristic_patterns_ok"))
							#output.append( (3, "cf->stats_heuristic_patterns_break_count[ "+sspace[""]+" ]++; " if self.puzzle.scenario.STATS > 0 else "" ))
							output.append( (3, "paddq xmm4, xmm1 # cf->stats_total_heuristic_patterns_break_count ++; " if self.puzzle.scenario.PERF > 0 else "" ))
							output.append( (3, "# cf->patterns_down[ "+x[""]+"] = "+str(ref_up)+";" ) )
							#output.append( (3, "ror "+patterns_down_reg[""]+", "+patterns_down_rotate[""] ) )
							output.append( (3, "movb "+patterns_down_reg[""]+"b, "+str(ref_up) ) )
							#output.append( (3, "rol "+patterns_down_reg[""]+", "+patterns_down_rotate[""] ) )
							output.append( (3, "ret" ))
							output.append( (2, funk_name+"__heuristic_patterns_ok:"))

							heuristic_patterns_already_checked_once = True

					if heuristic_conflicts and not heuristic_conflicts_already_checked_once:
						conflicts_allowed = self.puzzle.scenario.heuristic_conflicts_count[space[""]]
						if self.puzzle.scenario.heuristic_conflicts_count[space["previous"]] != conflicts_allowed:
							# if there is an increment in the heuristic, no need to test, it will always pass the test
							pass
						else:
							output.append( (2, "# if (cf->cumulative_heuristic_conflicts_count > "+str(conflicts_allowed)+" ) { "))
							output.append( (2, "cmp ch, "+str(conflicts_allowed)+" #  Heuristic conflicts count"))
							output.append( (2, "jae "+funk_name+"__heuristic_conflicts_ok"))
							#output.append( (3, "cf->stats_heuristic_patterns_break_count[ "+sspace[""]+" ]++; " if self.puzzle.scenario.STATS > 0 else "" ))
							output.append( (3, "paddq xmm5, xmm1 # cf->stats_total_heuristic_conflicts_break_count ++; " if self.puzzle.scenario.PERF > 0 else "" ))
							output.append( (3, "# cf->patterns_down[ "+x[""]+"] = "+str(ref_up)+";" ) )
							#output.append( (3, "ror "+patterns_down_reg[""]+", "+patterns_down_rotate[""] ) )
							output.append( (3, "movb "+patterns_down_reg[""]+"b, "+str(ref_up) ) )
							#output.append( (3, "rol "+patterns_down_reg[""]+", "+patterns_down_rotate[""] ) )
							output.append( (3, "ret" ))
							output.append( (2, funk_name+"__heuristic_conflicts_ok:"))

							heuristic_conflicts_already_checked_once = True


					mask_index = rp.p // 64
					mask_reg = "r"+str(8+mask_index)
					#mask_reg += "w" if rp.masks_bit_index[mask_index] in range(0,16) else ""
					#mask_reg += "d" if rp.masks_bit_index[mask_index] in range(16,32) else ""
					output.append( (2, 'paddq xmm3, xmm1 # cf->stats_total_pieces_tried_count ++;' if self.puzzle.scenario.PERF > 0 else "") )
					output.append( (2, "# Test if the piece is already in use" ))
					output.append( (2, "bt "+mask_reg+", "+str(rp.masks_bit_index[mask_index]) ))
					output.append( (2, "jc "+funk_name+"__skip_piece_"+str(piece_index) ))
					output.append( (3, "bts "+mask_reg+", "+str(rp.masks_bit_index[mask_index]) ))
					
					if insert_into_board:
						output.append( (3, "# Store the piece in the board[WH]" ))
						output.append( (3, "mov dword ptr [rsi + "+sspace[""]+"*4 ], 0x"+"{:02X}".format(rp.l)+"{:02X}".format(rp.d)+"{:02X}".format(rp.r)+"{:02X}".format(rp.u) ))
					
					if depth != WH-1:
						output.append( (3, "# cf->patterns_down[ "+x[""]+"] = "+str(rp.d)+";" ))
						#output.append( (3, "ror "+patterns_down_reg[""]+", "+patterns_down_rotate[""] ) )
						output.append( (3, "movb "+patterns_down_reg[""]+"b, "+str(rp.d) ) )
						#output.append( (3, "rol "+patterns_down_reg[""]+", "+patterns_down_rotate[""] ) )

						output.append( (3, "inc cl # cf->cumulative_heuristic_patterns_count ++;" if heuristic_patterns and rp.heuristic_patterns_count[0] > 0 else "" ))
						output.append( (3, "inc cl # cf->cumulative_heuristic_patterns_count ++;" if heuristic_patterns and rp.heuristic_patterns_count[0] > 1 else "" ))
						output.append( (3, "inc ch # cf->cumulative_heuristic_conflicts_count ++;" if rp.conflicts_count > 0 else "" ))

						output.append( (3, "# Call the next function by calculating its address" ))
						output.append( (3, "ror "+patterns_down_reg["next"]+", 8" ) )
						#output.append( (3, "movq rbx, "+patterns_down_reg["next"]+"b" ) )
						#output.append( (3, "ror rbx, "+patterns_down_rotate["next"] ) )
						output.append( (3, "movzx rax, "+patterns_down_reg["next"]+"b" ) )
						output.append( (3, "shl  eax, "+str(align_shift["next"]) ))
						#output.append( (3, "shl  ax, "+str(self.EDGE_SHIFT_LEFT) ))
						output.append( (3, "or   eax, (("+str(rp.l)+" * "+str(1 << self.EDGE_SHIFT_LEFT)+") << "+str(align_shift["next"])+") + " + funk_name_next+"-"+first_funk_name))
						# We should be doing the following call, but the linker doesn't get the right value for the function address
						#output.append( (3, "call [ "+funk_name_next+"@PLT + rax ]" if depth < 1 else "")) 
						# So we have to calculate it ourselves
						#output.append( (3, "add rax, "+funk_name_next+"-"+first_funk_name))
						output.append( (3, "add rax, r14"))
						output.append( (3, "call rax" ))
						output.append( (3, "rol "+patterns_down_reg["next"]+", 8" ) )

						output.append( (3, "dec ch # cf->cumulative_heuristic_conflicts_count --;" if rp.conflicts_count > 0 else "" ))
						output.append( (3, "dec cl # cf->cumulative_heuristic_patterns_count --;" if heuristic_patterns and rp.heuristic_patterns_count[0] > 0 else "" ))
						output.append( (3, "dec cl # cf->cumulative_heuristic_patterns_count --;" if heuristic_patterns and rp.heuristic_patterns_count[0] > 1 else "" ))
					else:
						output.extend( self.gen_registers("push") )
						output.append( (3, "# rdi pointing to cf->" ))
						output.append( (3, "movq rdi, xmm15" ))
						output.append( (3, "# rsi is already pointing to board[WH]" ))
						output.append( (3, "call [ "+funk_name_next+"@PLT ]" ))
						output.extend( self.gen_registers("pop") )

					output.append( (3, "btr "+mask_reg+", "+str(rp.masks_bit_index[mask_index]) ))

					output.append( (2, "jmp "+funk_name+"__end_piece_"+str(piece_index) if self.puzzle.scenario.PERF > 0 else "" ))
					#output.append( (2, "} else {" if self.puzzle.scenario.STATS + self.puzzle.scenario.PERF > 0 else ""))
					output.append( (2, funk_name+"__skip_piece_"+str(piece_index)+":" ))
					#output.append( (3, 'cf->stats_pieces_used_count['+sspace[""]+'] ++;' if self.puzzle.scenario.STATS > 0 else "") )
					output.append( (3, 'paddq xmm6, xmm1  # cf->stats_total_pieces_used_count ++;' if self.puzzle.scenario.PERF > 0 else "") )
					output.append( (2, funk_name+"__end_piece_"+str(piece_index)+":" ))

					piece_index += 1


				# Restore the previous patterns_down
				output.append( (2, "# cf->patterns_down[ "+x[""]+"] = "+str(ref_up)+";" ))
				#output.append( (2, "ror "+patterns_down_reg[""]+", "+patterns_down_rotate[""] ) )
				output.append( (2, "movb "+patterns_down_reg[""]+"b, "+str(ref_up) ) )
				#output.append( (2, "rol "+patterns_down_reg[""]+", "+patterns_down_rotate[""] ) )

				output.append( (2, funk_name+"__end:" ))
				output.append( (2, "ret") )
				output.append( (0, ".cfi_endproc") )
				output.append( (0, ".size "+funk_name+", .-"+funk_name ))
				output.append( (0, ".align "+str(1 << align_shift[""]) ))


		# Solve_Funk_Check_Command
		funk_name = "solve_funky_check_commands"
		if only_signature:
			# Signature for .h file
			output.append( (0, "void "+funk_name+"();") )
		else:

			output.extend( [
				(0, ".globl  "+funk_name ),
				(0, ".type   "+funk_name+", @function"),
				(0, funk_name+":"),
				(0, ".cfi_startproc"),
				] )
			output.extend( [
				(2, "btq [r15], 0"),
				(2, "jnc "+funk_name+"_end"),
				] )
			output.extend( self.gen_registers("push", with_rax=False, xmm_reg="rbx") )
			output.append( (3, "# rdi pointing to cf->" ))
			output.append( (3, "movq rdi, xmm15" ))
			output.append( (3, "# rsi is already pointing to board[WH]" ))
			output.append( (3, "# Save statistics" ))
			output.append( (3, "movq rax, xmm7" ))
			output.append( (3, "movq rbx, xmm2" ))
			output.append( (3, "mov [rax +  0], rbx" ))
			output.append( (3, "movq rbx, xmm3" ))
			output.append( (3, "mov [rax +  8], rbx" ))
			output.append( (3, "movq rbx, xmm4" ))
			output.append( (3, "mov [rax + 16], rbx" ))
			output.append( (3, "movq rbx, xmm5" ))
			output.append( (3, "mov [rax + 24], rbx" ))
			output.append( (3, "movq rbx, xmm6" ))
			output.append( (3, "mov [rax + 32], rbx" ))
			output.append( (3, "call solve_funky_check_commands_c@PLT" ))
			output.append( (3, "# rax = Time To Finish" ))
			#output.append( (3, "bt rax, 0  # We set the carry if TTF") )
			output.extend( self.gen_registers("pop", with_rax=False, xmm_reg="rbx") )

			output.extend( [
				(2, funk_name+"_end:"),
				(2, "ret"),
				(0, ".cfi_endproc"),
				(0, ".size solve"+funk_name+", .-"+funk_name ),
				] )

		# Solve_Funk_Best_Depth_Seen
		funk_name = "solve_funky_best_depth_seen"
		if only_signature:
			# Signature for .h file
			output.append( (0, "void "+funk_name+"();") )
		else:

			output.extend( [
				(0, ".globl  "+funk_name ),
				(0, ".type   "+funk_name+", @function"),
				(0, funk_name+":"),
				(0, ".cfi_startproc"),
				] )
			output.extend( self.gen_registers("push") )

			output.append( (3, "# rdi pointing to cf->" ))
			output.append( (3, "movq rdi, xmm15" ))
			output.append( (3, "# rsi is already pointing to board[WH]" ))
			output.append( (3, "# rdx's dl is already best_depth_seen" ))
			output.append( (3, "and rdx, 0xff" ))
			output.append( (3, "call solve_funky_best_depth_seen_c@PLT" ))

			output.extend( self.gen_registers("pop") )
			output.extend( [
				(2, funk_name+"_end:"),
				(2, "ret"),
				(0, ".cfi_endproc"),
				(0, ".size solve"+funk_name+", .-"+funk_name ),
				] )

		# Solve_Funk_Best_Depth_Seen
		funk_name = "solve_funky_bootstrap"
		if only_signature:
			# Signature for .h file
			output.append( (0, "void "+funk_name+"(") )
			output.append( (1, "p_blackwood cf,"), )
			output.append( (1, "t_piece board[WH],"), )
			output.append( (1, "uint64 * p_check_commands,"), )
			output.append( (1, "uint64 * p_stats"), )
			output.append( (1, ");"), )
		else:

			output.extend( [
				(0, ".globl  "+funk_name ),
				(0, ".type   "+funk_name+", @function"),
				(0, funk_name+":"),
				(0, ".cfi_startproc"),
				] )

			# Calling - https://www.agner.org/optimize/calling_conventions.pdf
			# First Argument  : RDI
			# Second Argument : RSI
			# Third Argument  : RDX
			# Fourth Argument : RCX
			# Fifth Argument  : R8
			# Sixth Argument  : R9

			output.append( (1, "mov rsi, rsi  # rsi board[WH]" ))
			output.append( (1, "mov r15, rdx  # &(cf->check_commands)" ))
			output.append( (1, "lea rax, [rip]  # First Function address because Linker is too stup^W weak" ))
			output.append( (1, "sub rax, .-"+first_funk_name+"" ))
			output.append( (1, "mov r14, rax" ))
			output.append( (1, "movq xmm7, rcx  # xmm7 &(cf->stats)" ))
			output.append( (1, "movq xmm8, rcx  # " ))
			output.append( (1, "movq xmm9, rcx  # " ))
			output.append( (1, "movq xmm10, rcx  # " ))
			output.append( (1, "movq xmm11, rcx  # " ))
			output.append( (1, "movq xmm12, rcx  # " ))
			output.append( (1, "movq xmm13, rcx  # " ))
			output.append( (1, "movq xmm14, rcx  # " ))
			output.append( (1, "movq xmm15, rdi  # xmm15 cf->" ))
			output.append( (1, "xor rdi, rdi  # rdi 0" ))

			output.append( (1, "xor rcx, rcx  #  cl heuristic patterns  count" ))
			output.append( (1, "xor rdx, rdx  #  dl best_depth_seen" ))
			output.append( (1, "xor r8, r8  # r8  pieces_used[0]" ))
			output.append( (1, "xor r9, r9  # r9  pieces_used[1] " ))
			output.append( (1, "xor r10, r10  # r10 pieces_used[2] " ))
			output.append( (1, "xor r11, r11  # r11 pieces_used[3]" ))
			output.append( (1, "xor r12, r12  # r12 patterns_down[0-7]" ))
			output.append( (1, "xor r13, r13  # r13 patterns_down[8-15]" ))
			output.append( (1, "pxor xmm0, xmm0  # xmm0 0" ))
			output.append( (1, "xor rax, rax" ))
			output.append( (1, "inc rax" ))
			output.append( (1, "pxor xmm1, xmm1  " ))
			output.append( (1, "movq xmm1, rax  # xmm1 1" ))
			output.append( (1, "pxor xmm2, xmm2  # xmm2 stats_total_nodes_count" ))
			output.append( (1, "pxor xmm3, xmm3  # xmm3 stats_pieces_tried_count" ))
			output.append( (1, "pxor xmm4, xmm4  # xmm4 stats_total_heuristic_patterns_break_count " ))
			output.append( (1, "pxor xmm5, xmm5  # xmm5 stats_total_heuristic_conflicts_break_count" ))
			output.append( (1, "pxor xmm6, xmm6  # xmm6 stats_pieces_used_count " ))
			output.append( (1, "xor rax, rax  # rax tmp" ))
			output.append( (1, "xor rbx, rbx  # rbx tmp" ))

			output.append( (1, "# Call the Bouzin" ))
			output.append( (1, "call "+first_funk_name+"@PLT" ))
			#output.append( (3, "call solve_funky_space_015_ref_up_00_ref_right_00@PLT" ))

			output.extend( [
				(1, funk_name+"_end:"),
				(1, "ret"),
				(0, ".cfi_endproc"),
				(0, ".size solve"+funk_name+", .-"+funk_name ),
				] )

		# Solve_Funk_trace
		funk_name = "solve_funky_trace"
		if only_signature:
			# Signature for .h file
			output.append( (0, "void "+funk_name+"();") )
		else:

			output.extend( [
				(0, ".globl  "+funk_name ),
				(0, ".type   "+funk_name+", @function"),
				(0, funk_name+":"),
				(0, ".cfi_startproc"),
				] )
			output.extend( self.gen_registers("push") )

			output.append( (3, "# rdi pointing to cf->" ))
			output.append( (3, "movq rdi, xmm15" ))
			output.append( (3, "mov rsi, rbx # The context" ))
			output.append( (3, "call solve_funky_trace_c@PLT" ))

			output.extend( self.gen_registers("pop") )
			output.extend( [
				(2, funk_name+"_end:"),
				(2, "ret"),
				(0, ".cfi_endproc"),
				(0, ".size solve"+funk_name+", .-"+funk_name ),
				] )


		return output

	# ----- Generate Funky functions
	def gen_solve_funky_bootstrap_c( self, only_signature=False):
		output = []

		output.extend( [ 
			(0, "int solve_funky_bootstrap_c("),
			(1, "p_blackwood cf"),
			] )

		if only_signature:
			output.append( (1, ');') )
			return output


		output.append( (1, ") {") )
		output.append( (1, "uint i;") )
		output.append( (0, '' ), )
		output.extend( [
			#(1, 'was_allocated = 0;' ),
			(1, 'if (cf == NULL) {' ),
			#(2, 'DEBUG_PRINT(("Allocating Memory\\n"));'), 
			(2, 'cf = (p_blackwood)allocate_blackwood();'), 
			#(2, 'was_allocated = 1;' ),
			(1, '}'), 
			(1, 'global_blackwood = cf;'), 
			(1, '' ),
			] )

		output.append( (1, "// Clear funky blackwood structure") )
		for (c, n, s) in self.FLAGS:
			if c == "Seed":
				continue
			output.append( (1, "cf->"+n+" = 0;") )

		output.extend( [
			(1, "cf->heartbeat = 1; // We start at 1 for the adaptative filter "),
			(1, "cf->heartbeat_limit = heartbeat_time_bonus[ 0 ];"),
			] )

		if self.DEBUG > 3:
 			output.extend( [
			(1, "cf->commands |= CLEAR_SCREEN;"),
			(1, "cf->commands |= SHOW_TITLE;"),
			(1, "cf->commands |= SHOW_SEED;"),
			(1, "cf->commands |= SHOW_HEARTBEAT;"),
			(1, "cf->commands |= SHOW_ADAPTATIVE_FILTER;"),
			(1, "cf->commands |= SHOW_STATS_NODES_COUNT;"),
			(1, "cf->commands |= ZERO_STATS_NODES_COUNT;"),
			(1, "cf->commands |= SHOW_STATS_PIECES_TRIED_COUNT;"),
			(1, "cf->commands |= ZERO_STATS_PIECES_TRIED_COUNT;"),
			#(1, "cf->commands |= SHOW_STATS_PIECES_USED_COUNT;"),
			#(1, "cf->commands |= ZERO_STATS_PIECES_USED_COUNT;"),
			#(1, "cf->commands |= SHOW_STATS_HEURISTIC_PATTERNS_BREAK_COUNT;"),
			#(1, "cf->commands |= ZERO_STATS_HEURISTIC_PATTERNS_BREAK_COUNT;"),
			#(1, "cf->commands |= SHOW_STATS_HEURISTIC_CONFLICTS_BREAK_COUNT;"),
			#(1, "cf->commands |= ZERO_STATS_HEURISTIC_CONFLICTS_BREAK_COUNT;"),
			(1, "cf->commands |= SHOW_STATS_ADAPTATIVE_FILTER_COUNT;"),
			(1, "cf->commands |= ZERO_STATS_ADAPTATIVE_FILTER_COUNT;"),
			#(1, "cf->commands |= SHOW_NODES_HEARTBEAT;"),
			#(1, "cf->commands |= ZERO_NODES_HEARTBEAT;"),
			(1, "cf->commands |= SHOW_MAX_DEPTH_SEEN;"),
			(1, "cf->commands |= SHOW_BEST_BOARD_URL;"),
			] )

		output.extend( [
			(1, 'for(i=0;i<WH;i++) cf->board[i].value = 0;' ),
			(1, 'for(i=0;i<WH;i++) { cf->board_pieces[i].u = 0;cf->board_pieces[i].r = 0;cf->board_pieces[i].d = 0;cf->board_pieces[i].l = 0; }' ),
			(1, 'for(i=0;i<WH;i++) cf->nodes_heartbeat[i] = 0;' ),
			(1, 'for(i=0;i<WH;i++) cf->best_depth_seen_heartbeat[i] = 0;' ),
			(2, ""),
			] )

		for (fname, vname, uname, flag)  in self.STATS:
			vtname = vname.replace("stats_", "stats_total_")
			output.extend( [
				(1, 'cf->'+vtname+" = 0;"),
				(1, 'for(i=0;i<WH;i++) cf->'+vname+'[i] = 0;' ),
				(0, "" ),
				] )


		output.append( (1, 'printf("Starting\\n");' ), )
		output.append( (1, 'solve_funky_bootstrap(' ), )
		output.append( (2, 'cf,' ), )
		output.append( (2, '&(cf->board_pieces[0]),' ), )
		output.append( (2, '&(cf->check_commands),' ), )
		output.append( (2, '&(cf->stats_total_nodes_count)' ), )
		output.append( (1, ');' ), )
		output.append( (0, '' ), )
		output.append( (1, 'return 0;' ), )
		output.append( (0, '}' ), )
		output.append( (0, '' ), )

		return output


	# ----- Generate Funky functions
	def gen_solve_funky_check_command_c( self, only_signature=False):
		output = []

		output.extend( [ 
			(0, "int solve_funky_check_commands_c("),
			(1, "p_blackwood cf,"),
			(1, "t_piece board[WH]"),
			] )

		if only_signature:
			output.append( (1, ');') )
			return output

		(u_shift, r_shift, d_shift, l_shift) = self.puzzle.scenario.edges_shift_from_references()

		output.append( (1, ") {") )
		output.append( (1, "uint i;") )

		#output.append( (1, 'printf("Checking Commands\\n");' if self.DEBUG > 0 else "" ), )
		output.append( (1, 'cf->check_commands = 0;' ), )
		output.append( (0, '' ) )
		output.append( (1, 'if (cf->time_to_finish) {' ) )
		output.append( (2, 'cf->check_commands = 1;' ) )
		output.append( (1, 'return cf->time_to_finish;' ), )
		output.append( (1, '};' ) )
		output.append( (0, '' ) )
		output.append( (1, 'if (cf->heartbeat > cf->heartbeat_limit) {' ) )
		output.append( (2, 'cf->time_to_finish = 1;' ) )
		output.append( (2, 'cf->check_commands = 1;' ) )
		output.append( (1, 'return cf->time_to_finish;' ), )
		output.append( (1, '};' ) )
		output.append( (0, '' ) )
		output.append( (1, 'do_commands(cf);' ), )
		output.append( (0, '' ) )
		output.append( (1, 'while ((cf->leave_cpu_alone || cf->pause) && !cf->time_to_finish) {' ) )
		output.append( (2, 'do_commands(cf);' ), )
		output.append( (2, 'sleep(1);' ), )
		output.append( (1, '}' ), )
		output.append( (0, '' ), )
		output.append( (1, 'if (cf->send_a_notification) {' ), )
		output.append( (2, 'if (cf->best_depth_seen == 0) {') )
		output.append( (3, 'for(i=0;i<WH;i++) { cf->board[i].info.u = board[i].u'+u_shift+'; cf->board[i].info.r = board[i].r'+r_shift+'; cf->board[i].info.d = board[i].d'+d_shift+'; cf->board[i].info.l = board[i].l'+l_shift+'; }') )
		output.append( (2, '}' ), )
		output.append( (2, 'cf->wait_for_notification = 1;' ) )
		output.append( (2, 'cf->send_a_notification = 0;' ), )
		output.append( (1, '}' ), )
		output.append( (0, '' ), )
		output.append( (1, 'return cf->time_to_finish;' ), )
		output.append( (0, '' ), )
		output.append( (0, '}' ), )
		output.append( (0, '' ), )

		return output

	# ----- Generate Funky functions
	def gen_solve_funky_we_have_a_solution_c( self, only_signature=False):
		output = []

		output.extend( [ 
			(0, "int solve_funky_we_have_a_solution_c("),
			(1, "p_blackwood cf,"),
			(1, "t_piece board[WH]"),
			] )

		if only_signature:
			output.append( (1, ');') )
			return output

		(u_shift, r_shift, d_shift, l_shift) = self.puzzle.scenario.edges_shift_from_references()

		output.append( (1, ") {") )
		output.append( (1, "uint i;") )

		output.append( (1, '// We have a complete puzzle !!' ) )
		output.append( (1, 'for(i=0;i<WH;i++) { cf->board[i].info.u = board[i].u'+u_shift+'; cf->board[i].info.r = board[i].r'+r_shift+'; cf->board[i].info.d = board[i].d'+d_shift+'; cf->board[i].info.l = board[i].l'+l_shift+'; }') )
		output.append( (1, 'cf->wait_for_notification = 1;' ), )
		output.append( (1, 'cf->check_commands = 1;' ), )
		output.append( (1, 'for(i=0;(i<3000000) && (!cf->time_to_finish);i++) {') )
		output.append( (2, 'do_commands(cf);' ) )
		output.append( (2, 'sleep(1); // Wait for the WFN thread' ) )
		output.append( (1, '}' ) )
		output.append( (0, '' ), )
		output.append( (1, 'return 0;' ), )
		output.append( (0, '}' ), )
		output.append( (0, '' ), )

		return output


	# ----- Generate Funky functions
	def gen_solve_funky_best_depth_seen_c( self, only_signature=False):
		output = []

		output.extend( [ 
			(0, "int solve_funky_best_depth_seen_c("),
			(1, "p_blackwood cf,"),
			(1, "t_piece board[WH],"),
			(1, "uint64 best_depth_seen"),
			] )

		if only_signature:
			output.append( (1, ');') )
			return output

		(u_shift, r_shift, d_shift, l_shift) = self.puzzle.scenario.edges_shift_from_references()

		output.append( (1, ") {") )
		output.append( (1, "uint i;") )


		output.append( (1, 'cf->best_depth_seen = best_depth_seen;') )
		output.append( (1, 'cf->best_depth_seen_heartbeat[ best_depth_seen ] = cf->heartbeat;') )
		if self.DEBUG > 0:
			output.append( (1, 'for(i=0;i<WH;i++) { cf->board[i].info.u = board[i].u'+u_shift+'; cf->board[i].info.r = board[i].r'+r_shift+'; cf->board[i].info.d = board[i].d'+d_shift+'; cf->board[i].info.l = board[i].l'+l_shift+'; }') )

		output.append( (1, "if (best_depth_seen >= "+str(self.puzzle.scenario.depth_first_notification)+" ) {" ) )
		output.append( (2, 'cf->wait_for_notification = 1;' ) )
		output.append( (2, 'cf->commands |= SAVE_MAX_DEPTH_SEEN_ONCE;' ) )
		output.append( (2, 'cf->commands |= SHOW_MAX_DEPTH_SEEN_ONCE;' ) )
		output.append( (2, 'if (best_depth_seen > WH-2)' ) )
		output.append( (3, 'cf->commands |= SHOW_BEST_BOARD_URL_ONCE;' ) )
		output.append( (2, 'do_commands(cf);' ) )
		output.append( (1, '}' ), )
		output.append( (0, '' ), )
		output.append( (1, 'return 0;' ), )
		output.append( (0, '}' ), )
		output.append( (0, '' ), )

		return output

	# ----- Generate Funky functions
	def gen_solve_funky_trace_c( self, only_signature=False):
		output = []

		output.extend( [ 
			(0, "int solve_funky_trace_c("),
			(1, "p_blackwood cf,"),
			(1, "uint64 position"),
			] )

		if only_signature:
			output.append( (1, ');') )
			return output


		output.append( (1, ") {") )
		output.append( (1, "uint64 i, depth, space, up, right;") )

		output.append( (0, 'depth  = (position >> 24) & 0xff;' ), )
		output.append( (0, 'space  = (position >> 16) & 0xff;' ), )
		output.append( (0, 'up     = (position >>  8) & 0xff;' ), )
		output.append( (0, 'right  = (position >>  0) & 0xff;' ), )
		output.append( (0, '' ), )
		output.append( (0, 'printf("Trace: %3llu solve_funky_space_%03llu_ref_up_%02llu_ref_right_%02llu\\n", depth, space, up, right); ' ), )
		output.append( (0, '' ), )
		output.append( (1, 'return 0;' ), )
		output.append( (0, '}' ), )
		output.append( (0, '' ), )

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
			#(1, 'return solve(NULL, NULL);'), 
			(1, 'return solve_funky_bootstrap_c(NULL);'), 
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
		self.writeGen( gen, self.gen_save_best_depth_seen_function( only_signature=True ) )
		self.writeGen( gen, self.gen_getSolutionURL_function( only_signature=True ) )
		self.writeGen( gen, self.gen_getBestDepthHeartbeat_function( only_signature=True ) )

		self.writeGen( gen, self.gen_print_url_functions(only_signature=True) )


		self.writeGen( gen, self.gen_do_commands(only_signature=True) )
		self.writeGen( gen, self.gen_print_functions(only_signature=True) )
		self.writeGen( gen, self.gen_filter_function( only_signature=True ) )
		#self.writeGen( gen, self.gen_solve_function(only_signature=True) )
		self.writeGen( gen, self.gen_solve_funky_functions(only_signature=True) )
		self.writeGen( gen, self.gen_solve_funky_check_command_c(only_signature=True) )
		self.writeGen( gen, self.gen_solve_funky_we_have_a_solution_c(only_signature=True) )
		self.writeGen( gen, self.gen_solve_funky_best_depth_seen_c(only_signature=True) )
		self.writeGen( gen, self.gen_solve_funky_bootstrap_c(only_signature=True) )
		self.writeGen( gen, self.gen_solve_funky_trace_c(only_signature=True) )

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
			self.writeGen( gen, self.gen_save_best_depth_seen_function( only_signature=False) )
			self.writeGen( gen, self.gen_getSolutionURL_function( only_signature=False ) )
			self.writeGen( gen, self.gen_getBestDepthHeartbeat_function( only_signature=False ) )
			self.writeGen( gen, self.gen_print_url_functions(only_signature=False) )
			self.writeGen( gen, self.gen_print_functions(only_signature=False) )
			self.writeGen( gen, self.gen_do_commands(only_signature=False ) )

			self.writeGen( gen, self.gen_solve_funky_check_command_c(only_signature=False) )
			self.writeGen( gen, self.gen_solve_funky_we_have_a_solution_c(only_signature=False) )
			self.writeGen( gen, self.gen_solve_funky_best_depth_seen_c(only_signature=False) )
			self.writeGen( gen, self.gen_solve_funky_bootstrap_c(only_signature=False) )
			self.writeGen( gen, self.gen_solve_funky_trace_c(only_signature=False) )


		elif macro_name == "generate":
			self.writeGen( gen, self.gen_filter_function( only_signature=False ) )
			#self.writeGen( gen, self.gen_solve_function(only_signature=False) )

		elif macro_name == "funky_asm":
			self.writeGen( gen, self.gen_solve_funky_functions(only_signature=False) )


		elif macro_name == "main":

			self.writeGen( gen, self.gen_main_function(only_signature=False) )


		self.writeGen( gen, self.getFooterC( module=module ) )

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
		cf = self.cb
		self.copy_new_arrays_to_cb()

		#l = self.gen_solve_function( only_signature=True )
		#args = []
		#loc = locals()
		#for pname in self.getParametersNamesFromSignature(l):
		#	args.append( loc[ pname ] )
		#self.LibExtWrapper( self.getFunctionNameFromSignature(l), args, timeit=True )

		l = self.gen_solve_funky_bootstrap_c( only_signature=True )
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

		if self.puzzle.scenario.STATS > 0 or self.puzzle.scenario.PERF > 0:
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


"""
# Calling function
# First Argument  : RDI
# Second Argument : RSI
# Third Argument  : RDX
# Fourth Argument : RCX
# Fifth Argument  : R8
# Sixth Argument  : R9

https://bob.cs.sonoma.edu/IntroCompOrg-x64/bookch6.html
+-----------------+---------------+---------------+------------+
| 8 Byte Register | Lower 4 Bytes | Lower 2 Bytes | Lower Byte |
+-----------------+---------------+---------------+------------+
|   rbp           |     ebp       |     bp        |     bpl    |
|   rsp           |     esp       |     sp        |     spl    |
|   rip           |     eip       |               |            |
|   rax           |     eax       |     ax        |     al     |
|   rbx           |     ebx       |     bx        |     bl     |
|   rcx           |     ecx       |     cx        |     cl     |
|   rdx           |     edx       |     dx        |     dl     |
|   rsi           |     esi       |     si        |     sil    |
|   rdi           |     edi       |     di        |     dil    |
|   r8            |     r8d       |     r8w       |     r8b    |
|   r9            |     r9d       |     r9w       |     r9b    |
|   r10           |     r10d      |     r10w      |     r10b   |
|   r11           |     r11d      |     r11w      |     r11b   |
|   r12           |     r12d      |     r12w      |     r12b   |
|   r13           |     r13d      |     r13w      |     r13b   |
|   r14           |     r14d      |     r14w      |     r14b   |
|   r15           |     r15d      |     r15w      |     r15b   |
+-----------------+---------------+---------------+------------+
"""
