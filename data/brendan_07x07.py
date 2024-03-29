import puzzle

class Brendan_07x07( puzzle.Puzzle ):
	"""The Brendan 07x07 puzzle"""

	name = "brendan/pieces_07x07.txt.js"
	aliases = [ "Brendan_07x07", "B7x7", "7x7" ]

	def __init__( self, params={} ):

		self.motifs_order = "jef"
		self.upside_down = False

		self.board_w = 7
		self.board_h = 7

		self.pieces = [

			[0,0,1,2],
			[0,0,1,3],
			[0,0,2,1],
			[0,0,3,2],
			[0,1,5,1],
			[0,1,6,1],
			[0,1,6,3],
			[0,1,7,2],
			[0,1,8,2],
			[0,1,8,3],
			[0,2,4,2],
			[0,2,5,3],
			[0,2,7,2],
			[0,2,8,2],
			[0,2,8,3],
			[0,2,9,1],
			[0,2,9,3],
			[0,3,4,1],
			[0,3,4,2],
			[0,3,5,1],
			[0,3,6,1],
			[0,3,6,3],
			[0,3,8,3],
			[0,3,9,1],
			[4,4,5,8],
			[4,4,7,5],
			[4,4,7,7],
			[4,5,5,7],
			[4,5,8,5],
			[4,6,5,7],
			[4,6,7,6],
			[4,8,6,9],
			[4,8,7,7],
			[4,8,9,5],
			[4,8,9,6],
			[4,9,6,8],
			[4,9,8,5],
			[4,9,9,6],
			[5,5,8,7],
			[5,5,9,7],
			[5,6,7,7],
			[5,6,8,6],
			[5,6,9,9],
			[5,9,7,9],
			[6,7,9,8],
			[6,8,7,7],
			[6,8,8,7],
			[6,9,8,9],
			[6,9,9,7]
		]

		# Fixed piece,space,rotation
		self.fixed = [
			[ 0,0,1 ], # we fix a corner
		]

		puzzle.Puzzle.__init__( self, params=params )

puzzle.global_list.append(Brendan_07x07)
