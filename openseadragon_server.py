#!/usr/bin/python3

import os
import sys
import json
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
#from SocketServer import ThreadingMixIn
from socketserver import ThreadingMixIn
from urllib.parse import urlparse
import requests
import time
import threading
from multiprocessing import Queue, Process
import subprocess



import data
import libbigpicture

# Status codes
status_eror = -2
status_none = -1
status_todo = 0
status_wait = 1
status_done = 2

hostName = ""
serverPort = 9000

all_jobs = None
start_timestamp = str(time.time())
timelimit = 1 # Minutes

TILESIZE = 1024

class MyServer(BaseHTTPRequestHandler):
	def do_GET(self):
		query = urlparse(self.path).query
		qc = dict(qc.split("=") for qc in query.split("&"))

		if not "depth" in qc  or \
			not "x" in qc  or \
			not "y" in qc:
			print("Wrong query, missing parameters")
			self.send_response(404)
			self.send_header('Content-Type', 'text/html')
			self.end_headers()
			return

		depth=int(qc["depth"])
		x=int(qc["x"])*TILESIZE
		y=int(qc["y"])*TILESIZE
		print("Generating tile image for depth=",depth, "x=",x, "y=",y)
		#lib.getImageRotations( depth, x, y, TILESIZE, TILESIZE )
		p = Process(target=lib.getImageRotations, args=( depth, x, y, TILESIZE, TILESIZE ))

		p.start()
		p.join()

		self.send_response(200)
		self.send_header('Content-Type', 'image/png')
		self.end_headers()

		filename = "jobs/"+lib.puzzle.getFileFriendlyName( lib.puzzle.name )+"/d="+str(depth)+"_x="+str(x)+"_y="+str(y)+".png"
		with open(filename, 'rb') as file_handle:
			png = file_handle.read()

		self.wfile.write(bytes(png))


def server():

	#webServer = HTTPServer((hostName, serverPort), MyServer)
	webServer = ThreadingHTTPServer((hostName, serverPort), MyServer)
	print("Server started http://%s:%s" % (hostName, serverPort))

	try:
		webServer.serve_forever()
	except KeyboardInterrupt:
		pass

	webServer.server_close()
	print("Server stopped.")

# ----- Parameters
def run( role = "" ):

	# timer
	startTime = time.time()

	# -------------------------------------------
	# Start

	if role == "server":
		server()
	elif role == "client":
		if len(sys.argv) > 2:
			client(sys.argv[2])
		else:
			run( "help" )

	elif role == "help":
		print( "+ Roles")
		print( " [--server|-s]\t\t\ttake on server role (default)")
		print( " [--client|-c] [hostname]\t\t\ttake on client role")
		print( )
	else:
		print( "ERROR: unknown parameter:", role )

	#print()
	#print( "Execution time: ", time.time() - startTime )



if __name__ == "__main__":

	p = data.loadPuzzle()
	lib = libbigpicture.LibBigPicture( p )

	role = "server"
	#role = "help"

	# Get Role
	if len(sys.argv) > 1:
		a = sys.argv[1]
		if a.startswith("--server") or a.startswith("-s"):
			role = "server"
		elif a.startswith("--client") or a.startswith("-c"):
			role = "client"
		elif a.startswith("-h") or a.startswith("--help"):
			role = "help"
	
	run( role )

