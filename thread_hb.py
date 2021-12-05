
# Global libes
import os
import time
import datetime
import threading
import multiprocessing
import subprocess
import ctypes


# 
# HeartBeat thread
# 

class HeartBeat_Thread(threading.Thread):
	"""This thread increases the heartbeat"""

	libblackwood = None
	period = 1
	stop_hb_thread = False

	def __init__(self, libblackwood, period=1): 
		threading.Thread.__init__(self)
		self.libblackwood = libblackwood
		self.period = period
		self.stop_hb_thread = False

	def run(self):
		while not self.stop_hb_thread and not self.libblackwood.LibExt.getTTF(self.libblackwood.cb):
			self.libblackwood.LibExt.incHB(self.libblackwood.cb)
			self.libblackwood.LibExt.setCheckCommands(self.libblackwood.cb, 1)
			time.sleep(self.period)



if __name__ == "__main__":

	# TODO test the script
	pass
