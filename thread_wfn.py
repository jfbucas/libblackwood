# Global Libs
import os
import time
import datetime
import threading
import multiprocessing
import subprocess
import ctypes
import base64
import requests

# Local Lib
import puzzle


#
# Thread that Waits For a Notification and reports it to a web-hook server
# 
# Note: environment URL_HOOK must be set
#

class Wait_For_Notification_Thread(threading.Thread):
	"""This thread does nothing until the main program sends a notification"""

	URL=""
	RETRY_PERIOD = 0x2

	libblackwood = None
	puzzle = None
	notification_url = ""
	stop_wfn_thread = False
	giturl = ""

	def __init__(self, libblackwood, puzzle): 
		threading.Thread.__init__(self)
		self.libblackwood = libblackwood
		self.puzzle = puzzle
		self.stop_wfn_thread = False
		self.notification_url = ctypes.create_string_buffer(self.puzzle.board_wh*32)
	
		if os.environ.get('URL_HOOK') != None:
			self.URL = os.environ.get('URL_HOOK')
			if self.puzzle.DEBUG > 2:
				self.puzzle.info(" * Reporting notifications to server : "+str(self.URL) )
		else:
			# We do not run if we have no URL to report to
			self.stop_wfn_thread = True
			self.puzzle.error(" * Make sure you have defined URL_HOOK to get notifications when a notification is found" )

		self.giturl = "https://github.com/jfbucas/libblackwood/commit/" + self.puzzle.git()


	def transmit(self, channel, payload):
		# Submit the notification up to 5 times
		good = 0
		retry = 20
		while retry > 0:

			r = requests.post(self.URL, data=payload)
			try:
				r.raise_for_status()
			except requests.exceptions.HTTPError as err:
				print('Error code: ', str(err), '... retrying in', self.RETRY_PERIOD, ' seconds')
				print( payload )
				time.sleep(self.RETRY_PERIOD)
				retry -= 1
			else:
				retry = 0
				good = 1

		if good:
			print()
			print(' Notification to '+channel+' transmitted @', str(datetime.datetime.now()), 'to', self.URL )
			print()
			if self.puzzle.DEBUG > 3:
				print( payload )
				print()
		else:
			self.puzzle.error(" * Giving up transmission")

	def run(self):


		while not self.stop_wfn_thread and not self.libblackwood.LibExt.getTTF(self.libblackwood.cb):
			if self.libblackwood.LibExt.getWFN(self.libblackwood.cb) != 0:

				
				self.libblackwood.LibExt.getSolutionURL( self.libblackwood.cb, self.notification_url )
				if self.puzzle.DEBUG > 3:
					print(" Now DO SOMETHING with the notification ", self.notification_url.value.decode("utf-8")  )

				# A complete solution
				channel = str(self.puzzle.scenario.score_target)

				if self.libblackwood.LibExt.getBestDepthSeen(self.libblackwood.cb) < self.puzzle.board_wh:
					# Have we reached the time limit?
					if self.libblackwood.LibExt.getHB(self.libblackwood.cb) > self.libblackwood.LibExt.getHBLimit(self.libblackwood.cb):
						if os.environ.get('NOTIFY_END') == None:
							self.libblackwood.LibExt.setWFN(self.libblackwood.cb, 0)
							continue
						channel = "end"
					else:
						# Only a partial solution
						channel = "partial"
						if self.libblackwood.LibExt.getBestDepthSeen(self.libblackwood.cb) >= self.puzzle.scenario.depth_first_notification:
							channel = str(self.libblackwood.LibExt.getBestDepthSeen(self.libblackwood.cb))

				max_depth_seen_hb="["
				for i in range(0, self.puzzle.board_wh):
					t = self.libblackwood.LibExt.getBestDepthSeenHeartbeat(self.libblackwood.cb, i)
					if t > 0:
						max_depth_seen_hb+=str(i)+":"+str(t)+" | "
				max_depth_seen_hb+="]"

				payload="{\"username\":\""+self.puzzle.HOSTNAME+"\","
				payload+="\"icon_emoji\":\":jigsaw:\","
				payload+="\"channel\":\""+channel+"\","
				payload+="\"text\":\"@channel [View]("+self.notification_url.value.decode("utf-8")+") "+ "[Git]("+self.giturl+") "+str(self.puzzle.scenario)
				payload+=" "+str(self.libblackwood.LibExt.getBestDepthSeen(self.libblackwood.cb))
				payload+=" "+max_depth_seen_hb
				payload+="\"}"

				self.transmit(channel, payload)

				self.libblackwood.LibExt.setWFN(self.libblackwood.cb, 0)

			time.sleep(1)



if __name__ == "__main__":

	# TODO
	pass
