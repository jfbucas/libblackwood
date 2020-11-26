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


#
# Pieces, Rotations, Lists, Puzzle 
# this is where we prepare everything for the algorithm
#



# General configuration for JBlackwood algorithm

SCORE_TARGET = 470

MAX_HEURISTIC_INDEX = {
		469: 156,
		470: 160,
		}

HEURISTIC_SIDES = {
		469: [ 17, 2, 18 ],
		470: [ 13, 16, 10 ],
		}

BREAK_INDEXES_ALLOWED = {
		469: [ 201, 206, 211, 216, 221, 225, 229, 233, 237, 239, 241, 256 ],
		470: [ 197, 203, 210, 216, 221, 225, 229, 233, 236, 238, 256 ],
		}




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
	break_count = 0
	heuristic_side_count = 0

	def __init__(self, p, rotation, u,r, b, h):
		self.p = p
		self.rotation = rotation
		self.u = u
		self.r = r
		self.break_count = b
		self.heuristic_side_count = h

	def __str__(self):
		return str(self.p).zfill(3)+"["+str(self.break_count)+"/"+str(self.heuristic_side_count)+":"+chr(ord('a')+self.u)+chr(ord('a')+self.r)+"]"
	def __repr__(self):
		return str(self.p).zfill(3)+"["+str(self.break_count)+"/"+str(self.heuristic_side_count)+":"+chr(ord('a')+self.u)+chr(ord('a')+self.r)+"]"

