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
		return str(self.p).zfill(3)+"["+str(self.conflicts_count)+"/"+str(self.heuristic_patterns_count)+":"+chr(ord('a')+self.r)+chr(ord('a')+self.d)+"]"
	def __repr__(self):
		return str(self.p).zfill(3)+"["+str(self.conflicts_count)+"/"+str(self.heuristic_patterns_count)+":"+chr(ord('a')+self.r)+chr(ord('a')+self.d)+"]"

class RotatedPieceWithRef():
	ref = 0
	score = 0
	rotated_piece = None

	def __init__(self, ref, score, rotated_piece):
		self.ref = ref
		self.score = score
		self.rotated_piece = rotated_piece

	def __str__(self):
		return str(self.ref)+":"+str(self.rotated_piece.p+1)+"("+str(self.score)+")"
	def __repr__(self):
		return str(self.ref)+":"+str(self.rotated_piece.p+1)+"("+str(self.score)+")"


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
		self.initStaticSpacesList()

		self.readStatistics()
		self.pieces_stats16_weight = [0] * self.board_wh

		self.scenario = scenarios.loadScenario(self)

		self.TITLE_STR += self.name+"("+ self.scenario.name +")"

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
			exit()
				
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

		for rotation in [ 0, 1, 2, 3 ]:

			if   for_ref in [ "lu", "dlu", "url", "urdl" ]:
				pe0 = piece.l
				pe1 = piece.u
			elif for_ref in [ "ur", "urd" ]:
				pe0 = piece.u
				pe1 = piece.r
			elif for_ref in [ "rd" ]:
				pe0 = piece.r
				pe1 = piece.d
			elif for_ref in [ "dl" ]:
				pe0 = piece.d
				pe1 = piece.l
			else:
				print("TODO: for_ref:", for_ref)
				exit()


			if for_ref == "":
				elist = list(itertools.product(self.colors,self.colors))
			else:
				if allow_conflicts:
					it0 = list(itertools.product([pe0],self.colors))
					it1 = list(itertools.product(self.colors,[pe1]))
					elist = it0 + it1
				else:
					elist = [ (pe0, pe1) ]
		
			for (e0, e1) in elist:

				conflict_u = conflict_r = conflict_d = conflict_l = False

				if   for_ref in [ "lu", "dlu", "url", "urdl" ]:
					conflict_l = (e0 != piece.l)
					conflict_u = (e1 != piece.u)
				elif for_ref in [ "ur", "urd" ]:
					conflict_u = (e0 != piece.u)
					conflict_r = (e1 != piece.r)
				elif for_ref in [ "rd" ]:
					conflict_r = (e0 != piece.r)
					conflict_d = (e1 != piece.d)
				elif for_ref in [ "dl" ]:
					conflict_d = (e0 != piece.d)
					conflict_l = (e1 != piece.l)

				if (conflict_u and (piece.u in self.colors_border)) or \
				   (conflict_r and (piece.r in self.colors_border)) or \
				   (conflict_d and (piece.d in self.colors_border)) or \
				   (conflict_l and (piece.l in self.colors_border)):
					continue

				conflicts = int(conflict_u) + int(conflict_r) + int(conflict_d) + int(conflict_l)

				if  (conflicts == 0) or \
				   ((conflicts == 1) and allow_conflicts) or \
				   (for_ref == ""):

					rotatedPieces.append(
						RotatedPieceWithRef(
							ref = (e0 << self.EDGE_SHIFT_LEFT) + e1,

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
	def list_rotated_pieces_to_dict(self, list_pieces, allow_conflicts=False, reference="", u=None, r=None, d=None, l=None, n=None, rotation=None):
		tmp = []
		for p in list_pieces:
			tmp.extend(self.getRotatedPieces( p, allow_conflicts, reference ))
			
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

			if p.ref in list_pieces_rotated.keys():
				list_pieces_rotated[p.ref].append(p)
			else:
				list_pieces_rotated[p.ref] = [ p ]

		return list_pieces_rotated


	def list_rotated_pieces_to_array(self, list_pieces):
		# Randomize the search
		rand_entropy = 99

		array = [ None ] * self.EDGE_DOMAIN_2_PIECE
		for ref in list_pieces.keys():
			tmp = []
			for p in sorted(list_pieces[ ref ], reverse=True, key=lambda x : x.score+random.randint(0,rand_entropy)):
				tmp.append(p.rotated_piece)
				
			array[ ref ] = tmp

		return array


	# ----- Prepare pieces and heuristics
	def prepare_pieces( self, local_seed=None ):
		W=self.board_w
		H=self.board_h
		WH=self.board_wh

		if self.DEBUG > 4:
			self.top("prepare pieces")
			self.info( " * Preparing pieces" )

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
		possible_references_corner = list(dict.fromkeys([ self.scenario.spaces_references[s] for s in self.static_spaces_corners]))
		for reference in possible_references_corner:
			tmp = self.list_rotated_pieces_to_dict(corner_pieces, reference=reference)
			master_index[ "corner_"+reference ] = self.list_rotated_pieces_to_array(tmp)

		# Border
		possible_references_border = list(dict.fromkeys([ self.scenario.spaces_references[s] for s in self.static_spaces_borders]))
		for (reference, (direction,rotation), conflicts) in itertools.product(possible_references_border, [("u",0),("r",1),("d",2),("l",3)], [False,True]):
			tmp = self.list_rotated_pieces_to_dict(border_pieces, rotation=rotation, allow_conflicts=conflicts, reference=reference)
			master_index[ "border_"+direction+("_conflicts" if conflicts else "")+"_"+reference ] = self.list_rotated_pieces_to_array(tmp)

		# Center
		possible_references_center = list(dict.fromkeys([ self.scenario.spaces_references[s] for s in self.static_spaces_centers]))
		for (reference, conflicts) in itertools.product(possible_references_center, [False,True]):
			tmp = self.list_rotated_pieces_to_dict(center_pieces, allow_conflicts=conflicts, reference=reference)
			master_index[ "center"+("_conflicts" if conflicts else "")+"_"+reference ] = self.list_rotated_pieces_to_array(tmp)

		# Fixed
		for [ fp, fs, fr ] in self.fixed:
			p = Piece( fp, self.pieces[fp][0], self.pieces[fp][1], self.pieces[fp][2], self.pieces[fp][3] )
			for i in range(fr):
				p.turnCW()
			reference = self.scenario.spaces_references[fs]
			tmp = self.list_rotated_pieces_to_dict(fixed_pieces, n=fp, rotation=fr, reference=reference)
			master_index[ "fixed"+str(fp)+"_"+reference ] = self.list_rotated_pieces_to_array(tmp)

			# Assuming neighbors of fixed pieces are always center_pieces
			reference = self.scenario.spaces_references[fs+W]
			tmp = self.list_rotated_pieces_to_dict(center_pieces, u=p.d, reference=reference)
			master_index[ "fixed"+str(fp)+"_s"+"_"+reference ] = self.list_rotated_pieces_to_array(tmp)

			reference = self.scenario.spaces_references[fs-1]
			tmp = self.list_rotated_pieces_to_dict(center_pieces, r=p.l, reference=reference)
			master_index[ "fixed"+str(fp)+"_w"+"_"+reference ] = self.list_rotated_pieces_to_array(tmp)

			reference = self.scenario.spaces_references[fs-W]
			tmp = self.list_rotated_pieces_to_dict(center_pieces, d=p.u, reference=reference)
			master_index[ "fixed"+str(fp)+"_n"+"_"+reference ] = self.list_rotated_pieces_to_array(tmp)

			reference = self.scenario.spaces_references[fs+1]
			tmp = self.list_rotated_pieces_to_dict(center_pieces, l=p.r, reference=reference)
			master_index[ "fixed"+str(fp)+"_e"+"_"+reference ] = self.list_rotated_pieces_to_array(tmp)


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

		if self.DEBUG > 4:
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
