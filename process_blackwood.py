# Global libs
from multiprocessing import Process,Queue
import threading
import ctypes
import time
import os

# Local libs
import libblackwood
import thread_lca
import thread_wfn


#
# This process will start one of the external Solve function
#
# it will spawn two other threads:
#  -  Waits for Solution
#  -  Leave CPU Alone : can pause the Solve function
#

# 
# Communication thread
# 

class Communication_Thread(threading.Thread):

	libblackwood = None
	queue = None
	stop_communication_thread = False

	def __init__(self, libblackwood, queue): 
		threading.Thread.__init__(self)
		self.libblackwood = libblackwood
		self.queue = queue
		self.stop_communication_thread = False

	def run(self):
		while not self.stop_communication_thread and not self.libblackwood.LibExt.getTTF(self.libblackwood.cb):
			while not self.queue.empty():
				msg = self.queue.get()
				#print("Received command:", msg)
				self.libblackwood.command_handler( msg )
			time.sleep(0.1)


# Thread Class for running Blackwood processes
class Blackwood_Process( Process ):

	blackwood = None
	puzzle = None
	number = 0
	queue_parent_child = None
	queue_child_parent = None
	myComm = None
	loop_count_limit = 1<<32

	def __init__(self, puzzle, number=0, queue_parent_child=None, queue_child_parent=None, loop_count_limit=1<<32): 
		Process.__init__(self)
		self.puzzle = puzzle
		self.number = number
		self.queue_parent_child = queue_parent_child
		self.queue_child_parent = queue_child_parent
		self.loop_count_limit = loop_count_limit


	def run(self):
		#self.blackwood = libblackwood.LibBlackwood( self.puzzle, extra_name="_"+str(self.number).zfill(4), skipcompile=True )
		self.blackwood = libblackwood.LibBlackwood( self.puzzle, skipcompile=True )
		self.blackwood.copy_new_arrays_to_cb()

		cb = self.blackwood.cb
		
		myComm = Communication_Thread(self.blackwood, self.queue_parent_child)
		myComm.start()

		# Start the solution thread
		myWFN = thread_wfn.Wait_For_Notification_Thread( self.blackwood, self.puzzle )
		myWFN.start()

		# Start the locking thread
		myLCA = thread_lca.Leave_CPU_Alone_Thread( self.blackwood, period=5, desktop=self.puzzle.DESKTOP )
		myLCA.start()

		if os.environ.get('LOOPCOUNTLIMIT') != None:
			self.loop_count_limit=int(os.environ.get('LOOPCOUNTLIMIT'))
			self.puzzle.info("Limiting the number of loops to "+str(self.loop_count_limit))

		thread_output_filename = ctypes.c_char_p(("generated/"+self.puzzle.HOSTNAME+"/progress_thread_"+'{:0>4d}'.format(self.number)).encode('utf-8'))

		l = self.blackwood.gen_solve_function( only_signature=True )
		args = []
		loc = locals()
		for pname in self.blackwood.getParametersNamesFromSignature(l):
			args.append( loc[ pname ] )

		self.queue_child_parent.put("running")

		loop_count = 0
		while not self.blackwood.LibExt.getTTF( self.blackwood.cb ) and (loop_count < self.loop_count_limit):
			self.blackwood.LibExtWrapper( self.blackwood.getFunctionNameFromSignature(l), args, timeit=True )
			if not self.blackwood.LibExt.getTTF( self.blackwood.cb ):
				self.blackwood.copy_new_arrays_to_cb()
			
			loop_count += 1
	
		self.queue_child_parent.put("exit")

		myComm.stop_communication_thread = True
		myLCA.stop_lca_thread = True	
		myWFN.stop_wfn_thread = True	


