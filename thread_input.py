#!/usr/bin/python3

# Global Libs
import os
import time
import datetime
import threading
import signal
import sys
import select

#
# This thread reads keyboard inputs and calls back a function
#


class Input_Thread(threading.Thread):

	callback = None
	libblackwood = None
	period = 1
	stop_input_thread = False
	stdin = None

	def __init__(self, callback, libblackwood=None, period=1, stdin_fn=None): 
		threading.Thread.__init__(self)
		self.libblackwood = libblackwood
		self.callback = callback
		self.period = period
		self.stop_input_thread = False
		if stdin_fn == None:
			self.stdin = sys.stdin
		else:
			self.stdin = os.fdopen(stdin_fn)

	def run(self):

		if sys.stdout.isatty():
			
			if self.libblackwood == None:

				while not self.stop_input_thread:
					#print("Enter commands :")
					i, o, e = select.select( [self.stdin], [], [], self.period )
					if (i):
						command = self.stdin.readline().strip()
						self.callback( [ command ] )
			else:

				while not self.stop_input_thread and not self.libblackwood.LibExt.getTTF(self.libblackwood.cb):
					#print("Enter commands:")
					i, o, e = select.select( [self.stdin], [], [], self.period )
					if (i):
						command = self.stdin.readline().strip()
						self.callback( [ command ] )
		else:
			print("Thread input cannot grab the STDIN")


