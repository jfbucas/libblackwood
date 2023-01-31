
import puzzle

class Tomy_4x4( puzzle.Puzzle ):
	"""The demo puzzle provided on Tomy's website"""

	name = "tomy/pieces.txt.4x4.js"
	aliases = [ "Tomy_4x4", "T4x4", "4x4" ]

	def __init__( self, params={} ):

		self.motifs_order = "jef"
		self.upside_down = False

		self.board_w = 4
		self.board_h = 4

		self.pieces = [
			[0,4,3,0] ,
			[0,0,3,4] ,
			[4,0,0,4] ,
			[3,0,0,3] ,
			[2,1,2,2] ,
			[1,1,1,2] ,
			[1,1,2,2] ,
			[1,1,2,2] ,
			[3,1,3,0] ,
			[4,1,4,0] ,
			[4,1,3,0] ,
			[3,1,4,0] ,
			[3,2,3,0] ,
			[4,2,4,0] ,
			[3,2,4,0] ,
			[4,2,3,0]
		]
	
		puzzle.Puzzle.__init__( self, params=params )


puzzle.global_list.append(Tomy_4x4)
