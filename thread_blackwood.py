
# Global libs
import threading
import ctypes

# Local libs
import libblackwood
import thread_lca
import thread_wfs


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

	def __init__(self, p, number=0): 
		threading.Thread.__init__(self)
		self.blackwood = libblackwood.LibBlackwood( p, extra_name="_"+str(number).zfill(4) )
		self.puzzle = p
		self.number = number

		self.blackwood.copy_new_arrays_to_current_blackwood()

	def run(self):
		# Start the solution thread
		myWFS = thread_wfs.Wait_For_Solution_Thread( self.blackwood, self.puzzle )
		myWFS.start()

		# Start the locking thread
		myLCA = thread_lca.Leave_CPU_Alone_Thread( self.blackwood, period=5, desktop=self.puzzle.DESKTOP )
		myLCA.start()

		current_blackwood = self.blackwood.current_blackwood

		thread_output_filename = ctypes.c_char_p(("generated/"+self.puzzle.HOSTNAME+"/progress_thread_"+'{:0>4d}'.format(self.number)).encode('utf-8'))

		l = self.blackwood.gen_solve_function( only_signature=True )
		args = []
		loc = locals()
		for pname in self.blackwood.getParametersNamesFromSignature(l):
			args.append( loc[ pname ] )

		while not self.blackwood.LibExt.getTTF( self.blackwood.current_blackwood ):
			self.blackwood.LibExtWrapper( self.blackwood.getFunctionNameFromSignature(l), args, timeit=True )
			if not self.blackwood.LibExt.getTTF( self.blackwood.current_blackwood ):
				self.blackwood.copy_new_arrays_to_current_blackwood()

		myLCA.stop_lca_thread = True	
		myWFS.stop_wfs_thread = True	


