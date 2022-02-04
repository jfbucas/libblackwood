
# Global libs
import os
import time
import math
from itertools import combinations
import subprocess

#
# Defines various general variables
#


class Defs():
	"""Definitions accross the various classes"""

	# 
	DEBUG = 0
	DEBUG_STATIC = 0
	DEBUG_TIME = 0
	DEBUG_STATS = 0
	DEBUG_PERF = 0
	QUIET = False

	NICE = 19
	
	HOSTNAME    = ""

	DESKTOP		= False

	topTime = { }

	MAX_NB_PIECES = 256
	MAX_NB_COLORS = 32

	EDGE_SHIFT_LEFT = 5

	EDGES_PER_PIECE = 4

	TYPE_OUTTER = 0
	TYPE_CORNER = 1
	TYPE_BORDER = 2
	TYPE_CENTER = 4
	TYPE_FIXED  = 8
	TYPE_DEFAULT = TYPE_CENTER
	TYPE_STR = [ "none", "corner", "border", "center" ] + [ "fixed" ] * 256


	EDGE_UP		= 0
	EDGE_RIGHT	= 1
	EDGE_DOWN	= 2
	EDGE_LEFT	= 3
	EDGE_MIDDLE	= 4
	EDGES_STR	= [ "up", "right", "down", "left", "middle" ]
	EDGES_OPP_STR	= [ "down", "left", "up", "right" ]

	REF_NONE	= 0
	REF_UP		= 1
	REF_RIGHT	= 2
	REF_DOWN	= 4
	REF_LEFT	= 8

	# Terminal Display colors & co.
	noire =   '0'
	noire_clair =   '0'
	grise = '244'
	grise_clair = '252'
	grise_board = '246'
	dbleu =  '60'
	dbleu_clair = '103'
	lbleu =  '74'
	lbleu_clair = '117'
	violi =  '97'
	violi_clair = '140'
	verta =  '71'
	verta_clair = '114'
	pinki = '168'
	pinki_clair = '211'
	maron =  '95'
	maron_clair = '138'
	jaune = '220'
	jaune_clair = '227'
	oranj = '172'
	oranj_clair = '215'
	nwhite = '255'


	rougeoie	= "\033"+'[38;5;196m'
	orangeoie	= "\033"+'[38;5;166m'
	oranjaunoie	= "\033"+'[38;5;178m'
	jaunoie		= "\033"+'[38;5;214m'
	verdoie		= "\033"+'[38;5;22m'
	bleuoie		= "\033"+'[38;5;33m'
	violoie		= "\033"+'[38;5;97m'
	noiroie		= "\033"+'[38;5;0m'
	rainbow = []

	XTermEnv	= "\033[48;5;"+noire+'m'+"\033"+'[38;5;'+jaune_clair+'m'
	XTermInfo	= "\033[48;5;"+noire+'m'+"\033"+'[38;5;'+verta+'m'
	XTermError	= "\033[48;5;"+noire+'m'+"\033"+'[38;5;'+oranj+'m'
	XTermNormal	= "\033[0m"

	# http://www.termsys.demon.co.uk/vtansi.htm
	XTermSaveCursor = "\033[s" # //  "\033[7" 
	XTermLoadCursor = "\033[u" # //  "\033[8" 
	XTermClearScr   = "\033[2J\033[H" 
        #XTermCursorMoveBack( x )  "\033["x"D" 

	TITLE_STR	= rougeoie + 'Eternity ' + jaunoie + 'II ' + bleuoie + 'Solver ' + orangeoie + '- ' + verdoie
	H1_OPEN		= 'x-]'+XTermInfo+'  '
	H1_CLOSE	= '  '+XTermNormal+'[-x'


	# ----- Init the puzzle
	def __init__( self ):


		if os.environ.get('QUIET') != None:
			self.QUIET = True

		if os.environ.get('DEBUG') != None:
			self.DEBUG = int(os.environ.get('DEBUG'))
			if self.DEBUG > 3:
				print(self.XTermEnv+'[ Debug mode enabled :', self.DEBUG, ']', self.XTermNormal)

		if os.environ.get('DEBUG_STATIC') != None:
			self.DEBUG_STATIC = int(os.environ.get('DEBUG_STATIC'))
			if self.DEBUG_STATIC > 1:
				print(self.XTermEnv+'[ Debug Static Data:', self.DEBUG_STATIC, ']', self.XTermNormal)

		self.DEBUG_STATS = self.DEBUG
		if os.environ.get('DEBUG_STATS') != None:
			self.DEBUG_STATS = int(os.environ.get('DEBUG_STATS'))
			if self.DEBUG_STATS > 1:
				print(self.XTermEnv+'[ Debug Stats mode enabled :', self.DEBUG_STATS, ']', self.XTermNormal)

		if os.environ.get('DEBUG_PERF') != None:
			self.DEBUG_PERF = int(os.environ.get('DEBUG_PERF'))
			if self.DEBUG_PERF > 1:
				print(self.XTermEnv+'[ Debug Perf mode enabled :', self.DEBUG_PERF, ']', self.XTermNormal)

		if os.environ.get('HOSTNAME') != None:
			self.HOSTNAME = os.environ.get('HOSTNAME')
		else:
			from socket import getfqdn
			self.HOSTNAME = getfqdn()
			if self.DEBUG > 7:
				print(self.XTermEnv+'[ HOSTNAME: '+ self.HOSTNAME +' ]', self.XTermNormal)

		if os.environ.get('DESKTOP') != None:
			print(self.XTermEnv+'[ Machine is a Desktop ]', self.XTermNormal)
			self.DESKTOP = True

		if os.environ.get('NICE') != None:
			self.NICE = int(os.environ.get('NICE'))
		os.nice(self.NICE)


		# Generate rainbow colors
		# For 32 colors
		nb_rainbow = 32
		freq = 0.15
		# For 16 colors
		nb_rainbow = 16
		freq = 0.30
		rainbow_func = lambda i, a, b: int(6 * (math.sin(freq * i + a * math.pi/3) * 127 + 128) / 256) * b
		for i in range(0,nb_rainbow):
			self.rainbow.append( '\033[38;5;'+ str( sum([16, rainbow_func(i, 0, 36), rainbow_func(i, 2, 6), rainbow_func(i, 4, 1)]) ) + "m" )

		if self.DEBUG_STATIC > 0:
			for i in range(0,nb_rainbow):
				print(self.rainbow[i],"###", end=" ")
			print(self.XTermNormal)

		# TRUECOLOR would be better but not available yet in GNU/screen packages
		#printf "\x1b[38;2;255;100;0mTRUECOLOR\x1b[0m\n"

	# Get the git tag
	def git( self ):
		# Get the get version
		return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()


	# ----- Debug
	def printDebug( self, min_debug_level=1, top=0, msg="" ):
		"""Print Debug"""
		if self.DEBUG >= min_debug_level:
			if top>0:
				print( msg, "(in ", self.top(top), ")" )
			else:
				print( msg )

	# ----- DebugTiming
	def printDebugTime( self, min_debug_time_level=1, top=0, msg="" ):
		"""Print Debug and timing"""
		if self.DEBUG_TIME >= min_debug_time_level:
			if top>0:
				print( msg, "(in ", self.top(top), ")" )
			else:
				print( msg )

	# ----- Error printing
	def error( self, msg="" ):
		"""Print Error"""
		print( self.XTermError + msg + self.XTermNormal)

	# ----- Info printing
	def info( self, msg="" ):
		"""Print Info"""
		print( self.XTermInfo + msg + self.XTermNormal )

	# ----- Chronos is the key
	def top( self, n=0, unit=True ):
		"""Chronos is the key"""

		if not n in self.topTime:
			self.topTime[ n ] = 0
		r = "%.2f" % (time.time() - self.topTime[ n ] ) + ("s" if unit else "")
		self.topTime[ n ] = time.time()
		return r



	
	# ----- return the filename for pre-computed data
	def getFileFriendlyName( self, name ):
		"""Return the friendly filename"""
		return name.replace("/","_").replace(".js","")


	# ----- Print an array
	def printArray( self, a, b=None, c=None, d=None, e=None, steps=1, array_wh=0, array_w=0, array_h=0, max_len=None, sep=" ", prefix="", translator=None, divideby=1, comma=False, noprint=False, replacezero=False, replaceone=False ):
		"""Print an array"""

		# get the chaine de caractere
		def get_str( x ):
			result=""
			if translator:
				if type(x) is str or x is None:
					result=translator[x]
				else:
					result=translator[x//divideby]
			elif comma:
				if type(x) is str or x is None:
					result="{:,}".format(x)
				else:
					result="{:,}".format(x//divideby)
			else:
				if (type(x) is str) or (type(x) is list) or (x is None):
					result=str(x)
				else:
					result=str(int(x)//divideby)

			if replacezero and result == "0":
				result="."

			if replaceone and result == "1":
				result="!"

			return result
				


		max_a = max_b = max_c = max_d = max_e = 0
		if max_len != None:
			max_a = max_b = max_c = max_d = max_e = max_len
		else:
			if array_wh == 0:
				array_wh = array_w * array_h

			for s in range( array_wh ):
				if max_a < len(get_str(a[ s ])):
					max_a = len(get_str(a[ s ]))
				if b and max_b < len(get_str(b[ s ])):
					max_b = len(get_str(b[ s ]))
				if c and max_c < len(get_str(c[ s ])):
					max_c = len(get_str(c[ s ]))
				if d and max_d < len(get_str(d[ s ])):
					max_d = len(get_str(d[ s ]))
				if e and max_e < len(get_str(e[ s ])):
					max_e = len(get_str(e[ s ]))

		sepb = sepc = sepd = sepe = ""
		if b:
			sepb = "|"
		if c:
			sepc = "|"
		if d:
			sepd = "|"
		if e:
			sepe = "|"
			
		output_total = ""
		for h in range( 0, array_h, steps ):
			
			output_a = ""
			output_b = ""
			output_c = ""
			output_d = ""
			output_e = ""

			for w in range( 0, array_w, steps ):
				s = w+ h*array_w
				output_a += get_str(a[ s ]).rjust(max_a, " ") + sep
				if b:
					output_b += get_str( b[ s ] ).rjust(max_b, " ") + sep
				if c:
					output_c += get_str( c[ s ] ).rjust(max_c, " ") + sep
				if d:
					output_d += get_str( d[ s ] ).rjust(max_d, " ") + sep
				if e:
					output_e += get_str( e[ s ] ).rjust(max_e, " ") + sep

			output_total += prefix+output_a+sepb+output_b+sepc+output_c+sepd+output_d+sepe+output_e+"\n"

		if noprint == False:
			#sys.stdout.buffer.write( output_a + sepb + output_b + sepc + output_c + sepd + output_d )
			print( output_total )
		else:
			return output_total

	# ----- Print an array in the shape of the block
	def printBlockArray( self, a, b=None, c=None, d=None, steps=1 ):
		"""Print an array in the shape of the block"""
		self.printArray(a, b, c, d, steps, 16, 4, 4)



	# ----- Self test
	def SelfTest( self ):
		print( )
		print( self.H1_OPEN + self.TITLE_STR + self.H1_CLOSE )
		print( )


if __name__ == "__main__":
	d = Defs()

	d.SelfTest()
