
# Global Libs
import os
import time
import datetime
import threading
import multiprocessing
import subprocess
import ctypes
import base64

from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# Local Lib
import puzzle


#
# Thread that Waits For a Solution  and  reports it to a web server
# 
# Note: environment REPORT_URL must be set
#

class Wait_For_Solution_Thread(threading.Thread):
	"""This thread does nothing until the main program finds a solution"""

	URL=""
	RETRY_PERIOD = 0x2

	libblackwood = None
	puzzle = None
	solution_url = ""
	stop_wfs_thread = False

	def __init__(self, libblackwood, puzzle): 
		threading.Thread.__init__(self)
		self.libblackwood = libblackwood
		self.puzzle = puzzle
		self.stop_wfs_thread = False
		self.solution_url = ctypes.create_string_buffer(self.puzzle.board_wh*32)
	
		if os.environ.get('REPORT_URL') != None:
			self.URL = os.environ.get('REPORT_URL')
			if self.puzzle.DEBUG > 2:
				self.puzzle.info(" * Reporting solutions to server : "+str(self.URL) )
		else:
			# We do not run if we have no URL to report to
			self.stop_wfs_thread = True
			self.puzzle.error(" * Make sure you have defined REPORT_URL to get notifications when a solution is found" )

	def run(self):


		while not self.stop_wfs_thread and not self.libblackwood.LibExt.getTTF(self.libblackwood.cb):
			if self.libblackwood.LibExt.getWFS(self.libblackwood.cb) != 0:
				self.libblackwood.LibExt.getSolutionURL( self.libblackwood.cb, self.solution_url )
				if self.puzzle.DEBUG > 3:
					print(" Now DO SOMETHING with the solution ", self.solution_url.value.decode("utf-8")  )

				# Submit the Solution until it is received
				good = 0
				while good == 0:
					req = Request( self.URL+'?solution='+base64.standard_b64encode(self.solution_url.value).decode("utf-8") )
					try:
						response = urlopen(req)
					except HTTPError as e:
						# do something
						print('Error code: ', e.code, '... retrying in', self.RETRY_PERIOD, ' seconds')
					except URLError as e:
						# do something
						print('Reason: ', e.reason, '... retrying in', self.RETRY_PERIOD, ' seconds')
					else:
						# do something
						good = 1

					time.sleep(self.RETRY_PERIOD)
				
				print()
				print(' Solution transmitted @', str(datetime.datetime.now()), 'to', self.URL )
				print()

				#(val, output) = subprocess.getstatusoutput(self.WGET+self.URL+self.solution_url.value.decode("utf-8") )
				#if val != 0:
				#	print(output)
				#	return val


				time.sleep(0x5)
				break

			time.sleep(1)



if __name__ == "__main__":

	# TODO test the script
	pass
