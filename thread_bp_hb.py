
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

class BigPicture_HeartBeat_Thread(threading.Thread):
	"""This thread increases the heartbeat"""

	libbigpicture = None
	period = 1
	stop_hb_thread = False

	def __init__(self, libbigpicture, period=1): 
		threading.Thread.__init__(self)
		self.libbigpicture = libbigpicture
		self.period = period
		self.stop_hb_thread = False

	def run(self):
		while not self.stop_hb_thread and not self.libbigpicture.LibExt.getTTF(self.libbigpicture.global_bigpicture):
			self.libbigpicture.LibExt.incHB(self.libbigpicture.global_bigpicture)
			self.libbigpicture.LibExt.setCheckCommands(self.libbigpicture.global_bigpicture, 1)
			time.sleep(self.period)



if __name__ == "__main__":

	# TODO test the script
	pass
