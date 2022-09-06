import puzzle

class Brendan_08x08( puzzle.Puzzle ):
	"""The Brendan 08x08 puzzle"""

	name = "brendan/pieces_08x08.txt.js"
	aliases = [ "Brendan_08x08", "B8x8", "8x8" ]

	def __init__( self, extra_fixed=[] ):

		self.motifs_order = "jef"
		self.upside_down = False

		self.board_w = 8
		self.board_h = 8

		self.pieces = [

			[0,0,1,2],
			[0,0,2,1],
			[0,0,2,2],
			[0,0,2,3],
			[0,1,4,1],
			[0,1,5,3],
			[0,1,6,3],
			[0,1,8,1],
			[0,1,8,3],
			[0,1,10,1],
			[0,1,10,2],
			[0,1,11,1],
			[0,1,11,2],
			[0,2,4,1],
			[0,2,4,2],
			[0,2,4,3],
			[0,2,9,1],
			[0,2,9,2],
			[0,2,10,3],
			[0,3,4,2],
			[0,3,4,3],
			[0,3,5,1],
			[0,3,5,2],
			[0,3,9,1],
			[0,3,9,3],
			[0,3,10,2],
			[0,3,11,1],
			[0,3,11,3],
			[4,5,4,7],
			[4,5,10,6],
			[4,6,5,9],
			[4,6,7,5],
			[4,6,10,9],
			[4,7,4,9],
			[4,7,5,6],
			[4,8,7,11],
			[4,8,10,10],
			[4,9,6,5],
			[4,9,6,8],
			[4,10,11,8],
			[4,11,7,10],
			[4,11,8,6],
			[5,5,5,8],
			[5,5,11,10],
			[5,6,10,10],
			[5,7,5,10],
			[5,7,6,9],
			[5,8,6,6],
			[5,9,6,6],
			[5,9,8,11],
			[5,11,8,7],
			[6,6,8,11],
			[6,7,8,7],
			[6,7,11,7],
			[6,8,7,9],
			[6,9,10,7],
			[6,10,7,8],
			[7,8,9,11],
			[7,9,10,11],
			[7,10,10,8],
			[7,10,11,11],
			[7,11,9,8],
			[7,11,9,9],
			[8,8,9,11]
		]

		"""
		if with_fixed:
			# Fixed piece,space,rotation
			self.fixed = [
				[ 0,0,3 ], # we fix a corner
			]
		"""
	
		# Add extra fixed
		self.extra_fixed = extra_fixed

		puzzle.Puzzle.__init__( self )

puzzle.global_list.append(Brendan_08x08)
