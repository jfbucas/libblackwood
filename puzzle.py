# Global Libs
import os
import sys
import time
import datetime
import select
import random
import multiprocessing
import ctypes

# Local Libs
import defs
import scenarios


#
# Pieces, Rotations, Lists, Puzzle 
#

class Piece():
	p = 0
	u = 0
	r = 0
	d = 0
	l = 0
	fixed = False

	def __init__(self, p, u,r,d,l, fixed=False):
		self.p = p
		self.u = u
		self.r = r
		self.d = d
		self.l = l
		self.fixed = fixed

	def __str__(self):
		return str(self.p)+"["+str(self.u)+","+str(self.r)+","+str(self.d)+","+str(self.l)+"]"
	def __repr__(self):
		return str(self.p)+"["+str(self.u)+","+str(self.r)+","+str(self.d)+","+str(self.l)+"]"

	def getEdges( self ):
		return [ self.u, self.r, self.d, self.l ]

	# ----- Return if is a corner
	def isCorner( self ):
		"""Return is a corner"""
		return (((self.u == 0) and (self.r == 0 )) or 
			 ((self.r == 0) and (self.d == 0 )) or 
			 ((self.d == 0) and (self.l == 0 )) or 
			 ((self.l == 0) and (self.u == 0 )))

	# ----- Return if is a border
	def isBorder( self ):
		"""Return is a border"""
		return ((self.u == 0) or
			(self.r == 0) or
			(self.d == 0) or
			(self.l == 0)) and not self.isCorner()

	# ----- Return if is a center(aka not special)
	def isCenter( self ):
		"""Return is center (aka not special)"""
		return ( not self.isCorner() and not self.isBorder() )

	# ----- Return if is a center(aka not special)
	def isFixed( self ):
		"""Return is fixed"""
		return self.fixed

	def turnCW(self):
		(self.u, self.r, self.d, self.l) = (self.l, self.u, self.r, self.d)

	def turnCCW(self):
		(self.u, self.r, self.d, self.l) = (self.r, self.d, self.l, self.u)

class RotatedPiece():
	p = 0
	rotation = 0
	u = 0
	r = 0
	d = 0
	l = 0
	conflicts_count = 0
	heuristic_side_count = 0

	def __init__(self, p, rotation, u, r, d, l, b, h):
		self.p = p
		self.rotation = rotation
		self.u = u
		self.r = r
		self.d = d
		self.l = l
		self.conflicts_count = b
		self.heuristic_side_count = h

	def __str__(self):
		return str(self.p).zfill(3)+"["+str(self.conflicts_count)+"/"+str(self.heuristic_side_count)+":"+chr(ord('a')+self.r)+chr(ord('a')+self.d)+"]"
	def __repr__(self):
		return str(self.p).zfill(3)+"["+str(self.conflicts_count)+"/"+str(self.heuristic_side_count)+":"+chr(ord('a')+self.r)+chr(ord('a')+self.d)+"]"

class RotatedPieceWithDownLeft():
	l_u = 0
	score = 0
	rotated_piece = None

	def __init__(self, l_u, score, rotated_piece):
		self.l_u = l_u
		self.score = score
		self.rotated_piece = rotated_piece

	def __str__(self):
		return str(self.l_u)+":"+str(self.rotated_piece.p+1)+"("+str(self.score)+")"
	def __repr__(self):
		return str(self.l_u)+":"+str(self.rotated_piece.p+1)+"("+str(self.score)+")"


