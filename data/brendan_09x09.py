import puzzle

class Brendan_09x09( puzzle.Puzzle ):
	"""The Brendan 09x09 puzzle"""

	def __init__( self ):

		self.name = "brendan/pieces_09x09.txt.js"
		self.motifs_order = "jef"

		self.board_w = 9
		self.board_h = 9

		self.pieces = [


			[0,0,1,1],
			[0,0,1,4],
			[0,0,2,1],
			[0,0,2,2],
			[0,1,7,4],
			[0,1,8,1],
			[0,1,9,2],
			[0,1,10,2],
			[0,1,10,3],
			[0,1,10,4],
			[0,2,5,4],
			[0,2,7,3],
			[0,2,9,2],
			[0,2,12,2],
			[0,2,13,1],
			[0,2,13,4],
			[0,3,5,2],
			[0,3,7,2],
			[0,3,7,3],
			[0,3,8,3],
			[0,3,9,3],
			[0,3,11,1],
			[0,3,11,2],
			[0,3,13,3],
			[0,4,5,1],
			[0,4,5,4],
			[0,4,6,4],
			[0,4,8,3],
			[0,4,11,1],
			[0,4,12,1],
			[0,4,12,3],
			[0,4,13,4],
			[5,5,12,8],
			[5,6,5,9],
			[5,6,8,8],
			[5,6,9,7],
			[5,6,13,8],
			[5,7,6,8],
			[5,7,8,11],
			[5,7,11,12],
			[5,7,13,11],
			[5,8,6,7],
			[5,8,8,8],
			[5,8,10,8],
			[5,9,10,6],
			[5,10,9,9],
			[5,11,5,13],
			[5,11,11,10],
			[5,12,6,10],
			[5,12,10,11],
			[5,12,12,8],
			[6,6,8,12],
			[6,7,6,9],
			[6,7,10,13],
			[6,8,10,8],
			[6,8,13,7],
			[6,9,9,8],
			[6,9,9,9],
			[6,9,11,7],
			[6,10,8,10],
			[6,10,12,12],
			[6,10,13,11],
			[6,11,7,12],
			[6,11,11,13],
			[6,11,13,12],
			[6,12,9,10],
			[7,7,11,11],
			[7,7,12,9],
			[7,7,13,12],
			[7,9,11,13],
			[7,9,13,9],
			[7,10,12,10],
			[7,12,10,13],
			[7,13,8,13],
			[8,11,12,13],
			[8,12,13,9],
			[8,13,11,10],
			[9,9,10,13],
			[9,10,10,11],
			[10,11,12,12],
			[11,12,13,13]
		]

		# Fixed piece,space,rotation
		self.fixed = [
			[ 0,0,1 ], # we fix a corner
		]

		puzzle.Puzzle.__init__( self )


