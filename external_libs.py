# Global Libs
import os
import sys
import ctypes
import random
import subprocess
import filecmp
import multiprocessing

# Local Lib
import defs

#
# This meta-class contains all the helpers to
#   - Generate
#   - Compile
#   - Load
#   - Execute
#
#  External C libraries
#


class External_Libs( defs.Defs ):
	"""Generate, Compile and Load external libs"""

	LIBFOLDER_PUZZLE = ""

	name = ""

	force_compile = False

	EXTRA_NAME = ""
	GCC_EXTRA_PARAMS = "-fsanitize=address"
	LD_EXTRA_PARAMS = ""
	ARCH = ""

	LibExt = None  # Ctype Ext library

	#puzzle = None	# some libs need to get the puzzle parameters

	dependencies = [] # Library dependencies
	LibDep = {}
	
	modules_names = None # Library modules names

	functions_used_list = None

	def __init__( self, skipcompile=False ):
		defs.Defs.__init__( self )
		
		# For each module
		if self.modules_names == None:
			self.modules_names = [ None ]
		
		if self.DEBUG > 3:
			print(self.name, self.modules_names)


		# Lib folder
		self.LIBFOLDER_PUZZLE       = "generated"+"/"+self.HOSTNAME+"/"+self.getFileFriendlyName(self.puzzle.name)+"_"+self.puzzle.scenario.name+self.EXTRA_NAME


		if not os.path.exists( self.LIBFOLDER_PUZZLE ):
			os.makedirs( self.LIBFOLDER_PUZZLE )
			
		# Get the list of functions that are actually used
		self.functions_used_list = []
		self.loadFunctionsUsed()

		# Starts the dependencies
		if self.dependencies != None:
			for d in self.dependencies:
				module = __import__("lib"+d)
				myclass = getattr(module, "Lib"+d.capitalize())
				self.LibDep[ d ] = myclass( self.puzzle, self.EXTRA_NAME, skipcompile )
		
		if not skipcompile:
			# Force recompile
			if os.environ.get('FORCE_COMPILE') != None:
				self.force_compile = True

			if self.force_compile:
				if os.path.exists(self.getNameSO(arch=self.ARCH)):
					os.remove(self.getNameSO(arch=self.ARCH))

			# If .so file is missing we make sure we regenerate
			if not os.path.exists( self.getNameSO(arch=self.ARCH) ):
				for f in [ self.getNameH() ] + self.getNamesC() + self.getNamesPrepro() + self.getNamesASM():
					if os.path.exists(f):
						os.remove(f)

				self.GenerateH_parent()
				for m in self.modules_names:
					if self.DEBUG > 2:
						print("Generating ", m)
					self.GenerateC_parent( m )
				self.Compile()

			# We compile if we detect a change
			elif os.path.getmtime(self.getNamePY()) > os.path.getmtime(self.getNameSO(arch=self.ARCH)):
				self.GenerateH_parent()
				for m in self.modules_names:
					if self.DEBUG > 2:
						print("Updating ", m)
					self.GenerateC_parent( m )
				self.Compile()


		# Do not load the library
		if os.environ.get('NO_LOAD') == None:
			if os.path.exists( self.getNameSO() ):
				self.load()


	# ----- 
	def __del__( self ):
		# Unload the library
		if self.LibExt:
			self.ctypesCloseLibrary()

	# ----- 
	def getModuleStr( self, module=None ):
		if module == None:
			return ""
		else:
			macro = module
			return "_"+macro

		return "./"+self.LIBFOLDER_PUZZLE+"/"+self.name+".makefile"+  (".tmp" if temp else "")

	# ----- 
	def getNameMakefile( self, temp=False, arch="" ):
		if arch != "": arch += "/"
		return "./"+self.LIBFOLDER_PUZZLE+"/"+arch+self.name+".makefile"+  (".tmp" if temp else "")

	# ----- 
	def getNameH( self, temp=False ):
		return "./"+self.LIBFOLDER_PUZZLE+"/"+self.name+".h"+  (".tmp" if temp else "")

	# ----- 
	def getNameC( self, temp=False, module=None ):
		return "./"+self.LIBFOLDER_PUZZLE+"/"+self.name+self.getModuleStr(module)+".c"+ (".tmp" if temp else "")

	# ----- 
	def getNamesC( self, temp=False ):
		return [ self.getNameC(temp, m) for m in self.modules_names ]

	# ----- 
	def getNamePrepro( self, temp=False, module=None ):
		return "./"+self.LIBFOLDER_PUZZLE+"/"+self.name+self.getModuleStr(module)+".preprocessed"+ (".tmp" if temp else "")

	# ----- 
	def getNamesPrepro( self, temp=False ):
		return [ self.getNamePrepro(temp, m) for m in self.modules_names ]

	# ----- 
	def getNameASM( self, temp=False, module=None ):
		return "./"+self.LIBFOLDER_PUZZLE+"/"+self.name+self.getModuleStr(module)+".asm"+ (".tmp" if temp else "")

	# ----- 
	def getNamesASM( self, temp=False ):
		return [ self.getNameASM(temp, m) for m in self.modules_names ]

	# ----- 
	def getNameO( self, temp=False, module=None, arch="" ):
		if arch != "": arch += "/"
		return "./"+self.LIBFOLDER_PUZZLE+"/"+arch+self.name+self.getModuleStr(module)+".o"+ (".tmp" if temp else "")

	# ----- 
	def getNamesO( self, temp=False, arch="" ):
		return [ self.getNameO(temp, m, arch) for m in self.modules_names ]

	# ----- 
	def getNameSO( self, temp=False, arch="" ):
		if arch != "": arch += "/"
		return "./"+self.LIBFOLDER_PUZZLE+"/"+arch+self.name+".so"+ (".tmp" if temp else "")

	# ----- 
	def getNameExe( self, temp=False, arch="" ):
		if arch != "": arch += "/"
		return "./"+self.LIBFOLDER_PUZZLE+"/"+arch+self.name+""+ (".tmp" if temp else "")

	# ----- 
	def getNameFunctionsUsed( self, temp=False ):
		return "./"+self.LIBFOLDER_PUZZLE+"/"+self.name+".functions_used"+ (".tmp" if temp else "")

	# ----- 
	def getNamePY( self ):
		return "./"+self.name+".py"

	# ----- Compilation parameters and arguments
	def getGCC( self ):

		#GCC_CMD = "clang"

		if self.ARCH == "":
			GCC_CMD = "gcc"
		elif self.ARCH == "k1om":
			GCC_CMD="/usr/linux-k1om-4.7/bin/x86_64-k1om-linux-gcc"

		GCC_PARAMS  = ""

		
		if self.DEBUG < 1:
			GCC_PARAMS += " -Os"
		else:
			GCC_PARAMS += " -O0"


		#GCC_PARAMS += " -DNL="		# for debugging preprocessor
		GCC_PARAMS += " -I" + self.LIBFOLDER_PUZZLE + "/"
		GCC_PARAMS += " "+self.GCC_EXTRA_PARAMS
		GCC_PARAMS += " -fPIC -c"
		GCC_PARAMS += " -s"

		return (GCC_CMD, GCC_PARAMS)

	# ----- Compilation parameters and arguments
	def getLD( self ):

		#LD_CMD = "clang"
		
		if self.ARCH == "":
			LD_CMD = "gcc"

		LD_PARAMS  = ""
		LD_PARAMS += " -Wl,-rpath="+self.LIBFOLDER_PUZZLE+"/" # pass the Library Search Path to the linker
		#LD_PARAMS += " -ftime-report"
		#LD_PARAMS += " -shared"
		LD_PARAMS += " "

		LD_LIBS  = ""
		LD_LIBS += " -L" + self.LIBFOLDER_PUZZLE + "/"
		LD_LIBS += " "+self.LD_EXTRA_PARAMS
		LD_LIBS += " "

		if self.dependencies != None:
			for d in self.dependencies:
				LD_LIBS += " -l"+d
		
		return (LD_CMD, LD_PARAMS, LD_LIBS)



	# ----- Compile library at execution time
	def Compile( self ):

		# Check that we have something to compile
		if not os.path.exists( self.getNameH(temp=True) ):
			if self.DEBUG > 1:
				print( self.getNameH(temp=True) + " doesn't exists, cannot compile" )
			return

		os.rename( self.getNameH( temp=True ), self.getNameH( temp=False ) )

		(GCC_CMD, GCC_PARAMS) = self.getGCC()
		(LD_CMD, LD_PARAMS, LD_LIBS) = self.getLD()

		arch=self.ARCH
	
		# Default targets
		output = [
			( 0, "all: " + self.getNameSO(arch=arch) ),
			#( 0, "main:"   ),
			#( 1, "@gcc -I. -L . -s -static ./*.o -o main" ),
			#( 0, "perf:" ),
			#( 1, "@perf stat -d ./main" ),
			( 0, "exe: " + self.getNameExe(arch=arch) ),
			( 0, "prepro: "+ " ".join([ self.getNamePrepro( module=module ) for module in self.modules_names ]) ),
			( 0, "asm: "+ " ".join([ self.getNameASM( module=module ) for module in self.modules_names ]) ),
			]

		# Build the list of module to compile
		for module in self.modules_names:

			# Check that we have something to compile
			if not os.path.exists( self.getNameC(temp=True, module=module) ):
				if self.DEBUG > 1:
					print( self.getNameC(temp=True, module=module) + " doesn't exists, cannot compile" )
				continue
			
			# we compare the temporary H+C files with last compiled ones
			if os.path.exists( self.getNameC(temp=False, module=module) ):
				if filecmp.cmp( self.getNameC( temp=True, module=module ), self.getNameC( temp=False, module=module ) ):
					# Remove temporary file
					os.remove( self.getNameC( temp=True, module=module ) )
					if self.DEBUG > 3:
						print( " [x] No new code to compile for " + self.name )
				else:
					# We now use the new file for compiling by letting the Makefile finding the new file
					os.rename( self.getNameC( temp=True, module=module ), self.getNameC( temp=False, module=module ) )
			else:
				# We now use the new file for compiling by letting the Makefile finding the new file
				os.rename( self.getNameC( temp=True, module=module ), self.getNameC( temp=False, module=module ) )


			# Preprocessed for debugging
			NLTAG="newlineplease"

			GCC_FILES = " "+ self.getNameC( module=module )+" -o "+self.getNamePrepro( module=module )
			output.extend( [ 
				( 0, self.getNamePrepro( module=module )+": "+self.getNameH()+" "+self.getNameC( module=module ) ),
				( 1, '@echo ' + self.getNamePrepro( module=module )),
				( 1, "@" + GCC_CMD + GCC_PARAMS + " -DNL="+NLTAG+" -E " + GCC_FILES ),
				( 1, "@sed -i -e 's/"+NLTAG+"/\\n/g' " + self.getNamePrepro( module=module )),
				] )
				
			# ASM for debugging
			GCC_FILES = " "+ self.getNameC( module=module )+" -o "+self.getNameASM( module=module )
			output.extend( [ 
				( 0, self.getNameASM( module=module )+": "+self.getNameH()+" "+self.getNameC( module=module ) ),
				( 1, '@echo ' + self.getNameASM( module=module )),
				( 1, "@" + GCC_CMD + GCC_PARAMS + " -DNL="+NLTAG+" -S -masm=intel " + GCC_FILES),
				] )
		
			# Compile with GCC
			GCC_FILES = " "+self.getNameC( module=module )+" -o "+self.getNameO( module=module, arch=arch )
			output.extend( [ 
				( 0, self.getNameO( module=module, arch=arch )+": "+self.getNameH()+" "+self.getNameC( module=module ) ),
				( 1, '@echo ' + self.getNameO( module=module, arch=arch )),
				( 1, "@" + GCC_CMD + GCC_PARAMS + GCC_FILES),
				] )


		# Link the modules into the library
		LD_FILES = " "+ " ".join(self.getNamesO(arch=arch))+" -o "+self.getNameSO(arch=arch)
		output.extend( [ 
			( 0, self.getNameSO(arch=arch)+": "+ " ".join([ self.getNameO( module=module, arch=arch ) for module in self.modules_names ]) + " " + self.getNameFunctionsUsed() ),
			( 1, '@echo ' + self.getNameSO(arch=arch)),
			( 1, "@" + LD_CMD + " -shared" + LD_PARAMS + LD_FILES + LD_LIBS ),
			] )

		# Link the modules into the executable
		LD_FILES = " "+ " ".join(self.getNamesO(arch=arch))+" -o "+self.getNameExe(arch=arch)
		output.extend( [ 
			( 0, self.getNameExe(arch=arch)+": "+ " ".join([ self.getNameO( module=module, arch=arch ) for module in self.modules_names ]) + " " + self.getNameFunctionsUsed() ),
			( 1, '@echo ' + self.getNameExe(arch=arch)),
			#( 1, "@" + LD_CMD + " -static" + LD_PARAMS + LD_FILES + LD_LIBS ),
			( 1, "@" + LD_CMD + LD_PARAMS + LD_FILES ),
			] )

		# Write Makefile
		gen = open( self.getNameMakefile(temp=False, arch=arch), "w" )
		self.writeGen( gen, output  )
		gen.close()

		# Setup the targets
		targets=[]
		if os.environ.get('PREPRO') != None:
			targets.append("prepro")
		if os.environ.get('ASM') != None:
			targets.append("asm")
		if os.environ.get('NO_COMPILE') == None:
			targets.append(self.getNameSO(arch=arch))

		# Start makefile
		if len(targets) > 0:
			CMD="make -j " + str(multiprocessing.cpu_count()) + " -f " + self.getNameMakefile(temp=False, arch=arch) + " " + " ".join(targets)
			if self.DEBUG > 1:
				print( CMD )

			if self.DEBUG > 0:
				os.system( CMD )
			else:
				print( " o Compiling",self.name,"... ", end="" )
				sys.stdout.flush()
				(val, output) = subprocess.getstatusoutput( CMD )

				if val != 0:
					print()
					print(output)
					return val
				else:
					if self.DEBUG > 1:
						print()
						print(CMD)
						print(output)
						print()
					else:
						print( "Done." )

	

			
	# ----- write into a file
	def writeGen( self, gen, a, extra=0, debug_code=False ):
		for (t, c) in a:
			s = "\t" * (t+extra) + c + "\n"
			gen.write(s)


	# ----- write into a file
	def GenerateH_parent( self ):
		self.GenerateH()
		self.printDebugTime( 2, 99, "Generate " + self.getNameH() )

	# ----- write into a file
	def GenerateC_parent( self, m ):
		self.GenerateC( m )
		self.printDebugTime( 2, 99, "Generate " + self.getNameC() + " module " + str( m ) )

	# ----- get some generic Header for H
	def getHeaderH( self ):
		header = [ 
			( 0, "// This File is Generated"),
			( 0, ""),
			( 0, "#include <stdio.h>"),
			( 0, "#include <time.h>     // for time"),
			( 0, "#include <signal.h>   // for signals"),
			( 0, "#include <stdint.h>   // for uint32"),
			( 0, "#include <unistd.h>   // for sleep"),
			( 0, "#include \"stdlib.h\" // for malloc/realloc"),
			( 0, ""),
			( 0, '#ifndef ' + self.name.upper() + "_H" ),
			( 0, '#define ' + self.name.upper() + "_H" ),
			( 0, '' ),
		]

		if self.dependencies != None:
			for d in self.dependencies:
				header.append( (0, "#include <lib"+d+".h>"), )

		header.append(	( 0, '' ), )

		if self.puzzle != None:
			header.extend( [ 
				(0, "#define WH " + str(self.puzzle.board_wh)),
				(0, "#define W " + str(self.puzzle.board_w)),
				(0, "#define H " + str(self.puzzle.board_h)),
				(0, '' ),
			])

		return header

	# ----- get some generic Footer for H
	def getFooterH( self ):
		footer = [ 
			( 0, '' ),
			( 0, '#endif' ),
		]
		return footer


	# ----- get some generic Header for C
	def getHeaderC( self, module=None ):

		(GCC_CMD, GCC_PARAMS) = self.getGCC()
		#(LD_CMD, LD_PARAMS) = self.getLD()
		GCC_FILES = " "+self.getNameC(module=module)+" -o "+self.getNameO(module=module, arch=self.ARCH)
		header = [ 
			(0, "// This File is Generated"),
			(0, ""),
			(0, "/* Compiled with: \n"+ GCC_CMD + "\\\n" + GCC_PARAMS.replace(" ", " \\\n") + GCC_FILES + "\\\n" + "\n*/"),
			#(0, "/* Linked with: \n"+ LD_CMD + "\\\n" + LD_PARAMS.replace(" ", " \\\n") + LD_FILES + "\\\n" + "\n*/"),
			(0, ""),
			(0, "#include <"+ self.name +".h>" ),
			(0, ""),
		]
		return header

	# ----- get some generic Footer for C
	def getFooterC( self ):

		footer = [ 
			(0, ""),
			(0, ""),
			(0, "/* Lapin */"),
		]

		return footer

	# ----- Get function name from the signature lines
	def getFunctionNameFromSignature(self, lines):
		for (tab, l) in lines:
			if "(" in l:
				if l.startswith("void "):
					return l.replace("void ","").rstrip("(")
				elif l.startswith("voidp "):
					return l.replace("voidp ","").rstrip("(")
				elif l.startswith("p_blackwood "):
					return l.replace("p_blackwood ","").rstrip("(")
				elif l.startswith("int "):
					return l.replace("int ","").rstrip("(")
				elif l.startswith("uint64 "):
					return l.replace("uint64 ","").rstrip("(")
		return None

	# ----- Get function name from the signature lines
	def getFunctionTypeFromSignature(self, lines):
		for (tab, l) in lines:
			if "(" in l:
				if l.startswith("void "):
					return ctypes.c_void_p
				elif l.startswith("voidp "):
					return ctypes.c_void_p
				elif l.startswith("p_blackwood "):
					return ctypes.c_void_p
				elif l.startswith("int "):
					return ctypes.c_int
				elif l.startswith("uint64 "):
					return ctypes.c_ulonglong
		return None

	# ----- Get function parameters types from signature lines
	def getParametersTypesFromSignature(self, lines):
		t = []
		for (tab, l) in lines:
			if not "(" in l:
				if l.startswith("uint64 "):
					t.append( ctypes.c_ulonglong )
				elif l.startswith("uint64p "):
					t.append( ctypes.c_void_p )
				elif l.startswith("p_blackwood "):
					t.append( ctypes.c_void_p )
				elif l.startswith("voidp "):
					t.append( ctypes.c_void_p )
				elif l.startswith("FILEp "):
					t.append( ctypes.c_void_p )
				elif l.startswith("charp "):
					t.append( ctypes.c_char_p )
		return t

	# ----- Get function parameters names from signature lines
	def getParametersNamesFromSignature(self, lines):
		t = []
		for (tab, l) in lines:
			if not "(" in l:
				if (l.startswith("uint64 ") or
				    l.startswith("uint64p ") or
				    l.startswith("p_blackwood ") or
				    l.startswith("voidp ") or
				    l.startswith("charp ")):
					t.append( l.split(" ")[-1].rstrip(",") )
		return t

	# ----- Get function name from the signature lines
	def getFunctionCallFromSignature(self, lines, prefix=""):
		tab_name = 0
		name=""
		t = []
		for (tab, l) in lines:
			if (l.startswith("uint64 ") or
			    l.startswith("uint64p ") or
			    l.startswith("voidp ") or
			    l.startswith("charp ")):
				t.append( (tab, prefix+l.split(" ")[-1]) )
			elif l.startswith("void "):
				t.append( (tab, l.replace("void ","")) )
				tab_name = tab
				name=l.replace("void ","").strip('(')
			else:
				t.append( (tab, l) )

		if self.DEBUG > 2:
			debug = [ (tab_name, 'DEBUG_PRINT(("' + name + ' : Start\\n" ))') ]
			debug.extend(t)
			debug.append( (tab_name, 'DEBUG_PRINT(("' + name + ' : End\\n" ))') )
			return debug

		return t
	
	# ----- Define args and restype from signatures lines  -- for calls directly from Python
	def defineFunctionsArgtypesRestype( self, lines ):
		signature =  []
		for (tab, l) in lines:
			signature.append((tab, l))
			if l.endswith( ");" ):

				name     = self.getFunctionNameFromSignature(signature)
				restype  = self.getFunctionTypeFromSignature(signature)
				argtypes = self.getParametersTypesFromSignature(signature)

				if self.DEBUG > 4:
					print(name, " : ", argtypes, "->", restype)
		
				f = getattr(self.LibExt, name )
				f.restype = restype
				f.argtypes = argtypes
				
				signature = []
			

	# ----- Call an external library function from LibExt with functionNames and Parameters
	def LibExtWrapper(self, functionName, args, timeit=False): # without star
		if self.DEBUG in [4]:
			import re
			print( "Calling", functionName )
			sys.stdout.flush()
		if self.DEBUG > 4:
			import re
			args_str = str(args)
			args_str = re.sub("<multiprocessing.sharedctypes.c_ulong_Array_([0-9]*) object at 0x[0-9a-f]*>", "Array[\\1]", args_str)
			print( "Calling", functionName, "with", args_str)
			sys.stdout.flush()
		f = getattr(self.LibExt, functionName )
		if timeit:
			r = random.randint(0, sys.maxsize)
			self.top( functionName+str(r) )
			result = f(*args)
			print( functionName, "took", self.top( functionName+str(r) ), "to execute" )
		else:
			result = f(*args)
			
		if self.DEBUG > 4:
			print( "Return ", functionName)
			sys.stdout.flush()

		return result

	# ----- 
	def output_extend( self, output, tab, lines ):
		for (t, l) in lines:
			t += tab
			output.extend( [ (t, l ) ] )

	# ----- 
	def removeComaOnLastLine( self, lines ):
		(t, l) = lines[-1]
		lines[-1] = (t, l.rstrip(','))
		return lines
	
	# ----- 
	def defineWrapper( self, output, tab, define_list ):
		undefine_list = []
		max_len_d = 0
		for (d, r) in define_list:
			if len(d) > max_len_d:
				max_len_d = len(d)
		#print(max_len_d)
			
		for (d, r) in define_list:
			output.append(        (tab, '#define '+d.ljust(max_len_d, " ")+"   "+r) )
			undefine_list = [(tab, '#undef '+d ) ] + undefine_list

		return undefine_list
	
	# ----- 
	def replaceDefines( self, output, define_list ):
		new_output = []
		import re

		# Create a regular expression from the dictionary keys
		d = {}
		for (old, new) in define_list:
			d[old] = new
		regex = re.compile("(%s)" % "|".join(map(re.escape, d.keys() )))


		for (t, s) in output:
			# For each match, look-up corresponding value in dictionary
			ns = regex.sub(lambda mo: d[mo.string[mo.start():mo.end()]], s) 
			new_output.append( (t, ns) )

		return new_output
				
	# ----- 
	def loadFunctionsUsed( self ):

		if not os.path.exists( self.getNameFunctionsUsed() ):
			f = open(self.getNameFunctionsUsed(), 'w')
			f.write('# Generated file - delete to regenerate\n')
			f.close()

			if self.DEBUG > 2:
				print( self.name , "doesn't know yet its function used list" )
		else:
			f = open(self.getNameFunctionsUsed(), 'r')
			c = 0
			for line in f:
				if not line.startswith('#'):
					self.functions_used_list.append( line.strip('\n') )
			f.close()

			if self.DEBUG > 2:
				print( self.name , "has", len(self.functions_used_list), "function used" )

	# ----- 
	def addFunctionsUsed( self, function_name ):
		if function_name not in self.functions_used_list:
			f = open(self.getNameFunctionsUsed(), 'a')
			f.write( function_name+'\n' )
			f.close()

			self.functions_used_list.append(function_name)


	# ----- 
	def ctypesCloseLibrary( self ):
		if self.DEBUG > 2:
			print( "Closing opened library", self.name )
		
		dlclose_func = ctypes.CDLL(None).dlclose
		dlclose_func.argtypes = [ctypes.c_void_p]
		dlclose_func.restype = ctypes.c_int

		dlclose_func(self.LibExt._handle)

