# Global Libs
import os
import sys
import time
import datetime
import select
import random
import multiprocessing
import itertools
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
	weight = 0

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
	heuristic_patterns_count = [0,0,0,0,0] # up to 5 heuristics on patterns count
	heuristic_stats16_count = 0

	def __init__(self, p, rotation, u, r, d, l, b, h, w):
		self.p = p
		self.rotation = rotation
		self.u = u
		self.r = r
		self.d = d
		self.l = l
		self.conflicts_count = b
		self.heuristic_patterns_count = h
		self.heuristic_stats16_count = w

	def __str__(self):
		return str(self.p).zfill(3)+"["+str(self.conflicts_count)+"/"+str(self.heuristic_patterns_count)+":"+chr(ord('a')+self.u)+chr(ord('a')+self.r)+chr(ord('a')+self.d)+chr(ord('a')+self.l)+"]"

	def __repr__(self):
		return str(self.p).zfill(3)+"["+str(self.conflicts_count)+"/"+str(self.heuristic_patterns_count)+":"+chr(ord('a')+self.u)+chr(ord('a')+self.r)+chr(ord('a')+self.d)+chr(ord('a')+self.l)+"]"

class RotatedPieceWithRef():
	ref = 0
	score = 0
	rotated_piece = None

	def __init__(self, ref, score, rotated_piece):
		self.ref = ref
		self.score = score
		self.rotated_piece = rotated_piece

	def __str__(self):
		return str(self.ref)+":"+str(self.rotated_piece.p)+"("+str(self.score)+")"
	def __repr__(self):
		return str(self.ref)+":"+str(self.rotated_piece.p)+"("+str(self.score)+")"


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

	static_spaces_corners = []
	static_spaces_borders = []
	static_spaces_centers = []

	static_space_up		= []
	static_space_right	= []
	static_space_down	= []
	static_space_left	= []
	static_space_up_right	= []
	static_space_right_down	= []
	static_space_down_left	= []
	static_space_left_up	= []

	static_spaces_type = []		# the type for each space

	pieces_stats16_weight = []

	# Precomputed statistics
	stats = None

	# ----- Init the puzzle
	def __init__( self ):
		"""
		Initialize
		"""

		defs.Defs.__init__( self )

		self.board_wh = self.board_w * self.board_h
	
		self.normalizePieces()		# Make sure the pieces are how we expect them to be
		self.initStaticColorsCount()

		self.readStatistics()
		self.pieces_stats16_weight = [0] * self.board_wh

		self.scenario = scenarios.loadScenario(self)

		self.initStaticSpacesList()
		self.initStaticSpaceURDL()
		self.initStaticSpacesType()

		self.TITLE_STR += self.name+"("+ self.scenario.name +")"

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
		self.EDGE_DOMAIN_2_PIECE = self.EDGE_DOMAIN_1_PIECE * (1 << self.EDGE_SHIFT_LEFT)
		self.EDGE_DOMAIN_3_PIECE = self.EDGE_DOMAIN_1_PIECE * (1 << (self.EDGE_SHIFT_LEFT*2))

		# Duo colors
		self.colors_border = [0] + list(self.static_colors_border_count)
		self.colors_center = list(self.static_colors_center_count)
		self.colors = sorted(self.colors_border + self.colors_center)


	# ----- Init Static Spaces Lists
	def initStaticSpacesList( self ):
		W=self.board_w
		H=self.board_h
		WH=self.board_wh

		self.static_spaces_corners = []
		self.static_spaces_borders = []
		self.static_spaces_centers = []

		self.static_spaces_corners = [0, W-1, WH-W, WH-1 ]
		
		for space in range(WH):
			if space not in self.static_spaces_corners:

				if  (space < W) or \
				    (space % W == W-1) or \
				    (space >= WH-W) or \
				    (space % W == 0):
					self.static_spaces_borders.append(space)

		for space in range(WH):
			if space not in self.static_spaces_corners+self.static_spaces_borders:
				self.static_spaces_centers.append(space)

		if self.DEBUG_STATIC > 2:
			self.info( " * Spaces Corners : " + str(len(self.static_spaces_corners))+" "+str(self.static_spaces_corners) )
			self.info( " * Spaces Borders : " + str(len(self.static_spaces_borders))+" "+str(self.static_spaces_borders) )
			self.info( " * Spaces Centers : " + str(len(self.static_spaces_centers))+" "+str(self.static_spaces_centers) )

	# ----- Init the static space up, right, down, left
	def initStaticSpaceURDL( self ):
		"""Init the static space up, right, down, left"""

		self.static_space_up    = [None] * self.board_wh 
		self.static_space_right = [None] * self.board_wh 
		self.static_space_down  = [None] * self.board_wh 
		self.static_space_left  = [None] * self.board_wh 
		self.static_space_up_right    = [None] * self.board_wh 
		self.static_space_right_down = [None] * self.board_wh 
		self.static_space_down_left  = [None] * self.board_wh 
		self.static_space_left_up  = [None] * self.board_wh 

		for s in range( self.board_wh ):
			self.static_space_up[ s ]	= s - self.board_w
			self.static_space_right[ s ]	= s + 1
			self.static_space_down[ s ]	= s + self.board_w
			self.static_space_left[ s ]	= s - 1
			self.static_space_up_right[ s ]		= s - self.board_w + 1
			self.static_space_right_down[ s ]	= s + 1 + self.board_w
			self.static_space_down_left[ s ]	= s + self.board_w - 1
			self.static_space_left_up[ s ]		= s - 1 - self.board_w


			if self.static_space_up[ s ] < 0:
				self.static_space_up[ s ] = None

			if self.static_space_down[ s ] >= self.board_wh:
				self.static_space_down[ s ] = None

			if self.static_space_right[ s ] // self.board_w != s // self.board_w:
				self.static_space_right[ s ] = None
			
			if self.static_space_left[ s ] // self.board_w != s // self.board_w:
				self.static_space_left[ s ] = None
		

			if self.static_space_up[ s ] == None  or  self.static_space_right[ s ] == None:
				self.static_space_up_right[ s ] = None

			if self.static_space_right[ s ] == None  or  self.static_space_down[ s ] == None:
				self.static_space_right_down[ s ] = None

			if self.static_space_down[ s ] == None  or  self.static_space_left[ s ] == None:
				self.static_space_down_left[ s ] = None

			if self.static_space_left[ s ] == None  or  self.static_space_up[ s ] == None:
				self.static_space_left_up[ s ] = None


		if self.DEBUG_STATIC > 2:
			self.printArray( self.static_space_up, self.static_space_right, self.static_space_down, self.static_space_left, array_w=self.board_w, array_h=self.board_h)
			self.printArray( self.static_space_up_right, self.static_space_right_down, self.static_space_down_left, self.static_space_left_up, array_w=self.board_w, array_h=self.board_h )
			

	# ----- Init the static type for each space
	def initStaticSpacesType( self ):
		"""Init the static type for each space"""

		self.static_spaces_type = [None] * self.board_wh 

		# Clean the array
		for s in range( self.board_wh ):
			self.static_spaces_type[ s ] = "center"

		# Borders
		for s in range( self.board_wh ):
			if ((s % self.board_w) == 0          ):	self.static_spaces_type[ s ] = "border"
			if ((s % self.board_w) == (self.board_w-1)):	self.static_spaces_type[ s ] = "border"
			if (s < self.board_w)		:	self.static_spaces_type[ s ] = "border"
			if (s > (self.board_wh - self.board_w))	:	self.static_spaces_type[ s ] = "border"

		# Corners
		self.static_spaces_type[ 0 ] = "corner"
		self.static_spaces_type[ self.board_w - 1 ] = "corner"
		self.static_spaces_type[ self.board_wh - self.board_w ] = "corner"
		self.static_spaces_type[ self.board_wh - 1 ] = "corner"

		# Fixed
		for [ fp, fs, fr ] in self.fixed:
			self.static_spaces_type[ fs ] = "fixed"

		if self.DEBUG_STATIC > 2:
			self.printArray( self.static_spaces_type, array_w=self.board_w, array_h=self.board_h)

	# ----- read pre-computed data
	def readStatistics( self ):

		def keySort(e):
			return e[1]

		filename= "data/" + self.getFileFriendlyName( self.name ) + ".stats"
		
		self.stats = {}

		if os.path.exists(filename):
			numbers = range(0, self.board_wh)

			f = open(filename, 'r')
			for line in f:
				if line.startswith('#'):
					continue
				line = line.strip('\n').strip(' ')
				line = list( map(int, line.split(' ')) )

				space = line[0]
				total = line[1]

				data = {}
				data[ "space" ] = space
				data[ "total" ] = total

				# Numberize
				tmp = [ (n, x) for (n,x) in zip(numbers, line[2:]) if x >= 0 ]
				# Normalize
				tmp = [ (n, int(x*1000000/total)) for (n,x) in tmp ]
				# Sort
				tmp.sort(key=keySort)

				pieces = [ n for (n,x) in tmp if x > 0 ]
				stats  = [ x for (n,x) in tmp if x > 0 ]

				data[ "pieces" ] = pieces
				data[ "stats"  ] = stats
				data[ "pieces_stats"  ] = tmp

				if self.DEBUG_STATIC > 1:
					print(data)

				self.stats[ space ] = data
			f.close()
		else:
			#if self.DEBUG_STATIC > 0:
			self.info( " * Statistics not found: " + filename )
			#exit()
				
			self.stats = None

		return self.stats


	# ----- Prepare stats for the last 16 pieces to insert, according to the sequence
	def prepare_stats16_from_sequence( self, sequence ):
		self.pieces_stats16_count  = [0] * self.board_wh
		self.pieces_stats16_weight = [0] * self.board_wh
		
		for s in sequence[-16:]:

			# Pieces that should have been there, but are not, get a huge weight
			index = 0
			for (p, stats16) in self.stats[ s ]["pieces_stats"]:
				if stats16 != 0:
					break
				self.pieces_stats16_count[p] += 1
				self.pieces_stats16_weight[p] += 5
				index += 1
				
			#print(s)
			
			# Pieces that have been seen during the stats16
			seen = self.stats[ s ]["pieces_stats"][index:]
			seen_avg = sum([ x for (n,x) in seen])//len(seen)
			seen_min = min([ x for (n,x) in seen])
			seen_max = max([ x for (n,x) in seen])
			#print(seen_min, seen_avg, seen_max, " =>  ", seen_avg-seen_min, "<", seen_avg, ">", seen_max-seen_avg)

			# The weight is proportionnal to the distance to the average
			for (n, x) in seen:
				if x >= seen_avg:
					break

				w = int(4 * ((seen_avg-x) / (seen_avg-seen_min))) # Can be 3,4,5,6

				self.pieces_stats16_count[n] += 1
				self.pieces_stats16_weight[n] += w


		if self.DEBUG_STATIC > 1:
			self.info( " * Preparing stats16 weights..." )
			self.printArray( self.pieces_stats16_count, array_w=self.board_w, array_h=self.board_h, replacezero=True )
			self.printArray( self.pieces_stats16_weight, array_w=self.board_w, array_h=self.board_h, replacezero=True )

		for p in range(self.board_wh):
			if self.pieces_stats16_count[p] > 0:
				self.pieces_stats16_weight[p] = self.pieces_stats16_weight[p] // self.pieces_stats16_count[p]
		
		if self.DEBUG_STATIC > 1:
			self.printArray( self.pieces_stats16_weight, array_w=self.board_w, array_h=self.board_h, replacezero=True )

			print(sum(self.pieces_stats16_weight))
			print(sum([ (w>0) for w in self.pieces_stats16_weight]))

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
				if q.isCorner() and not q.isFixed():
					l.append(q)
			elif only_border:
				if q.isBorder() and not q.isFixed():
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
	def getRotatedPieces( self, piece, allow_conflicts=False, for_ref="" ):
		
		score = 0
		heuristic_patterns_count = [ 0, 0, 0, 0, 0 ]

		i = 0
		for hp in self.scenario.heuristic_patterns:
			for pattern in hp:
				for e in piece.getEdges():
					if e == pattern:
						score += 100
						heuristic_patterns_count[i] += 1
			i += 1


		rotatedPieces = []

		for left in self.colors:
			for up in self.colors:

				for rotation in [ 0, 1, 2, 3 ]:

					rotation_conflicts = 0
					pattern_conflicts = 0

					if left != piece.l:
						rotation_conflicts += 1
						if piece.l in self.colors_border:
							pattern_conflicts += 1

					if up != piece.u:
						rotation_conflicts += 1
						if piece.u in self.colors_border:
							pattern_conflicts += 1

					if  (rotation_conflicts == 0) or \
					   ((rotation_conflicts == 1) and allow_conflicts):

						if pattern_conflicts == 0:
							
							rotatedPieces.append(
								RotatedPieceWithRef(
									ref = (left << self.EDGE_SHIFT_LEFT) + up,

									score = score - 100000 * rotation_conflicts,
									rotated_piece = RotatedPiece(
										p = piece.p,
										rotation = rotation,
										u = piece.u,
										r = piece.r,
										d = piece.d,
										l = piece.l,
										b = rotation_conflicts,
										h = heuristic_patterns_count,
										w = self.pieces_stats16_weight[ piece.p ]
										)
									)
								)
					piece.turnCW()



		return rotatedPieces

	# ----- Get all the pieces
	def getRotatedPiecesNew( self, piece, allow_conflicts=False, for_ref="" ):
		
		score = 0
		heuristic_patterns_count = [ 0, 0, 0, 0, 0 ]

		i = 0
		for hp in self.scenario.heuristic_patterns:
			for pattern in hp:
				for e in piece.getEdges():
					if e == pattern:
						score += 100
						heuristic_patterns_count[i] += 1
			i += 1


		rotatedPieces = []

		for rotation in [ 0, 1, 2, 3 ]:

			piece_edges = {}
			piece_edges["u"] = piece.u
			piece_edges["r"] = piece.r
			piece_edges["d"] = piece.d
			piece_edges["l"] = piece.l

			pe = [0]*4

			for i in range(len(for_ref)):
				pe[i] = piece_edges[for_ref[i]]

			if len(for_ref) == 0:
				elist = list(itertools.product(self.colors,self.colors))
			elif len(for_ref) == 1:
				elist = [ (pe[0]) ]
			elif len(for_ref) == 2:
				if allow_conflicts:
					it0 = list(itertools.product([pe[0]],self.colors))
					it1 = list(itertools.product(self.colors,[pe[1]]))
					elist = list(dict.fromkeys(it0 + it1))
				else:
					elist = [ (pe[0], pe[1]) ]
			elif len(for_ref) == 3:
				if allow_conflicts:
					it0 = list(itertools.product([pe[0]],[pe[1]],self.colors))
					it1 = list(itertools.product([pe[0]],self.colors,[pe[2]]))
					it2 = list(itertools.product(self.colors,[pe[1]],[pe[2]]))
					elist = list(dict.fromkeys(it0 + it1 + it2))
				else:
					elist = [ (pe[0], pe[1], pe[2]) ]
			elif len(for_ref) == 4:
				if allow_conflicts:
					it0 = list(itertools.product([pe[0]],[pe[1]],[pe[2]],self.colors))
					it1 = list(itertools.product([pe[0]],[pe[2]],self.colors,[pe[3]]))
					it2 = list(itertools.product([pe[0]],self.colors,[pe[2]],[pe[3]]))
					it3 = list(itertools.product(self.colors,[pe[1]],[pe[2]],[pe[3]]))
					elist = list(dict.fromkeys(it0 + it1 + it2 + it3))
				else:
					elist = [ (pe[0], pe[1], pe[2], pe[3]) ]
		
			for u in elist:
				e= [0]*4

				if len(for_ref) == 0:
					ref = 0
				elif len(for_ref) == 1:
					(e[0]) = u
					ref = e[0]
				elif len(for_ref) == 2:
					(e[0], e[1]) = u
					ref = (e[0] << self.EDGE_SHIFT_LEFT) + e[1]
				elif len(for_ref) == 3:
					(e[0], e[1], e[2]) = u
					ref = (((e[0] << self.EDGE_SHIFT_LEFT) + e[1]) << self.EDGE_SHIFT_LEFT) + e[2]
				elif len(for_ref) == 4:
					(e[0], e[1], e[2], e[3]) = u
					ref = (((e[0] << self.EDGE_SHIFT_LEFT) + e[1]) << self.EDGE_SHIFT_LEFT) + e[2]


				conflict = {}
				conflict["u"] = conflict["r"] = conflict["d"] = conflict["l"] = False

				for i in range(len(for_ref)):
					conflict[for_ref[i]] = (e[i] != piece_edges[for_ref[i]])


				if (conflict["u"] and (piece_edges["u"] in self.colors_border)) or \
				   (conflict["r"] and (piece_edges["r"] in self.colors_border)) or \
				   (conflict["d"] and (piece_edges["d"] in self.colors_border)) or \
				   (conflict["l"] and (piece_edges["l"] in self.colors_border)):
					continue

				conflicts = int(conflict["u"]) + int(conflict["r"]) + int(conflict["d"]) + int(conflict["l"])

				if  (conflicts == 0) or \
				   ((conflicts == 1) and allow_conflicts):

					rotatedPieces.append(
						RotatedPieceWithRef(
							ref = ref,

							score = score - 100000 * conflicts,
							rotated_piece = RotatedPiece(
								p = piece.p,
								rotation = rotation,
								u = piece.u,
								r = piece.r,
								d = piece.d,
								l = piece.l,
								b = conflicts,
								h = heuristic_patterns_count,
								w = self.pieces_stats16_weight[ piece.p ]
								)
							)
						)
			piece.turnCW()



		return rotatedPieces

	# 
	def list_rotated_pieces_to_dict(self, list_pieces, allow_conflicts=False, reference="", u=None, r=None, d=None, l=None, p=None, rotation=None):
		if self.DEBUG > 0:
			self.top("list rotated pieces to dict")
			self.info( " * List rotated pieces to dict with reference " + reference )

		tmp = []
		for piece in list_pieces:
			tmp.extend(self.getRotatedPiecesNew( piece, allow_conflicts, reference ))
			
		list_pieces_rotated = {}
		for piece in tmp:
			if u != None:
				if piece.rotated_piece.u != u:
					continue
			if r != None:
				if piece.rotated_piece.r != r:
					continue
			if d != None:
				if piece.rotated_piece.d != d:
					continue
			if l != None:
				if piece.rotated_piece.l != l:
					continue
			if p != None:
				if piece.rotated_piece.p != p:
					continue
			if rotation != None:
				if piece.rotated_piece.rotation != rotation:
					continue

			if piece.ref in list_pieces_rotated.keys():
				list_pieces_rotated[piece.ref].append(piece)
			else:
				list_pieces_rotated[piece.ref] = [ piece ]

		if self.DEBUG > 0:
			self.info( " * List rotated pieces to dict with reference "+ reference + " took "+ self.top("list rotated pieces to dict"))

		return list_pieces_rotated


	def list_rotated_pieces_to_array(self, list_pieces, reference="" ):
		# Randomize the search
		rand_entropy = 99

		DOMAIN=0
		if len(reference) == 0:
			DOMAIN = 1
		if len(reference) == 1:
			DOMAIN = self.EDGE_DOMAIN_1_PIECE
		elif len(reference) == 2:
			DOMAIN = self.EDGE_DOMAIN_2_PIECE
		elif len(reference) == 3:
			DOMAIN = self.EDGE_DOMAIN_3_PIECE
		elif len(reference) == 4:
			DOMAIN = self.EDGE_DOMAIN_3_PIECE

		array = [ None ] * DOMAIN
		for ref in list_pieces.keys():
			tmp = []
			for p in sorted(list_pieces[ ref ], reverse=True, key=lambda x : x.score+random.randint(0,rand_entropy)):
				tmp.append(p.rotated_piece)
				
			array[ ref ] = tmp

		return array


	# ----- Prepare pieces and heuristics
	def prepare_pieces( self ):
		W=self.board_w
		H=self.board_h
		WH=self.board_wh

		if self.DEBUG > 0:
			self.top("prepare pieces")
			self.info( " * Preparing pieces" )

		master_index = {}
		master_lists_of_rotated_pieces = []
		master_all_rotated_pieces = {}

		# Randomize the pieces
		random.seed( self.scenario.seed )

		pieces = {}
		pieces["corner"] = self.getPieces(only_corner=True) 
		pieces["border"] = self.getPieces(only_border=True) 
		pieces["center"] = self.getPieces(only_center=True) 
		pieces["fixed" ] = self.getPieces(only_fixed=True) 
		
		# Corner
		possible_references_corner = list(dict.fromkeys([ self.scenario.spaces_references[s] for s in self.static_spaces_corners]))
		for reference in possible_references_corner:
			tmp = self.list_rotated_pieces_to_dict(pieces["corner"], reference=reference)
			master_index[ "corner_"+reference ] = self.list_rotated_pieces_to_array(tmp, reference)

		# Border
		possible_references_border = list(dict.fromkeys([ self.scenario.spaces_references[s] for s in self.static_spaces_borders]))
		for (reference, (direction,rotation), conflicts) in itertools.product(possible_references_border, [("u",0),("r",1),("d",2),("l",3)], [False,True]):
			tmp = self.list_rotated_pieces_to_dict(pieces["border"], rotation=rotation, allow_conflicts=conflicts, reference=reference)
			master_index[ "border_"+direction+("_conflicts" if conflicts else "")+"_"+reference ] = self.list_rotated_pieces_to_array(tmp, reference)

		# Center
		possible_references_center = list(dict.fromkeys([ self.scenario.spaces_references[s] for s in self.static_spaces_centers]))
		for (reference, conflicts) in itertools.product(possible_references_center, [False,True]):
			tmp = self.list_rotated_pieces_to_dict(pieces["center"], allow_conflicts=conflicts, reference=reference)
			master_index[ "center"+("_conflicts" if conflicts else "")+"_"+reference ] = self.list_rotated_pieces_to_array(tmp, reference)

		# Fixed
		for [ fp, fs, fr ] in self.fixed:
			p = Piece( fp, self.pieces[fp][0], self.pieces[fp][1], self.pieces[fp][2], self.pieces[fp][3] )
			for i in range(fr):
				p.turnCW()

			# The fixed piece
			reference = self.scenario.spaces_references[fs]
			tmp = self.list_rotated_pieces_to_dict(pieces["fixed"], p=fp, rotation=fr, reference=reference)
			master_index[ "fixed"+str(fp)+"_"+reference ] = self.list_rotated_pieces_to_array(tmp, reference)

			# Neighbors of fixed pieces
			if self.static_space_down[ fs ] != None:
				nfs = self.static_space_down[ fs ]
				reference = self.scenario.spaces_references[nfs]
				tmp = self.list_rotated_pieces_to_dict(pieces[ self.static_spaces_type[ nfs ] ], u=p.d, reference=reference)
				master_index[ "fixed"+str(fp)+"_s"+"_"+reference ] = self.list_rotated_pieces_to_array(tmp, reference)

			if self.static_space_left[ fs ] != None:
				nfs = self.static_space_left[ fs ]
				reference = self.scenario.spaces_references[nfs]
				tmp = self.list_rotated_pieces_to_dict(pieces[ self.static_spaces_type[ nfs ] ], r=p.l, reference=reference)
				master_index[ "fixed"+str(fp)+"_w"+"_"+reference ] = self.list_rotated_pieces_to_array(tmp, reference)

			if self.static_space_up[ fs ] != None:
				nfs = self.static_space_up[ fs ]
				reference = self.scenario.spaces_references[nfs]
				tmp = self.list_rotated_pieces_to_dict(pieces[ self.static_spaces_type[ nfs ] ], d=p.u, reference=reference)
				master_index[ "fixed"+str(fp)+"_n"+"_"+reference ] = self.list_rotated_pieces_to_array(tmp, reference)

			if self.static_space_right[ fs ] != None:
				nfs = self.static_space_right[ fs ]
				reference = self.scenario.spaces_references[nfs]
				tmp = self.list_rotated_pieces_to_dict(pieces[ self.static_spaces_type[ nfs ] ], l=p.r, reference=reference)
				master_index[ "fixed"+str(fp)+"_e"+"_"+reference ] = self.list_rotated_pieces_to_array(tmp, reference)


		if self.DEBUG > 4:
			for k,v in master_index.items():
				print(k)

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

		if self.DEBUG > 0:
			self.info( " * Preparing pieces took "+ self.top("prepare pieces"))

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
						relations[ e*len(colors) + c ] += 1

		# Clear the borders
		for x in range(len(colors)):
			relations[ 0*len(colors) + x ] = 0 
		for y in range(len(colors)):
			relations[ y*len(colors) + 0 ] = 0 
		for i in range(len(colors)):
			relations[ i*len(colors) + i ] = 0 

			
		for m in range(max(relations)+1):
			try:
				relations.index(m)
			except ValueError as error:
				continue
			except IndexError as error:
				continue

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