class Puzzle( defs.Defs ):
	"""Defines properties for a puzzle"""

	name = ""

	board_w = 0
	board_h = 0
	board_wh = 0

	pieces = []
	fixed = []

	nb_colors_border = 0
	nb_colors_center = 0

	static_colors_border_count = {}
	static_colors_center_count = {}

	# Precomputed statistics
	stats = None

	# ----- Init the puzzle
	def __init__( self ):
		"""
		Initialize
		"""

		defs.Defs.__init__( self )

		self.board_wh = self.board_w * self.board_h
	
		self.TITLE_STR += self.name

		self.normalizePieces()		# Make sure the pieces are how we expect them to be

		self.initStaticColorsCount()

		self.readStatistics()

		self.scenario = scenarios.loadScenario(self)

		# The Seed for the Generator
		self.seed = random.randint(0, sys.maxsize)
		if os.environ.get('SEED') != None:
			self.seed = int(os.environ.get('SEED'))
			if self.DEBUG > 0:
				self.info(" * Init Puzzle Env Seed : "+str(self.seed) )
	


		# Prepare the list of lists of pieces
		( self.master_index, self.master_lists_of_rotated_pieces, self.master_all_rotated_pieces ) = self.prepare_pieces()
	


	# ----- Return if Pieces[ p ] is a corner
	def isPieceCorner( self, p ):
		"""Return if Pieces[ p ] is a corner"""
		return (((p[ 0 ] == 0) and (p[ 1 ] == 0 )) or 
			 ((p[ 1 ] == 0) and (p[ 2 ] == 0 )) or 
			 ((p[ 2 ] == 0) and (p[ 3 ] == 0 )) or 
			 ((p[ 3 ] == 0) and (p[ 0 ] == 0 )))

	# ----- Return if Pieces[ p ] is a border
	def isPieceBorder( self, p ):
		"""Return if Pieces[ p ] is a border"""
		return ((p[ 0 ] == 0) or
			(p[ 1 ] == 0) or
			(p[ 2 ] == 0) or
			(p[ 3 ] == 0)) and not self.isPieceCorner(p)

	# ----- Return if Pieces[ p ] is a center(aka not special)
	def isPieceCenter( self, p ):
		"""Return if Pieces[ p ] is center (aka not special)"""
		return ( not self.isPieceCorner( p ) and not self.isPieceBorder( p ) )

	# ----- Return type of piece
	def getPieceType( self, p ):
		"""Return the type of piece"""
		if self.isPieceBorder( p ): return self.TYPE_BORDER
		if self.isPieceCorner( p ): return self.TYPE_CORNER

		return self.TYPE_CENTER

	# ----- Rotate piece (Counter-ClockWise)
	def rotatePiece( self, piece, rotation=1 ):
		"""Normalize a piece by rotating (Counter-ClockWise)"""
		tmp = [ None ] * self.EDGES_PER_PIECE
		for e in range(self.EDGES_PER_PIECE):
			tmp[ e ] = piece[ (rotation+e) % self.EDGES_PER_PIECE ]
		for e in range(self.EDGES_PER_PIECE):
			piece[ e ] = tmp[ e ]

	# ----- Normalize a piece so that we know where the edges are
	def normalizePiece( self, p ):
		if self.isPieceCorner( p ):
			while (p[0]+p[1]) != 0:
				self.rotatePiece(p, 1)
		elif self.isPieceBorder( p ):
			while p[0] != 0:
				self.rotatePiece(p, 1)
		return p
		
	# ----- Normalize all pieces
	def normalizePieces( self ):
		# Make sure the pieces are how we expect them to be
		for p in self.pieces:
			self.normalizePiece(p)




	# ----- Init Count colors
	def initStaticColorsCount( self ):
		"""Count the border and center colors"""

		for i in range(self.MAX_NB_COLORS):
			self.static_colors_border_count[ i ] = 0
			self.static_colors_center_count[ i ] = 0

		for p in self.pieces:
			if self.isPieceCorner( p ):
				l = [ (self.EDGE_DOWN, self.TYPE_BORDER), (self.EDGE_LEFT, self.TYPE_BORDER) ]
			elif self.isPieceBorder( p ):
				l =  [ (self.EDGE_LEFT, self.TYPE_BORDER), (self.EDGE_RIGHT, self.TYPE_BORDER) ]
				l += [ (self.EDGE_DOWN, self.TYPE_CENTER) ] 
			else:
				l = [ (self.EDGE_UP, self.TYPE_CENTER), (self.EDGE_RIGHT, self.TYPE_CENTER), (self.EDGE_DOWN, self.TYPE_CENTER), (self.EDGE_LEFT, self.TYPE_CENTER) ]
				
			for (e, t) in l:
				if t == self.TYPE_BORDER:
					self.static_colors_border_count[ p[ e ] ] += 1
				elif t == self.TYPE_CENTER:
					self.static_colors_center_count[ p[ e ] ] += 1

		self.static_colors_border_count = { k:v//2 for k, v in self.static_colors_border_count.items() if v }
		self.static_colors_center_count = { k:v//2 for k, v in self.static_colors_center_count.items() if v }

		if self.DEBUG_STATIC > 0:
			self.info( " * Colors Border : " + str(self.static_colors_border_count) )
			self.info( " * Colors Center : " + str(self.static_colors_center_count) )

		self.EDGE_DOMAIN_1_PIECE = max( [ max(self.static_colors_center_count), max(self.static_colors_border_count) ] ) + 1
		self.EDGE_DOMAIN_2_PIECE = (self.EDGE_DOMAIN_1_PIECE << self.EDGE_SHIFT_LEFT) | self.EDGE_DOMAIN_1_PIECE
		self.EDGE_DOMAIN_2_PIECE = self.EDGE_DOMAIN_1_PIECE * (1 << self.EDGE_SHIFT_LEFT)

	# ----- read pre-computed data
	def readStatistics( self ):

		def keySort(e):
			return e[1]

		filename= "data/" + self.getFileFriendlyName( self.name ) + ".stats"
		
		self.stats = {}

		if os.path.exists(filename):
			f = open(filename, 'r')
			for line in f:
				if not line.startswith('#'):
					line = line.strip('\n').strip(' ')
					line = list( map(int, line.split(' ')) )

					#print(line)
					space = line[0]
					total = line[1]

					data = {}
					data[ "space" ] = space
					data[ "total" ] = total


					# Normalize
					tmp = [ int(x*1000000/total) for x in line[2:] ]
					# Numberize
					numbers = range(0, self.board_wh)
					tmp = [ (n, x) for (n,x) in zip(numbers, tmp) if x > 0 ]
					# Sort
					tmp.sort(key=keySort)

					pieces = [ n for (n,x) in tmp if x > 0 ]
					stats  = [ x for (n,x) in tmp if x > 0 ]

					data[ "pieces" ] = pieces
					data[ "stats"  ] = stats
					data[ "pieces_stats"  ] = tmp

					if self.DEBUG_STATIC > 1:
						# Normalize
						#non_zero = [ x for x in line[2:] if x > 0 ]
						#local_min = min(non_zero)
						#tmp = [ int(x-local_min+1) for x in non_zero ]
						print( tmp )
						#self.printArray( line[2:], array_w=self.board_w, array_h=self.board_h )
						#print(data)

					self.stats[ space ] = data
			f.close()
		else:
			#if self.DEBUG_STATIC > 0:
			self.info( " * Statistics not found: " + filename )
			exit()
				
			self.stats = None

		return self.stats



	# ----- Get all the pieces
	def getPieces( self, only_corner=False, only_border=False, only_center=False, only_fixed=False ):
		l = []

		n = 0
		for p in self.pieces:
			q = Piece( n, p[0], p[1], p[2], p[3] )
			for [ fp, fs, fr ] in self.fixed:
				if n == fp:
					q.fixed = True

			if only_corner:
				if q.isCorner():
					l.append(q)
			elif only_border:
				if q.isBorder():
					l.append(q)
			elif only_center:
				if q.isCenter() and not q.isFixed():
					l.append(q)
			elif only_fixed:
				if q.isFixed():
					l.append(q)
			else:
				l.append(q)

			n += 1

		return l


	# ----- Get all the pieces
	def getRotatedPieces( self, piece, allow_conflicts=False ):
		
		score = 0
		heuristic_side_count = 0

		for side in self.scenario.heuristic_patterns:
			for e in piece.getEdges():
				if e == side:
					score += 100
					heuristic_side_count += 1


		rotatedPieces = []

		colors_border = [0] + list(self.static_colors_border_count)
		colors_center = list(self.static_colors_center_count)
		colors = sorted(colors_border + colors_center)
		
		for left in colors:
			for up in colors:

				for rotation in [ 0, 1, 2, 3 ]:

					rotation_conflicts = 0
					side_conflicts = 0

					if left != piece.l:
						rotation_conflicts += 1
						if piece.l in colors_border:
							side_conflicts += 1

					if up != piece.u:
						rotation_conflicts += 1
						if piece.u in colors_border:
							side_conflicts += 1

					if  (rotation_conflicts == 0) or \
					   ((rotation_conflicts == 1) and allow_conflicts):

						if side_conflicts == 0:
							
							rotatedPieces.append(
								RotatedPieceWithDownLeft(
									l_u = (left << self.EDGE_SHIFT_LEFT) + up,

									score = score - 100000 * rotation_conflicts,
									rotated_piece = RotatedPiece(
										p = piece.p,
										rotation = rotation,
										u = piece.u,
										r = piece.r,
										d = piece.d,
										l = piece.l,
										b = rotation_conflicts,
										h = heuristic_side_count
										)
									)
								)
					piece.turnCW()



		return rotatedPieces

	# 
	def list_rotated_pieces_to_dict(self, list_pieces, allow_conflicts=False, u=None, r=None, d=None, l=None, n=None, rotation=None):
		tmp = []
		for p in list_pieces:
			tmp.extend(self.getRotatedPieces( p, allow_conflicts ))
			
		list_pieces_rotated = {}
		for p in tmp:
			if u != None:
				if p.rotated_piece.u != u:
					continue
			if r != None:
				if p.rotated_piece.r != r:
					continue
			if d != None:
				if p.rotated_piece.d != d:
					continue
			if l != None:
				if p.rotated_piece.l != l:
					continue
			if n != None:
				if p.rotated_piece.p != n:
					continue
			if rotation != None:
				if p.rotated_piece.rotation != rotation:
					continue

			if p.l_u in list_pieces_rotated.keys():
				list_pieces_rotated[p.l_u].append(p)
			else:
				list_pieces_rotated[p.l_u] = [ p ]

		return list_pieces_rotated


	def list_rotated_pieces_to_array(self, list_pieces):
		# Randomize the search
		rand_entropy = 99

		array = [ None ] * self.EDGE_DOMAIN_2_PIECE
		for l_u in list_pieces.keys():
			tmp = []
			for p in sorted(list_pieces[ l_u ], reverse=True, key=lambda x : x.score+random.randint(0,rand_entropy)):
				tmp.append(p.rotated_piece)
				
			array[ l_u ] = tmp
		return array


	# ----- Prepare pieces and heuristics
	def prepare_pieces( self, local_seed=None ):

		if self.DEBUG > 2:
			self.info( " * Preparing pieces..." )

		master_index = {}
		master_lists_of_rotated_pieces = []
		master_all_rotated_pieces = {}

		# Randomize the pieces
		if local_seed:
			random.seed( local_seed )
		else:
			random.seed( self.seed )

		corner_pieces = self.getPieces(only_corner=True) 
		border_pieces = self.getPieces(only_border=True) 
		center_pieces = self.getPieces(only_center=True) 
		fixed_pieces  = self.getPieces(only_fixed=True) 
		
		# Corner
		corner_pieces_rotated = self.list_rotated_pieces_to_dict(corner_pieces)

		# Border
		border_u_pieces_rotated           = self.list_rotated_pieces_to_dict(border_pieces, rotation=0)
		border_u_pieces_rotated_conflicts = self.list_rotated_pieces_to_dict(border_pieces, rotation=0, allow_conflicts=True)
		border_r_pieces_rotated           = self.list_rotated_pieces_to_dict(border_pieces, rotation=1)
		border_r_pieces_rotated_conflicts = self.list_rotated_pieces_to_dict(border_pieces, rotation=1, allow_conflicts=True)
		border_d_pieces_rotated           = self.list_rotated_pieces_to_dict(border_pieces, rotation=2)
		border_d_pieces_rotated_conflicts = self.list_rotated_pieces_to_dict(border_pieces, rotation=2, allow_conflicts=True)
		border_l_pieces_rotated           = self.list_rotated_pieces_to_dict(border_pieces, rotation=3)
		border_l_pieces_rotated_conflicts = self.list_rotated_pieces_to_dict(border_pieces, rotation=3, allow_conflicts=True)
		
		# Center
		center_pieces_rotated             = self.list_rotated_pieces_to_dict(center_pieces)
		center_pieces_rotated_conflicts   = self.list_rotated_pieces_to_dict(center_pieces, allow_conflicts=True)

		# Fixed
		for [ fp, fs, fr ] in self.fixed:
			p = Piece( fp, self.pieces[fp][0], self.pieces[fp][1], self.pieces[fp][2], self.pieces[fp][3] )
			for i in range(fr):
				p.turnCW()
			exec("fixed"+str(fp)+"_pieces_rotated = self.list_rotated_pieces_to_dict(fixed_pieces, n="+str(fp)+", rotation="+str(fr)+")")
			exec("fixed"+str(fp)+"_pieces_rotated_s = self.list_rotated_pieces_to_dict(center_pieces, u="+str(p.d)+")")
			exec("fixed"+str(fp)+"_pieces_rotated_w = self.list_rotated_pieces_to_dict(center_pieces, r="+str(p.l)+")")
			exec("fixed"+str(fp)+"_pieces_rotated_n = self.list_rotated_pieces_to_dict(center_pieces, d="+str(p.u)+")")
			exec("fixed"+str(fp)+"_pieces_rotated_e = self.list_rotated_pieces_to_dict(center_pieces, l="+str(p.r)+")")


		master_index[ "corner"             ] = self.list_rotated_pieces_to_array(corner_pieces_rotated)
		master_index[ "border_u"           ] = self.list_rotated_pieces_to_array(border_u_pieces_rotated)
		master_index[ "border_u_conflicts" ] = self.list_rotated_pieces_to_array(border_u_pieces_rotated_conflicts)
		master_index[ "border_r"           ] = self.list_rotated_pieces_to_array(border_r_pieces_rotated)
		master_index[ "border_r_conflicts" ] = self.list_rotated_pieces_to_array(border_r_pieces_rotated_conflicts)
		master_index[ "border_d"           ] = self.list_rotated_pieces_to_array(border_d_pieces_rotated)
		master_index[ "border_d_conflicts" ] = self.list_rotated_pieces_to_array(border_d_pieces_rotated_conflicts)
		master_index[ "border_l"           ] = self.list_rotated_pieces_to_array(border_l_pieces_rotated)
		master_index[ "border_l_conflicts" ] = self.list_rotated_pieces_to_array(border_l_pieces_rotated_conflicts)
		master_index[ "center"             ] = self.list_rotated_pieces_to_array(center_pieces_rotated)
		master_index[ "center_conflicts"   ] = self.list_rotated_pieces_to_array(center_pieces_rotated_conflicts)
		for [ fp, fs, fr ] in self.fixed:
			exec("master_index[ \"fixed"+str(fp)+"_s\" ] = self.list_rotated_pieces_to_array(fixed"+str(fp)+"_pieces_rotated_s)")
			exec("master_index[ \"fixed"+str(fp)+"_w\" ] = self.list_rotated_pieces_to_array(fixed"+str(fp)+"_pieces_rotated_w)")
			exec("master_index[ \"fixed"+str(fp)+"_n\" ] = self.list_rotated_pieces_to_array(fixed"+str(fp)+"_pieces_rotated_n)")
			exec("master_index[ \"fixed"+str(fp)+"_e\" ] = self.list_rotated_pieces_to_array(fixed"+str(fp)+"_pieces_rotated_e)")
			exec("master_index[ \"fixed"+str(fp)+"\"   ] = self.list_rotated_pieces_to_array(fixed"+str(fp)+"_pieces_rotated)")


		# Create a list of all the RotatedPiece
		for k,v in master_index.items():
			for l in v:
				if l != None:
					for p in l:
						master_all_rotated_pieces[ str(p) ] = p

		# Assign an index number to each RotatedPiece
		master_all_rotated_pieces_index = {}
		index = 0
		for k in sorted(master_all_rotated_pieces.keys()):
			master_all_rotated_pieces_index[ k ] = index
			index += 1


		# Replace the RotatedPiece Class by the RotatedPiece index number
		for k,v in master_index.items():
			for i in range(len(v)):
				if v[i] != None:
					new_l = []
					for p in v[i]:
						new_l.append(master_all_rotated_pieces_index[ str(p) ])
					v[i] = new_l


		# Create a global list with all the indexes of RotatedPiece, each sub list ended with none
		# and replace the lists in master_index with indexes
		master_lists_of_rotated_pieces = []
		for k,v in master_index.items():
			for i in range(len(v)):
				if v[i] != None:
					new_index = len(master_lists_of_rotated_pieces)
					master_lists_of_rotated_pieces.extend( v[i] + [ None ] ) # [ -1 ] marks the end of the sub list
					v[i] = new_index
					
		
		# We obtain 
		if self.DEBUG > 5:
			# - a dictionnary of a few arrays of size 529 for quick access to lists of indexed pieces
			print(master_index)
			# - a list of "None"-separated lists, containing indexed pieces
			print(master_lists_of_rotated_pieces)
			# - all the rotated pieces
			print(sorted(master_all_rotated_pieces))


		return ( master_index, master_lists_of_rotated_pieces, master_all_rotated_pieces )



	# ----- Get how the patterns are relating to each other
	def initPatternsRelations(self):

		colors_border = [0]+ list(self.static_colors_border_count)
		colors_center = list(self.static_colors_center_count)
		colors = sorted(colors_border + colors_center)

		relations = [ 0 ] * (len(colors) * len(colors))

		for c in colors:
			for p in self.pieces:
				if c in p:
					for e in p:
						relations[ c*len(colors) + e ] += 1
			
		for m in range(max(relations)):
			print("##################################", m, "########################")
			print()
			print( "".rjust(3, " "), end="   " )
			for x in range(len(colors)):
				print( str(x).rjust(3, " "), end="   " )
			print()
			print("    "+ ("|-----" * len(colors))+"|")

			for y in range(len(colors)):
				print( str(y).rjust(3, " "), end=" | " )
				for x in range(len(colors)):
					v = relations[x+y*len(colors)]
					if x == y:
						v = " ~ "
					elif v < m:
						v = " "
					elif v == 0:
						v = " "
					elif v == 1:
						v = "."
					else:
						v = str(v)

					print( v.rjust(3, " "), end=" | " )
				print()
				print("    "+ ("|-----" * len(colors))+"|")
			print()
			print()



if __name__ == "__main__":
	import data

	p = data.loadPuzzle()

	p.initPatternsRelations()








# Lapin
