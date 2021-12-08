
import puzzle

class Tomy_EternityII( puzzle.Puzzle ):
	"""The full Eternity II puzzle"""

	def __init__( self, with_clues=True  ):

		self.name = "EternityII"
		self.motifs_order = "jef"

		self.board_w = 16
		self.board_h = 16

		# up, right. dowm, left
		self.pieces = [
			[ 8,22,0,0 ],
			[ 8,4,0,0 ],
			[ 16,22,0,0 ],
			[ 22,16,0,0 ],
			[ 7,8,0,8 ],
			[ 15,16,0,8 ],
			[ 3,8,0,8 ],
			[ 3,12,0,8 ],
			[ 14,22,0,8 ],
			[ 2,4,0,8 ],
			[ 10,16,0,8 ],
			[ 1,4,0,8 ],
			[ 1,12,0,8 ],
			[ 18,4,0,8 ],
			[ 15,8,0,16 ],
			[ 21,22,0,16 ],
			[ 11,12,0,16 ],
			[ 20,12,0,16 ],
			[ 2,16,0,16 ],
			[ 10,16,0,16 ],
			[ 5,4,0,16 ],
			[ 13,8,0,16 ],
			[ 13,12,0,16 ],
			[ 19,8,0,16 ],
			[ 18,8,0,16 ],
			[ 7,16,0,22 ],
			[ 7,22,0,22 ],
			[ 15,22,0,22 ],
			[ 21,22,0,22 ],
			[ 2,12,0,22 ],
			[ 10,16,0,22 ],
			[ 19,22,0,22 ],
			[ 1,16,0,22 ],
			[ 1,4,0,22 ],
			[ 9,12,0,22 ],
			[ 17,4,0,22 ],
			[ 21,8,0,4 ],
			[ 6,12,0,4 ],
			[ 14,12,0,4 ],
			[ 20,16,0,4 ],
			[ 20,22,0,4 ],
			[ 10,8,0,4 ],
			[ 10,16,0,4 ],
			[ 10,22,0,4 ],
			[ 5,8,0,4 ],
			[ 19,4,0,4 ],
			[ 1,4,0,4 ],
			[ 9,4,0,4 ],
			[ 7,12,0,12 ],
			[ 15,8,0,12 ],
			[ 15,16,0,12 ],
			[ 3,8,0,12 ],
			[ 2,4,0,12 ],
			[ 5,4,0,12 ],
			[ 5,12,0,12 ],
			[ 1,22,0,12 ],
			[ 9,8,0,12 ],
			[ 9,12,0,12 ],
			[ 18,16,0,12 ],
			[ 17,22,0,12 ],
			[ 3,21,7,7 ],
			[ 11,2,7,7 ],
			[ 15,6,7,15 ],
			[ 7,1,7,21 ],
			[ 21,17,7,21 ],
			[ 11,11,7,21 ],
			[ 14,15,7,21 ],
			[ 19,3,7,21 ],
			[ 17,1,7,21 ],
			[ 6,2,7,6 ],
			[ 2,13,7,6 ],
			[ 11,21,7,14 ],
			[ 10,5,7,14 ],
			[ 19,10,7,14 ],
			[ 1,6,7,14 ],
			[ 11,10,7,20 ],
			[ 20,10,7,20 ],
			[ 6,9,7,2 ],
			[ 19,6,7,2 ],
			[ 9,18,7,2 ],
			[ 20,21,7,10 ],
			[ 21,21,7,5 ],
			[ 14,5,7,5 ],
			[ 21,20,7,13 ],
			[ 3,11,7,13 ],
			[ 1,13,7,13 ],
			[ 9,19,7,13 ],
			[ 7,18,7,19 ],
			[ 3,17,7,19 ],
			[ 5,9,7,19 ],
			[ 14,13,7,1 ],
			[ 20,10,7,1 ],
			[ 20,5,7,1 ],
			[ 5,18,7,1 ],
			[ 13,11,7,1 ],
			[ 18,6,7,18 ],
			[ 5,20,7,17 ],
			[ 19,1,7,17 ],
			[ 18,3,7,17 ],
			[ 17,18,7,17 ],
			[ 13,10,15,15 ],
			[ 13,9,15,15 ],
			[ 9,20,15,15 ],
			[ 17,3,15,15 ],
			[ 5,10,15,21 ],
			[ 6,1,15,3 ],
			[ 20,1,15,3 ],
			[ 5,10,15,3 ],
			[ 9,14,15,3 ],
			[ 10,13,15,11 ],
			[ 13,10,15,11 ],
			[ 19,20,15,6 ],
			[ 19,9,15,6 ],
			[ 11,5,15,14 ],
			[ 2,13,15,14 ],
			[ 13,14,15,14 ],
			[ 17,9,15,14 ],
			[ 6,18,15,20 ],
			[ 9,13,15,2 ],
			[ 1,17,15,10 ],
			[ 11,17,15,5 ],
			[ 3,9,15,19 ],
			[ 11,20,15,19 ],
			[ 19,10,15,19 ],
			[ 13,17,15,1 ],
			[ 18,10,15,1 ],
			[ 11,3,15,9 ],
			[ 20,18,15,9 ],
			[ 5,6,15,9 ],
			[ 19,1,15,9 ],
			[ 3,19,15,18 ],
			[ 13,11,15,18 ],
			[ 11,9,15,17 ],
			[ 14,5,15,17 ],
			[ 5,6,15,17 ],
			[ 9,19,15,17 ],
			[ 19,2,21,21 ],
			[ 3,6,21,3 ],
			[ 3,14,21,3 ],
			[ 3,13,21,3 ],
			[ 20,18,21,3 ],
			[ 10,3,21,3 ],
			[ 9,13,21,3 ],
			[ 18,18,21,3 ],
			[ 6,5,21,11 ],
			[ 21,13,21,6 ],
			[ 21,17,21,6 ],
			[ 6,11,21,6 ],
			[ 10,13,21,6 ],
			[ 3,14,21,20 ],
			[ 5,17,21,20 ],
			[ 14,14,21,2 ],
			[ 14,20,21,2 ],
			[ 17,9,21,2 ],
			[ 2,2,21,5 ],
			[ 2,13,21,5 ],
			[ 17,2,21,5 ],
			[ 2,9,21,19 ],
			[ 1,3,21,19 ],
			[ 18,18,21,1 ],
			[ 3,19,21,9 ],
			[ 11,19,21,9 ],
			[ 10,14,21,17 ],
			[ 5,9,21,17 ],
			[ 6,5,3,11 ],
			[ 5,1,3,11 ],
			[ 6,6,3,14 ],
			[ 14,10,3,20 ],
			[ 20,18,3,20 ],
			[ 5,1,3,2 ],
			[ 19,9,3,2 ],
			[ 18,14,3,2 ],
			[ 10,10,3,10 ],
			[ 13,19,3,10 ],
			[ 2,18,3,5 ],
			[ 2,20,3,13 ],
			[ 11,5,3,19 ],
			[ 13,9,3,1 ],
			[ 1,10,3,1 ],
			[ 2,9,3,9 ],
			[ 14,9,3,18 ],
			[ 2,14,3,18 ],
			[ 20,1,11,11 ],
			[ 17,2,11,6 ],
			[ 20,13,11,14 ],
			[ 1,1,11,14 ],
			[ 18,2,11,20 ],
			[ 11,18,11,2 ],
			[ 6,20,11,2 ],
			[ 9,20,11,2 ],
			[ 6,6,11,10 ],
			[ 10,19,11,10 ],
			[ 14,2,11,5 ],
			[ 18,14,11,13 ],
			[ 18,17,11,13 ],
			[ 17,10,11,13 ],
			[ 14,17,11,19 ],
			[ 20,1,11,19 ],
			[ 19,19,11,19 ],
			[ 20,6,11,1 ],
			[ 18,1,11,9 ],
			[ 17,2,11,9 ],
			[ 13,20,11,18 ],
			[ 13,1,11,18 ],
			[ 9,6,11,18 ],
			[ 17,18,11,18 ],
			[ 17,2,6,6 ],
			[ 20,17,6,14 ],
			[ 1,10,6,14 ],
			[ 14,20,6,2 ],
			[ 9,10,6,2 ],
			[ 6,9,6,10 ],
			[ 1,1,6,5 ],
			[ 6,19,6,13 ],
			[ 5,17,6,13 ],
			[ 17,18,6,13 ],
			[ 20,10,6,19 ],
			[ 5,13,6,9 ],
			[ 14,5,6,18 ],
			[ 14,9,6,17 ],
			[ 18,18,6,17 ],
			[ 18,17,6,17 ],
			[ 13,17,14,14 ],
			[ 19,2,14,14 ],
			[ 9,10,14,14 ],
			[ 20,10,14,2 ],
			[ 13,13,14,2 ],
			[ 20,1,14,5 ],
			[ 2,17,14,19 ],
			[ 9,1,14,19 ],
			[ 13,19,14,1 ],
			[ 13,18,14,1 ],
			[ 20,19,20,20 ],
			[ 9,5,20,2 ],
			[ 2,5,20,5 ],
			[ 2,19,20,5 ],
			[ 13,10,20,5 ],
			[ 5,9,20,13 ],
			[ 10,17,20,19 ],
			[ 18,10,20,19 ],
			[ 2,18,20,1 ],
			[ 5,18,20,1 ],
			[ 10,13,2,10 ],
			[ 19,1,2,10 ],
			[ 17,19,2,5 ],
			[ 9,17,2,18 ],
			[ 18,17,10,10 ],
			[ 13,5,10,5 ],
			[ 5,18,10,13 ],
			[ 9,18,10,19 ],
			[ 17,1,5,5 ],
			[ 1,13,5,13 ],
			[ 9,19,13,1 ],
			[ 18,9,19,9 ],
			[ 9,17,19,17 ],
			[ 18,17,1,17 ],
		]

		# Fixed piece,space,rotation

		self.fixed = []

		if with_clues:
			self.fixed.extend( [
				[ 180,210,3 ],
				[ 207,34,3 ],
				[ 248,221,0 ],
				[ 254,45,3 ]
				] )

		# Mandatory piece in the middle
		self.fixed.extend( [
			[ 138,135,2 ], # as the last one, so that it is on masks[2]
			] )

		puzzle.Puzzle.__init__( self )

