
# Global libs
import threading
import ctypes

# Local libs
import libblackwood
import thread_lca
import thread_wfn


#
# This thread will start one of the external Solve function
#
# it will spawn two other threads:
#  -  Waits for Solution
#  -  Leave CPU Alone : can pause the Solve function
#



# Thread Class for running Blackwood processes
class Blackwood_Thread( threading.Thread ):

	blackwood = None
	puzzle = None
	number = 0
	ready = False

	def __init__(self, puzzle, number=0): 
		threading.Thread.__init__(self)
		self.puzzle = puzzle
		self.number = number
		self.ready = False


	def run(self):
		self.blackwood = libblackwood.LibBlackwood( self.puzzle, extra_name="_"+str(self.number).zfill(4), skipcompile=True )
		self.blackwood.copy_new_arrays_to_cb()

		cb = self.blackwood.cb
		
		self.ready = True

		# Start the solution thread
		myWFN = thread_wfn.Wait_For_Notification_Thread( self.blackwood, self.puzzle )
		myWFN.start()

		# Start the locking thread
		myLCA = thread_lca.Leave_CPU_Alone_Thread( self.blackwood, period=5, desktop=self.puzzle.DESKTOP )
		myLCA.start()


		thread_output_filename = ctypes.c_char_p(("generated/"+self.puzzle.HOSTNAME+"/progress_thread_"+'{:0>4d}'.format(self.number)).encode('utf-8'))

		l = self.blackwood.gen_solve_function( only_signature=True )
		args = []
		loc = locals()
		for pname in self.blackwood.getParametersNamesFromSignature(l):
			args.append( loc[ pname ] )

		while not self.blackwood.LibExt.getTTF( self.blackwood.cb ):
			self.blackwood.LibExtWrapper( self.blackwood.getFunctionNameFromSignature(l), args, timeit=True )
			if not self.blackwood.LibExt.getTTF( self.blackwood.cb ):
				self.blackwood.copy_new_arrays_to_cb()

		myLCA.stop_lca_thread = True	
		myWFN.stop_wfn_thread = True	


