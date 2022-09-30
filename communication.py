#!/usr/bin/python3

import os
import sys
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import time
import threading
from multiprocessing import Queue
import subprocess

import data

# Status codes
status_eror = -2
status_none = -1
status_todo = 0
status_wait = 1
status_done = 2

hostName = ""
serverPort = 21080

all_jobs = None
start_timestamp = str(time.time())
timelimit = 1 # Minutes

class MyServer(BaseHTTPRequestHandler):
	def do_GET(self):
		next_job = None
		for k in all_jobs.keys():
			if all_jobs[k]["status"] == status_todo:
				next_job = k
				break

		if next_job != None:
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			print("Sending job ID", next_job)
			all_jobs[next_job]["status"] = status_wait
			self.wfile.write(bytes(json.dumps({"job_id" : next_job, "prefix": all_jobs[next_job]["prefix"], "timelimit": timelimit}), "utf-8"))
		else:
			self.send_response(404)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			#self.wfile.write(bytes(json.dumps({"job_id" : -1, "prefix": ""}), "utf-8"))

	def do_POST(self):

		length = int(self.headers['Content-Length'])
		post_data = self.rfile.read(length)
		result = None
		try:
			result = json.loads(post_data)
		except json.decoder.JSONDecodeError as error:
			print("Wrong data: ", post_data)
			self.send_response(404)
			self.end_headers()
			#self.wfile.write(bytes(json.dumps({ "status": status_eror }), "utf-8"))

		if result != None:
			print(result)

			if "job_id" in result:
				job_id = result["job_id"]
				if all_jobs[ job_id  ][ "status" ] == status_wait:
					print("Received result for job ID", job_id)
					all_jobs[ job_id ][ "result" ] = result
					all_jobs[ job_id ][ "status" ] = status_done

					# Write to disk
					job_file = open("jobs/depth_014/EternityII_jobs.txt."+start_timestamp, "a")	
					job_file.write(str(all_jobs[ job_id ])+"\n")
					job_file.close()

					self.send_response(200)
					self.send_header('Content-Type', 'application/json')
					self.end_headers()
					self.wfile.write(bytes(json.dumps({ "status": status_done }), "utf-8"))
				else:
					print("Job ID", job_id, "was not waiting.")
					self.send_response(404)
					self.end_headers()
					#self.wfile.write(bytes(json.dumps({ "status": status_eror }), "utf-8"))
			else:
				print("No 'job_id' found : ", result)
				self.send_response(404)
				self.end_headers()
				#self.wfile.write(bytes(json.dumps({ "status": status_eror }), "utf-8"))
		

	def do_PUT(self):
		self.do_POST()




def readJobs():
	
	jobs = {}

	#filename = "jobs/depth_014/"+self.getFileFriendlyName( self.puzzle.name )+".txt"
	filename = "jobs/depth_014/EternityII.txt"

	if os.path.exists(filename):
		
		# Read the data
		job_id = 0
		jobsfile = open( filename, "r" )
		for line in jobsfile:
			if line.startswith('#'):
				continue
			line = line.strip('\n').strip(' ')
			prefix = line.split("|")[1]
			jobs[job_id] = { "job_id" : job_id, "line": line, "prefix" : prefix, "status" : status_todo }
			job_id += 1
		jobsfile.close()
	
	print("Found", len(jobs.keys()), "jobs")

	return jobs
		

def server():
	globals()["all_jobs"] = readJobs()

	webServer = HTTPServer((hostName, serverPort), MyServer)
	print("Server started http://%s:%s" % (hostName, serverPort))

	try:
		webServer.serve_forever()
	except KeyboardInterrupt:
		pass

	webServer.server_close()
	print("Server stopped.")


# A simple thread for multicore support
class client_thread(threading.Thread):

	host = None
	stop = False
	number = 0
	queue = None

	def __init__(self, host="localhost", number=0, queue=None):
		threading.Thread.__init__(self)
		self.host = host
		self.number = number
		self.queue = queue
		self.stop = False

	def run(self):

		os.environ["FORCECOMPILE"] = str(1)
		os.environ["PUZZLE"] = "E2"
		os.environ["SCENARIO"] = "ForBigpicture"

		while not self.stop:

			# Get a job
			r = None
			try:
				r = requests.get('http://'+self.host+":"+str(serverPort)+'/')
			except:
				print("Couldn't connect to "+self.host+". Try again in 5 sec.")
				time.sleep(5)
				

			if r != None:

				# check status code for response received
				if r.status_code != 200:
					print("Status code", r.status_code, ". Try again in 5 sec.")
					time.sleep(5)
					continue

				job = None
				try:
					job = json.loads(r.content)
				except json.decoder.JSONDecodeError as error:
					print("Wrong job data: ", r.content)


				# Do the job
				if job != None:
					print("Working on Job ID",job["job_id"], "with Prefix", job["prefix"], "in", job["timelimit"], "minutes")

					os.environ["PREFIX"] = job["prefix"]
					os.environ["TIMELIMIT"] = str(job["timelimit"])
					os.environ["EXTRA_NAME"] = "_"+str(self.number).zfill(4) 

					backtracker_result = subprocess.run(["python3", "libblackwood.py", "--simple"], stdout=subprocess.PIPE)
					print(backtracker_result.stdout) 

					job["result"] = json.dumps(str(backtracker_result.stdout))


				# Submit results
				try:
					r = requests.put('http://'+self.host+":"+str(serverPort)+'/', data = json.dumps({ "job_id":job["job_id"], "result" : job["result"] }))
				except:
					print("Couldn't send results for job ID ", job["job_id"]," to "+self.host+". Status ", r.status_code, ". Moving on to the next job.")



def client( host ): 

	# Create the threads
	CORES=os.cpu_count()
	if os.environ.get('CPUS') != None:
		CORES=int(os.environ.get('CPUS'))
	if os.environ.get('CORE') != None:
		CORES=int(os.environ.get('CORE'))
	if os.environ.get('CORES') != None:
		CORES=int(os.environ.get('CORES'))

	if CORES < 0:
		CORES=os.cpu_count()-abs(CORES)
	if CORES <= 0:
		CORES=1

	# Start the jobs
	job_threads = []
	for c in range(CORES):
		q_p_c = Queue()
		job_threads.append(client_thread(host, c, q_p_c)) 
	
	for j in job_threads:
		j.start()
	
	j.join()


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


	role = "help"

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

