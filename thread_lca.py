
# Global libs
import os
import time
import datetime
import threading
import ctypes


#
# This thread checks if the CPU should be left alone based on
#
#   - not "niced" CPU usage
#   - Time of day
#



CLOCK_TICKS = os.sysconf("SC_CLK_TCK")

class Leave_CPU_Alone():

	cpu_info = {}
	cpu_info[ 0 ] = {}
	cpu_info[ 1 ] = {}
	cpu_turn = 0
	period = 1

	last_answer = False

	PROCESS_CPU_THRESHOLD_SERVER = 2.8
	#PROCESS_CPU_THRESHOLD_SERVER = 20.8
	PROCESS_CPU_THRESHOLD_DESKTOP = 1.5

	desktop = False

	#HOURS_WINDOW = [ 23, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ]
	HOURS_WINDOW = [ 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21 ]

	def __init__( self, period=5, desktop=False ):

		self.get_cpu_info( 0 )
		self.get_cpu_info( 1 )

		self.period  = period
		self.desktop = desktop

	def get_cpu_info(self, turn=None ):

		if turn == None:
			turn = self.cpu_turn


		f = open('/proc/stat', 'rb')
		try:
			values = f.readline().split()
		finally:
			f.close()

		self.cpu_info[ turn ][ 0 ] = datetime.datetime.now()
		self.cpu_info[ turn ][ 1 ] = float(values[1]) / CLOCK_TICKS # User 


	def is_one_process_running( self ):
		self.get_cpu_info()

		# If the last reading is less than the time period old we prefer not to rush to any conclusion
		if (self.cpu_info[ self.cpu_turn ][ 0 ] - self.cpu_info[ 1 - self.cpu_turn ][ 0 ]) < datetime.timedelta(seconds=self.period):
			return self.last_answer

		v = (self.cpu_info[ self.cpu_turn ][ 1 ] - self.cpu_info[ 1 - self.cpu_turn ][ 1 ]) / self.period

		self.cpu_turn = 1 - self.cpu_turn
		self.last_answer = (v > (self.PROCESS_CPU_THRESHOLD_DESKTOP if self.desktop else self.PROCESS_CPU_THRESHOLD_SERVER))
		return self.last_answer
	
	def is_during_working_hours( self ):
		n = datetime.datetime.now()
		return self.desktop and (n.hour in self.HOURS_WINDOW)


class Leave_CPU_Alone_Thread(threading.Thread):

	lca = None
	libblackwood = None
	period = 1
	stop_lca_thread = False

	def __init__(self, libblackwood, period=5, desktop=False): 
		threading.Thread.__init__(self)
		self.lca = Leave_CPU_Alone( period=period, desktop=desktop )
		self.libblackwood = libblackwood
		self.period = period
		self.stop_lca_thread = False

	def run(self):
		#while not self.stop_lca_thread and not self.libblackwood.LibExt.getTTF(self.libblackwood.cb):
		#	time.sleep(self.period)

		if os.environ.get('NOLCA') != None:
			return
		
		while not self.stop_lca_thread and not self.libblackwood.LibExt.getTTF(self.libblackwood.cb):

			# 0 means it is not paused
			# 1 means it has been activated
			# 2 means it has been activated/forced manually

			if self.libblackwood.LibExt.getPause(self.libblackwood.cb) == 0:
				one_process = self.lca.is_one_process_running()
				working_hours = self.lca.is_during_working_hours()
				if one_process or working_hours:
					if self.libblackwood.DEBUG > 1:
						if one_process:
							print( "LCA: There one process running" )
						if working_hours:
							print( "LCA: Working hours" )
					self.libblackwood.LibExt.setLCA(self.libblackwood.cb, 1)
				else:
					self.libblackwood.LibExt.clearLCA(self.libblackwood.cb)

			time.sleep(self.period)
		


if __name__ == "__main__":

	lca = Leave_CPU_Alone(desktop=False)

	while True:
		print( lca.is_one_process_running() )
		print( lca.is_during_working_hours() )
		time.sleep(1)

