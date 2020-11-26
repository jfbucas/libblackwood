
# Global Libs
import os
import ctypes

# Local Libs
import external_libs

#
# Generates definitions
#


class LibDefs( external_libs.External_Libs ):
	"""Definitions for External Libraries"""

	def __init__( self, puzzle, extra_name="" ):

		self.name = "libdefs"
		
		self.puzzle = puzzle

		# Params for External_Libs
		self.EXTRA_NAME = extra_name
		self.dependencies = [ ]
		self.GCC_EXTRA_PARAMS = ""

		external_libs.External_Libs.__init__( self )

	# ----- Load the C library
	def load( self ):

		self.LibExt = ctypes.cdll.LoadLibrary( self.getNameSO() )


	# ----- generate LibGen Header
	def GenerateH( self ):

		gen = open( self.getNameH(temp=True), "w" )

		self.writeGen( gen, self.getHeaderH() )

		defs_const = [
			( 0, '// Defines a few Constants' ),
			( 0, '' ),
			( 0, '#define TYPE_CORNER	' + str(self.TYPE_CORNER)),
			( 0, '#define TYPE_BORDER	' + str(self.TYPE_BORDER)),
			( 0, '#define TYPE_CENTER	' + str(self.TYPE_CENTER)),
			( 0, '#define TYPE_FIXED	' + str(self.TYPE_FIXED)),
			( 0, '#define EDGE_UP		' + str(self.EDGE_UP)),
			( 0, '#define EDGE_RIGHT	' + str(self.EDGE_RIGHT)),
			( 0, '#define EDGE_DOWN		' + str(self.EDGE_DOWN)),
			( 0, '#define EDGE_LEFT		' + str(self.EDGE_LEFT)),
			( 0, '#define EDGE_SHIFT_LEFT	' + str(self.EDGE_SHIFT_LEFT)),
			( 0, '' ),
			]
		self.writeGen( gen, defs_const )

		defs = [
			( 0, '// Defines a few types and Macros' ),
			( 0, '' ),
			( 0, 'typedef unsigned int		uint;' ),
			( 0, 'typedef unsigned long long int	uint64;' ),
			( 0, 'typedef uint32_t			uint32;' ),
			( 0, 'typedef unsigned short		uint16;' ),
			( 0, 'typedef unsigned char		uint8;' ),
			( 0, 'typedef   signed long long int	int64;' ),
			( 0, 'typedef int32_t			int32;' ),
			( 0, 'typedef   signed short		int16;' ),
			( 0, 'typedef   signed char		int8;' ),
			( 0, '' ),
			( 0, 'typedef uint * 			uintp;' ),
			( 0, 'typedef uint32 *			uint32p;' ),
			( 0, 'typedef uint64 *			uint64p;' ),
			( 0, '' ),
			( 0, 'typedef char *			charp;' ),
			( 0, 'typedef void *			voidp;' ),
			( 0, 'typedef FILE *			FILEp;' ),
			( 0, '' ),
			]

		if self.DEBUG > 0:
			defs.extend( [  (0, "#define DEBUG " + str(self.DEBUG)), ] )
			defs.extend( [	(1, '#define DEBUG_PRINT(x) printf x;  fflush (stdout);'), ] )
			defs.extend( [	(1, '#define DEBUG_DO(x) x;'), ] )
			if self.DEBUG > 1:
				defs.extend( [	(1, '#define DEBUG_DEADEND(...) printf(__VA_ARGS__);  fflush (stdout);'), ] )
			else:
				defs.extend( [	(1, '#define DEBUG_DEADEND(...) ;'), ] )

			for i in range(self.DEBUG+1):
				defs.extend( [	(1, '#define DEBUG'+str(i)+'(...) printf(__VA_ARGS__);  fflush (stdout);'), ] )
				defs.extend( [	(1, '#define DEBUG'+str(i)+'_PRINT(...) printf(__VA_ARGS__);  fflush (stdout);'), ] )
				defs.extend( [	(1, '#define DEBUG'+str(i)+'_DO(x) x;'), ] )

			for i in range(self.DEBUG+1, 10):
				defs.extend( [	(1, '#define DEBUG'+str(i)+'(...) ;'), ] )
				defs.extend( [	(1, '#define DEBUG'+str(i)+'_PRINT(...) ;'), ] )
				defs.extend( [	(1, '#define DEBUG'+str(i)+'_DO(x) ;'), ] )
		else:
			defs.extend( [	(1, '#define DEBUG_PRINT(x) ;'), ] )
			defs.extend( [	(1, '#define DEBUG_DO(x) ;'), ] )
			defs.extend( [	(1, '#define DEBUG_DEADEND(...) ;'), ] )
			for i in range(10):
				defs.extend( [	(1, '#define DEBUG'+str(i)+'(x) ;'), ] )
				defs.extend( [	(1, '#define DEBUG'+str(i)+'_DO(x) ;'), ] )
			
		self.writeGen( gen, defs )

		self.writeGen( gen, self.getFooterH() )

	# ----- generate LibGen
	def GenerateC( self, module=None ):
		
		gen = open( self.getNameC(temp=True), "w" )

		self.writeGen( gen, self.getHeaderC() )

		self.writeGen( gen, self.getFooterC() )


if __name__ == "__main__":
	lib = LibDefs()
