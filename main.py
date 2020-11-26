#!/usr/bin/python3


#
# The Main program
# 


# Global libs
import random
import os
import time
import sys
import ctypes
import threading
import socket

if (sys.version_info[0] < 3) or (sys.version_info[1] < 6):
    raise Exception("Python 3.6 or a more recent version is required.")

# Local libs
import data
import libblackwood
import thread_input
import thread_blackwood


# Puzzle
puzzle = data.loadPuzzle()
if puzzle == None:
	print( "Error with loading puzzle" )
	exit()

# Threads
blackwood_threads = []



# ----- dispatch the command to all threads
def standalone_blackwood_threads_command( commands ):
	for gt in blackwood_threads:
		gt.blackwood.command_handler( commands )

# ----- get the time to finish flags from all threads
def standalone_blackwood_threads_getTTF():
	result = 0
	for gt in blackwood_threads:
		result += gt.blackwood.LibExt.getTTF( gt.blackwood.current_blackwood )
	return result


# ----- Standalone machine
def standalone():

	# Compile the library - this one is not actually executed
	blackwood = libblackwood.LibBlackwood( puzzle )

	# Create the threads
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


	for c in range(CORES):
		blackwood_threads.append( thread_blackwood.Blackwood_Thread( puzzle, c ) )

	# Start the input thread
	myInput = thread_input.Input_Thread( standalone_blackwood_threads_command, blackwood, 0.1 )
	myInput.start()

	# Start the threads
	for gt in blackwood_threads:
		#print( "Starting thread ", gt.number )
		gt.start()

	# Wait for Time To Finish flag
	count = 0
	while not standalone_blackwood_threads_getTTF():
		standalone_blackwood_threads_command( [ "heartbeat", "check_commands" ] )
		time.sleep(1)
	
	myInput.stop_input_thread = True	

	# Tell all threads to finish
	standalone_blackwood_threads_command( "exit" )


# ----- Parameters
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
	elif role_id == "help":
		print( "+ Roles")
		print( " [--standalone]\t\t\ttake on standalone mode (default)")
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
			elif a.startswith("--nop"):
				role_id = "nop"
			elif a.startswith("-h") or a.startswith("--help"):
				role_id = "help"
			else:
				role_id = "help"

	# -------------------------------------------
	# Validate parameters

	
	# -------------------------------------------
	# Do the thing
	run( role_id )
