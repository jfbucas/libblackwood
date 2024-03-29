#!/usr/bin/python3


#
# The Main program
# 


# Global libs
import os
import time
import sys
import ctypes
import socket
import threading
from multiprocessing import Queue

# Local libs
import data
import libblackwood
import thread_input
import thread_blackwood
import process_blackwood


# Puzzle
puzzle = data.loadPuzzle()
if puzzle == None:
	print( "Error with loading puzzle" )
	exit()

# Processes
blackwood_processes = []

# ----- dispatch the command to all processes
def standalone_blackwood_processes_command( commands ):
	for gt in blackwood_processes:
		if gt.status == "running":
			#print("Send command ", commands)
			gt.queue_parent_child.put( commands )
		#else:
		#	print("Process not ready for ", commands)

# ----- get the process status
def standalone_blackwood_processes_status():
	for gt in blackwood_processes:
		while not gt.queue_child_parent.empty():
			gt.status = gt.queue_child_parent.get()
			#print("Process status is now  : ", gt.status)

# ----- get the TTF
def getTTF():
	for gt in blackwood_processes:
		if gt.status == "exit":
			return True
	return False

# ----- get the number of CORES
def getCores():
	CORES=os.cpu_count()
	if os.environ.get('CPUS') != None:
		CORES=int(os.environ.get('CPUS'))
	if os.environ.get('CORE') != None:
		CORES=int(os.environ.get('CORE'))
	if os.environ.get('CORES') != None:
		CORES=int(os.environ.get('CORES'))

	if CORES < 0:
		CORES=os.cpu_count()-abs(CORES)
	if CORES <= 0:
		CORES=1

	return CORES

# ----- Standalone machine
def standalone():

	# Compile the library - this one is not actually executed
	blackwood = libblackwood.LibBlackwood( puzzle, skipcompile=False )

	# Create the queues/threads
	CORES=getCores()
	for c in range(CORES):
		q_p_c = Queue() # Queue Parent-Child
		q_c_p = Queue() # Queue Child-Parent
		gt = process_blackwood.Blackwood_Process( puzzle, c, q_p_c, q_c_p )
		gt.status = "init"
		blackwood_processes.append( gt )

	# Start the input thread
	myInput = thread_input.Input_Thread( standalone_blackwood_processes_command, blackwood, 0.1, stdin_fn=sys.stdin.fileno() )
	myInput.start()


	# Start the parallel jobs
	print("x-]"+puzzle.XTermInfo+"  Starting "+str(CORES)+" thread"+ ("s" if CORES > 1 else "")+"  "+puzzle.XTermNormal+"[-x")
	for gt in blackwood_processes:
		print(".", end="", flush=True)
		gt.start()
	print()

	# Wait for Time To Finish flag
	count = 0
	while not getTTF():
		standalone_blackwood_processes_status()
		standalone_blackwood_processes_command( [ "heartbeat", "check_commands" ] )
		time.sleep(1)
	
	myInput.stop_input_thread = True	

	# Tell all processes to finish
	standalone_blackwood_processes_command( "exit" )

# ----- Statistics
def statistics():

	# Iterate through all combinations of 1 border + 2 center patterns
	hp_to_test = []
	
	for a in puzzle.static_colors_border_count: 
		for b in puzzle.static_colors_center_count: 
			if a != b:
				for c in puzzle.static_colors_center_count: 
					if b != c:
						hp_to_test.append( (a, b, c) )

	print("Combination of heuristic patterns to try", len(hp_to_test))
	
	CORES=getCores()

	for hp in hp_to_test:
		p = data.loadPuzzle(params={ "heuristic_patterns": hp, "timelimit": 100 })
		# Compile the library - this one is not actually executed
		blackwood = libblackwood.LibBlackwood( p, skipcompile=False )

		# Create the queues/threads
		CORES=getCores()
		for c in range(CORES):
			q_p_c = Queue() # Queue Parent-Child
			q_c_p = Queue() # Queue Child-Parent
			gt = process_blackwood.Blackwood_Process( p, c, q_p_c, q_c_p, loop_count_limit=1 )
			gt.status = "init"
			blackwood_processes.append( gt )

		# Start the input thread
		myInput = thread_input.Input_Thread( standalone_blackwood_processes_command, blackwood, 0.1, stdin_fn=sys.stdin.fileno() )
		myInput.start()


		# Start the parallel jobs
		print("x-]"+puzzle.XTermInfo+"  Starting "+str(CORES)+" thread"+ ("s" if CORES > 1 else "")+"  "+puzzle.XTermNormal+"[-x")
		for gt in blackwood_processes:
			print(".", end="", flush=True)
			gt.start()
		print()

		# Wait for Time To Finish flag
		while not getTTF():
			standalone_blackwood_processes_status()
			standalone_blackwood_processes_command( [ "heartbeat", "check_commands" ] )
			time.sleep(1)
		
		myInput.stop_input_thread = True	

		# Tell all processes to finish
		standalone_blackwood_processes_command( "exit" )




# ----- Run
def run( role_id = "" ):

	# timer
	startTime = time.time()

	print( )
	print( puzzle.H1_OPEN + puzzle.TITLE_STR + puzzle.H1_CLOSE )
	print( )

	# -------------------------------------------
	# Start

	if role_id == "standalone":
		standalone()
	elif role_id == "stats":
		statistics()
	elif role_id == "help":
		print( "+ Roles")
		print( " [--standalone]\t\t\ttake on standalone mode (default)")
		print( " [--stats]\t\t\ttry to get some stats")
		print( )
	else:
		print( "ERROR: unknown Role:", role_id )

	print()
	print( "Execution time: ", time.time() - startTime )




if __name__ == "__main__":

	role_id = "standalone"

	# -------------------------------------------
	# Get parameters
	if len(sys.argv) > 1:
		for a in sys.argv[1:]:
			if a.startswith("--standalone"):
				role_id = "standalone"
			elif a.startswith("--stats"):
				role_id = "stats"
			elif a.startswith("--nop"):
				role_id = "nop"
			elif a.startswith("-h") or a.startswith("--help"):
				role_id = "help"
			else:
				role_id = "help"

	# -------------------------------------------
	# Validate parameters
	pass
	
	# -------------------------------------------
	# Do the thing
	run( role_id )