class RotatedPieceWithDownLeft():
	d_l = 0
	score = 0
	rotated_piece = None

	def __init__(self, d_l, score, rotated_piece):
		self.d_l = d_l
		self.score = score
		self.rotated_piece = rotated_piece

	def __str__(self):
		return str(self.d_l)+":"+str(self.rotated_piece.p+1)+"("+str(self.score)+")"
	def __repr__(self):
		return str(self.d_l)+":"+str(self.rotated_piece.p+1)+"("+str(self.score)+")"


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


	# JBlackwood algorithm
	score_target = 0
	heuristic_sides = None
	break_indexes_allowed = None
	max_heuristic_index = 0
	seed = 0
	master_index = {}
	master_lists_of_rotated_pieces = []
	master_all_rotated_pieces = {}
	heuristic_array = []
	pieceSequence = []
	searchSequence = []
	spaces_board_sequence = []
	spaces_patterns_sequence = []


	# ----- Init the puzzle
	def __init__( self ):
		"""
		Initialize
		"""

		defs.Defs.__init__( self )

		self.board_wh = self.board_w * self.board_h

		self.normalizePieces()		# Make sure the pieces are how we expect them to be

		self.initStaticColorsCount()


		# The Seed for the Generator
		self.seed = random.randint(0, sys.maxsize)
		if os.environ.get('SEED') != None:
			self.seed = int(os.environ.get('SEED'))
			if self.DEBUG > 0:
				self.info(" * Init Puzzle Env Seed : "+str(self.seed) )


		# The score we are trying to reach
		self.score_target = SCORE_TARGET
		if os.environ.get('TARGET') != None:
			self.score_target = int(os.environ.get('TARGET'))
			if self.DEBUG > 0:
				self.info(" * Score target set to "+str(self.score_target) )

		self.max_heuristic_index = MAX_HEURISTIC_INDEX[ self.score_target ]
		self.heuristic_sides = HEURISTIC_SIDES[ self.score_target ]
		self.break_indexes_allowed = BREAK_INDEXES_ALLOWED[ self.score_target ]

		( self.master_index, self.master_lists_of_rotated_pieces, self.master_all_rotated_pieces ) = self.prepare_pieces()
		self.prepare_heuristics_and_sequence()

	


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



	# ----- Get all the pieces
	def getPieces( self, only_corner=False, only_border=False, only_center=False, only_fixed=False ):
		l = []

		n = 0
		for p in self.pieces:
			q = Piece( n, p[0], p[1], p[2], p[3] )
			for [ p, s, r ] in self.fixed:
				if n == p:
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
	def getRotatedPieces( self, piece, allow_breaks=False ):
		
		score = 0
		heuristic_side_count = 0

		for side in self.heuristic_sides:
			for e in piece.getEdges():
				if e == side:
					score += 100
					heuristic_side_count += 1


		rotatedPieces = []

		colors_border = list(self.static_colors_border_count)
		colors_center = list(self.static_colors_center_count)
		colors = sorted([0] + colors_border + colors_center)
		

		
		for left in colors:
			for down in colors:

				for rotation in [ 0, 1, 2, 3 ]:

					rotation_breaks = 0
					side_breaks = 0

					if left != piece.l:
						rotation_breaks += 1
						if piece.l in colors_border:
							side_breaks += 1

					if down != piece.d:
						rotation_breaks += 1
						if piece.d in colors_border:
							side_breaks += 1

					if (rotation_breaks == 0) or \
					   ((rotation_breaks == 1) and allow_breaks):

						if side_breaks == 0:
							
							rotatedPieces.append(
								RotatedPieceWithDownLeft(
									d_l = (left << self.EDGE_SHIFT_LEFT) + down,

									score = score - 100000 * rotation_breaks,
									rotated_piece = RotatedPiece(
										p = piece.p,
										rotation = rotation,
										u = piece.u,
										r = piece.r,
										b = rotation_breaks,
										h = heuristic_side_count
										)
									)
								)
					piece.turnCW()



		return rotatedPieces

	# 
	def list_rotated_pieces_to_dict(self, list_pieces, allow_breaks=False, u=None, r=None, rotation=None):
		tmp = []
		for p in list_pieces:
			tmp.extend(self.getRotatedPieces( p, allow_breaks ))
			
		list_pieces_rotated = {}
		for p in tmp:
			if u != None:
				if p.rotated_piece.u != u:
					continue
			if r != None:
				if p.rotated_piece.r != r:
					continue
			if rotation != None:
				if p.rotated_piece.rotation != rotation:
					continue

			if p.d_l in list_pieces_rotated.keys():
				list_pieces_rotated[p.d_l].append(p)
			else:
				list_pieces_rotated[p.d_l] = [ p ]

		return list_pieces_rotated


	def list_rotated_pieces_to_array(self, list_pieces):
		# Randomize the search
		rand_entropy = 99

		array = [ None ] * self.EDGE_DOMAIN_2_PIECE
		for d_l in list_pieces.keys():
			tmp = []
			for p in sorted(list_pieces[ d_l ], reverse=True, key=lambda x : x.score+random.randint(0,rand_entropy)):
				tmp.append(p.rotated_piece)
				
			array[ d_l ] = tmp
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
		border_u_pieces_rotated_breaks = self.list_rotated_pieces_to_dict(border_pieces, rotation=0, allow_breaks=True)
		border_r_pieces_rotated        = self.list_rotated_pieces_to_dict(border_pieces, rotation=1)
		border_r_pieces_rotated_breaks = self.list_rotated_pieces_to_dict(border_pieces, rotation=1, allow_breaks=True)
		border_d_pieces_rotated        = self.list_rotated_pieces_to_dict(border_pieces, rotation=2)
		border_l_pieces_rotated        = self.list_rotated_pieces_to_dict(border_pieces, rotation=3)
		
		# Center
		center_pieces_rotated          = self.list_rotated_pieces_to_dict(center_pieces)
		center_pieces_rotated_breaks   = self.list_rotated_pieces_to_dict(center_pieces, allow_breaks=True)

		# Fixed
		fixed_pieces_rotated_south     = self.list_rotated_pieces_to_dict(center_pieces, u=6)
		fixed_pieces_rotated_west      = self.list_rotated_pieces_to_dict(center_pieces, r=11)
		fixed_pieces_rotated           = self.list_rotated_pieces_to_dict(fixed_pieces, rotation=2)


		master_index[ "corner"          ] = self.list_rotated_pieces_to_array(corner_pieces_rotated)
		master_index[ "border_u_breaks" ] = self.list_rotated_pieces_to_array(border_u_pieces_rotated_breaks)
		master_index[ "border_r"        ] = self.list_rotated_pieces_to_array(border_r_pieces_rotated)
		master_index[ "border_r_breaks" ] = self.list_rotated_pieces_to_array(border_r_pieces_rotated_breaks)
		master_index[ "border_d"        ] = self.list_rotated_pieces_to_array(border_d_pieces_rotated)
		master_index[ "border_l"        ] = self.list_rotated_pieces_to_array(border_l_pieces_rotated)
		master_index[ "center"          ] = self.list_rotated_pieces_to_array(center_pieces_rotated)
		master_index[ "center_breaks"   ] = self.list_rotated_pieces_to_array(center_pieces_rotated_breaks)
		master_index[ "fixed_south"     ] = self.list_rotated_pieces_to_array(fixed_pieces_rotated_south)
		master_index[ "fixed_west"      ] = self.list_rotated_pieces_to_array(fixed_pieces_rotated_west)
		master_index[ "fixed"           ] = self.list_rotated_pieces_to_array(fixed_pieces_rotated)

		# 38738 pieces_rotated

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



	# ----- Prepare pieces and heuristics
	def prepare_heuristics_and_sequence( self ):

		if self.DEBUG > 2:
			self.info( " * Preparing heuristics and sequence..." )

		self.heuristic_array = [0] * self.board_wh
		if self.score_target == 469:
			for i in range(self.board_wh):
				if i <= 16:
					self.heuristic_array[i] = 0
				elif i <= 26:
					self.heuristic_array[i] = int((float(i) - 16) * float(3.1))
				elif i <= 56:
					self.heuristic_array[i] = int(((float(i) - 26) * float(1.43333)) + 31)
				elif i <= 96:
					self.heuristic_array[i] = int(((float(i) - 56) * float(0.65)) + 74)
				elif i <= self.max_heuristic_index:
					self.heuristic_array[i] = int(((float(i) - 96) / 3.75) + 100)
		if self.score_target == 470:
			for i in range(self.board_wh):
				if i <= 16:
					self.heuristic_array[i] = 0
				elif i <= 26:
					self.heuristic_array[i] = int((float(i) - 16) * float(2.8))
				elif i <= 56:
					self.heuristic_array[i] = int(((float(i) - 26) * float(1.43333)) + 28)
				elif i <= 76:
					self.heuristic_array[i] = int(((float(i) - 56) * float(0.9)) + 71)
				elif i <= 102:
					self.heuristic_array[i] = int(((float(i) - 76) * float(0.6538)) + 89)
				elif i <= self.max_heuristic_index:
					self.heuristic_array[i] = int(((float(i) - 102) / 4.4615) + 106)


		if self.DEBUG > 2:
			print(self.heuristic_array)

		self.pieceSequence = [
			0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 
			16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 
			32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 
			48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 
			64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 
			80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 
			96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 
			112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 
			128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 
			144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 
			160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 
			176, 177, 178, 179, 180, 201, 206, 211, 216, 221, 226, 231, 236, 237, 238, 239, 
			181, 182, 183, 184, 185, 202, 207, 212, 217, 222, 227, 232, 240, 244, 245, 246, 
			186, 187, 188, 189, 190, 203, 208, 213, 218, 223, 228, 233, 241, 247, 250, 251, 
			191, 192, 193, 194, 195, 204, 209, 214, 219, 224, 229, 234, 242, 248, 252, 253, 
			196, 197, 198, 199, 200, 205, 210, 215, 220, 225, 230, 235, 243, 249, 254, 255,
			]

		self.searchSequence = [
			[0,0], [1,0], [2,0], [3,0], [4,0], [5,0], [6,0], [7,0], [8,0], [9,0], [10,0], [11,0], [12,0], [13,0], [14,0], [15,0], 
			[0,1], [1,1], [2,1], [3,1], [4,1], [5,1], [6,1], [7,1], [8,1], [9,1], [10,1], [11,1], [12,1], [13,1], [14,1], [15,1], 
			[0,2], [1,2], [2,2], [3,2], [4,2], [5,2], [6,2], [7,2], [8,2], [9,2], [10,2], [11,2], [12,2], [13,2], [14,2], [15,2], 
			[0,3], [1,3], [2,3], [3,3], [4,3], [5,3], [6,3], [7,3], [8,3], [9,3], [10,3], [11,3], [12,3], [13,3], [14,3], [15,3], 
			[0,4], [1,4], [2,4], [3,4], [4,4], [5,4], [6,4], [7,4], [8,4], [9,4], [10,4], [11,4], [12,4], [13,4], [14,4], [15,4], 
			[0,5], [1,5], [2,5], [3,5], [4,5], [5,5], [6,5], [7,5], [8,5], [9,5], [10,5], [11,5], [12,5], [13,5], [14,5], [15,5], 
			[0,6], [1,6], [2,6], [3,6], [4,6], [5,6], [6,6], [7,6], [8,6], [9,6], [10,6], [11,6], [12,6], [13,6], [14,6], [15,6], 
			[0,7], [1,7], [2,7], [3,7], [4,7], [5,7], [6,7], [7,7], [8,7], [9,7], [10,7], [11,7], [12,7], [13,7], [14,7], [15,7], 
			[0,8], [1,8], [2,8], [3,8], [4,8], [5,8], [6,8], [7,8], [8,8], [9,8], [10,8], [11,8], [12,8], [13,8], [14,8], [15,8], 
			[0,9], [1,9], [2,9], [3,9], [4,9], [5,9], [6,9], [7,9], [8,9], [9,9], [10,9], [11,9], [12,9], [13,9], [14,9], [15,9], 
			[0,10], [1,10], [2,10], [3,10], [4,10], [5,10], [6,10], [7,10], [8,10], [9,10], [10,10], [11,10], [12,10], [13,10], [14,10], [15,10], 
			[0,11], [1,11], [2,11], [3,11], [4,11], [0,12], [1,12], [2,12], [3,12], [4,12], [0,13], [1,13], [2,13], [3,13], [4,13], [0,14], 
			[1,14], [2,14], [3,14], [4,14], [0,15], [1,15], [2,15], [3,15], [4,15], [5,11], [5,12], [5,13], [5,14], [5,15], [6,11], [6,12], 
			[6,13], [6,14], [6,15], [7,11], [7,12], [7,13], [7,14], [7,15], [8,11], [8,12], [8,13], [8,14], [8,15], [9,11], [9,12], [9,13], 
			[9,14], [9,15], [10,11], [10,12], [10,13], [10,14], [10,15], [11,11], [11,12], [11,13], [11,14], [11,15], [12,11], [13,11], [14,11], [15,11], 
			[12,12], [12,13], [12,14], [12,15], [13,12], [14,12], [15,12], [13,13], [13,14], [13,15], [14,13], [15,13], [14,14], [15,14], [14,15], [15,15], 
			]

		self.spaces_board_sequence = []
		self.spaces_patterns_sequence = []
		for depth in range(self.board_wh):
			(col, row) = self.searchSequence[ depth ]
			
			self.spaces_board_sequence.append(row * self.board_w + col)

			row = self.board_h-1 - row
			self.spaces_patterns_sequence.append(row * self.board_w + col)





	# ----- Get how the patterns are relating to each other
	def initPatternsRelations(self):

		colors_border = list(self.static_colors_border_count)
		colors_center = list(self.static_colors_center_count)
		colors = sorted([0] + colors_border + colors_center)

		relations = [ 0 ] * (len(colors) * len(colors))

		for c in colors:
			for p in self.pieces:
				if c in p:
					for e in p:
						relations[ c*len(colors) + e ] += 1
			
		print( "".rjust(3, " "), end="   " )
		for x in range(len(colors)):
			print( str(x).rjust(3, " "), end="   " )
		print()
		print("    "+ ("|-----" * len(colors))+"|")

		for y in range(len(colors)):
			print( str(y).rjust(3, " "), end=" | " )
			for x in range(len(colors)):
				v = relations[x+y*len(colors)]
				"""
				if v == 0:
					v = ""
				elif v == 1:
					v = "."
				elif v == 2:
					v = "o"
				elif v == 3:
					v = "#"
				else:
					v = str(v)
				"""
				if x == y:
					v = " ~ "

				elif v < 10:
					v = " "
				else:
					v = str(v)
					#v = "###"

				print( v.rjust(3, " "), end=" | " )
			print()
			print("    "+ ("|-----" * len(colors))+"|")



if __name__ == "__main__":
	import data

	p = data.loadPuzzle()

	p.initPatternsRelations()








# Lapin
