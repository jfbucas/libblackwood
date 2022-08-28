
import puzzle

class Tomy_EternityII_Blackwood( puzzle.Puzzle ):
	"""The full Eternity II puzzle without the clues and with Blackwood edge numbering"""

	name = "tomy/pieces.txt.EternityII_blackwood.js"
	aliases = [ "JB", "jb", "blackwood", "b" ]

	def __init__( self, extra_fixed=[] ):

		self.motifs_order = "jblackwood"
		self.upside_down = False

		self.board_w = 16
		self.board_h = 16

		# up, right. dowm, left
		self.pieces = [
		 [ 1, 17, 0, 0 ],
		 [ 1, 5, 0, 0 ],
		 [ 9, 17, 0, 0 ],
		 [ 17, 9, 0, 0 ],
		 [ 2, 1, 0, 1 ],
		 [ 10, 9, 0, 1 ],
		 [ 6, 1, 0, 1 ],
		 [ 6, 13, 0, 1 ],
		 [ 11, 17, 0, 1 ],
		 [ 7, 5, 0, 1 ],
		 [ 15, 9, 0, 1 ],
		 [ 8, 5, 0, 1 ],
		 [ 8, 13, 0, 1 ],
		 [ 21, 5, 0, 1 ],
		 [ 10, 1, 0, 9 ],
		 [ 18, 17, 0, 9 ],
		 [ 14, 13, 0, 9 ],
		 [ 19, 13, 0, 9 ],
		 [ 7, 9, 0, 9 ],
		 [ 15, 9, 0, 9 ],
		 [ 4, 5, 0, 9 ],
		 [ 12, 1, 0, 9 ],
		 [ 12, 13, 0, 9 ],
		 [ 20, 1, 0, 9 ],
		 [ 21, 1, 0, 9 ],
		 [ 2, 9, 0, 17 ],
		 [ 2, 17, 0, 17 ],
		 [ 10, 17, 0, 17 ],
		 [ 18, 17, 0, 17 ],
		 [ 7, 13, 0, 17 ],
		 [ 15, 9, 0, 17 ],
		 [ 20, 17, 0, 17 ],
		 [ 8, 9, 0, 17 ],
		 [ 8, 5, 0, 17 ],
		 [ 16, 13, 0, 17 ],
		 [ 22, 5, 0, 17 ],
		 [ 18, 1, 0, 5 ],
		 [ 3, 13, 0, 5 ],
		 [ 11, 13, 0, 5 ],
		 [ 19, 9, 0, 5 ],
		 [ 19, 17, 0, 5 ],
		 [ 15, 1, 0, 5 ],
		 [ 15, 9, 0, 5 ],
		 [ 15, 17, 0, 5 ],
		 [ 4, 1, 0, 5 ],
		 [ 20, 5, 0, 5 ],
		 [ 8, 5, 0, 5 ],
		 [ 16, 5, 0, 5 ],
		 [ 2, 13, 0, 13 ],
		 [ 10, 1, 0, 13 ],
		 [ 10, 9, 0, 13 ],
		 [ 6, 1, 0, 13 ],
		 [ 7, 5, 0, 13 ],
		 [ 4, 5, 0, 13 ],
		 [ 4, 13, 0, 13 ],
		 [ 8, 17, 0, 13 ],
		 [ 16, 1, 0, 13 ],
		 [ 16, 13, 0, 13 ],
		 [ 21, 9, 0, 13 ],
		 [ 22, 17, 0, 13 ],
		 [ 6, 18, 2, 2 ],
		 [ 14, 7, 2, 2 ],
		 [ 10, 3, 2, 10 ],
		 [ 2, 8, 2, 18 ],
		 [ 18, 22, 2, 18 ],
		 [ 14, 14, 2, 18 ],
		 [ 11, 10, 2, 18 ],
		 [ 20, 6, 2, 18 ],
		 [ 22, 8, 2, 18 ],
		 [ 3, 7, 2, 3 ],
		 [ 7, 12, 2, 3 ],
		 [ 14, 18, 2, 11 ],
		 [ 15, 4, 2, 11 ],
		 [ 20, 15, 2, 11 ],
		 [ 8, 3, 2, 11 ],
		 [ 14, 15, 2, 19 ],
		 [ 19, 15, 2, 19 ],
		 [ 3, 16, 2, 7 ],
		 [ 20, 3, 2, 7 ],
		 [ 16, 21, 2, 7 ],
		 [ 19, 18, 2, 15 ],
		 [ 18, 18, 2, 4 ],
		 [ 11, 4, 2, 4 ],
		 [ 18, 19, 2, 12 ],
		 [ 6, 14, 2, 12 ],
		 [ 8, 12, 2, 12 ],
		 [ 16, 20, 2, 12 ],
		 [ 2, 21, 2, 20 ],
		 [ 6, 22, 2, 20 ],
		 [ 4, 16, 2, 20 ],
		 [ 11, 12, 2, 8 ],
		 [ 19, 15, 2, 8 ],
		 [ 19, 4, 2, 8 ],
		 [ 4, 21, 2, 8 ],
		 [ 12, 14, 2, 8 ],
		 [ 21, 3, 2, 21 ],
		 [ 4, 19, 2, 22 ],
		 [ 20, 8, 2, 22 ],
		 [ 21, 6, 2, 22 ],
		 [ 22, 21, 2, 22 ],
		 [ 12, 15, 10, 10 ],
		 [ 12, 16, 10, 10 ],
		 [ 16, 19, 10, 10 ],
		 [ 22, 6, 10, 10 ],
		 [ 4, 15, 10, 18 ],
		 [ 3, 8, 10, 6 ],
		 [ 19, 8, 10, 6 ],
		 [ 4, 15, 10, 6 ],
		 [ 16, 11, 10, 6 ],
		 [ 15, 12, 10, 14 ],
		 [ 12, 15, 10, 14 ],
		 [ 20, 19, 10, 3 ],
		 [ 20, 16, 10, 3 ],
		 [ 14, 4, 10, 11 ],
		 [ 7, 12, 10, 11 ],
		 [ 12, 11, 10, 11 ],
		 [ 22, 16, 10, 11 ],
		 [ 3, 21, 10, 19 ],
		 [ 16, 12, 10, 7 ],
		 [ 8, 22, 10, 15 ],
		 [ 14, 22, 10, 4 ],
		 [ 6, 16, 10, 20 ],
		 [ 14, 19, 10, 20 ],
		 [ 20, 15, 10, 20 ],
		 [ 12, 22, 10, 8 ],
		 [ 21, 15, 10, 8 ],
		 [ 14, 6, 10, 16 ],
		 [ 19, 21, 10, 16 ],
		 [ 4, 3, 10, 16 ],
		 [ 20, 8, 10, 16 ],
		 [ 6, 20, 10, 21 ],
		 [ 12, 14, 10, 21 ],
		 [ 14, 16, 10, 22 ],
		 [ 11, 4, 10, 22 ],
		 [ 4, 3, 10, 22 ],
		 [ 16, 20, 10, 22 ],
		 [ 20, 7, 18, 18 ],
		 [ 6, 3, 18, 6 ],
		 [ 6, 11, 18, 6 ],
		 [ 6, 12, 18, 6 ],
		 [ 19, 21, 18, 6 ],
		 [ 15, 6, 18, 6 ],
		 [ 16, 12, 18, 6 ],
		 [ 21, 21, 18, 6 ],
		 [ 3, 4, 18, 14 ],
		 [ 18, 12, 18, 3 ],
		 [ 18, 22, 18, 3 ],
		 [ 3, 14, 18, 3 ],
		 [ 15, 12, 18, 3 ],
		 [ 6, 11, 18, 19 ],
		 [ 4, 22, 18, 19 ],
		 [ 11, 11, 18, 7 ],
		 [ 11, 19, 18, 7 ],
		 [ 22, 16, 18, 7 ],
		 [ 7, 7, 18, 4 ],
		 [ 7, 12, 18, 4 ],
		 [ 22, 7, 18, 4 ],
		 [ 7, 16, 18, 20 ],
		 [ 8, 6, 18, 20 ],
		 [ 21, 21, 18, 8 ],
		 [ 6, 20, 18, 16 ],
		 [ 14, 20, 18, 16 ],
		 [ 15, 11, 18, 22 ],
		 [ 4, 16, 18, 22 ],
		 [ 3, 4, 6, 14 ],
		 [ 4, 8, 6, 14 ],
		 [ 3, 3, 6, 11 ],
		 [ 11, 15, 6, 19 ],
		 [ 19, 21, 6, 19 ],
		 [ 4, 8, 6, 7 ],
		 [ 20, 16, 6, 7 ],
		 [ 21, 11, 6, 7 ],
		 [ 15, 15, 6, 15 ],
		 [ 12, 20, 6, 15 ],
		 [ 7, 21, 6, 4 ],
		 [ 7, 19, 6, 12 ],
		 [ 14, 4, 6, 20 ],
		 [ 12, 16, 6, 8 ],
		 [ 8, 15, 6, 8 ],
		 [ 7, 16, 6, 16 ],
		 [ 11, 16, 6, 21 ],
		 [ 7, 11, 6, 21 ],
		 [ 19, 8, 14, 14 ],
		 [ 22, 7, 14, 3 ],
		 [ 19, 12, 14, 11 ],
		 [ 8, 8, 14, 11 ],
		 [ 21, 7, 14, 19 ],
		 [ 14, 21, 14, 7 ],
		 [ 3, 19, 14, 7 ],
		 [ 16, 19, 14, 7 ],
		 [ 3, 3, 14, 15 ],
		 [ 15, 20, 14, 15 ],
		 [ 11, 7, 14, 4 ],
		 [ 21, 11, 14, 12 ],
		 [ 21, 22, 14, 12 ],
		 [ 22, 15, 14, 12 ],
		 [ 11, 22, 14, 20 ],
		 [ 19, 8, 14, 20 ],
		 [ 20, 20, 14, 20 ],
		 [ 19, 3, 14, 8 ],
		 [ 21, 8, 14, 16 ],
		 [ 22, 7, 14, 16 ],
		 [ 12, 19, 14, 21 ],
		 [ 12, 8, 14, 21 ],
		 [ 16, 3, 14, 21 ],
		 [ 22, 21, 14, 21 ],
		 [ 22, 7, 3, 3 ],
		 [ 19, 22, 3, 11 ],
		 [ 8, 15, 3, 11 ],
		 [ 11, 19, 3, 7 ],
		 [ 16, 15, 3, 7 ],
		 [ 3, 16, 3, 15 ],
		 [ 8, 8, 3, 4 ],
		 [ 3, 20, 3, 12 ],
		 [ 4, 22, 3, 12 ],
		 [ 22, 21, 3, 12 ],
		 [ 19, 15, 3, 20 ],
		 [ 4, 12, 3, 16 ],
		 [ 11, 4, 3, 21 ],
		 [ 11, 16, 3, 22 ],
		 [ 21, 21, 3, 22 ],
		 [ 21, 22, 3, 22 ],
		 [ 12, 22, 11, 11 ],
		 [ 20, 7, 11, 11 ],
		 [ 16, 15, 11, 11 ],
		 [ 19, 15, 11, 7 ],
		 [ 12, 12, 11, 7 ],
		 [ 19, 8, 11, 4 ],
		 [ 7, 22, 11, 20 ],
		 [ 16, 8, 11, 20 ],
		 [ 12, 20, 11, 8 ],
		 [ 12, 21, 11, 8 ],
		 [ 19, 20, 19, 19 ],
		 [ 16, 4, 19, 7 ],
		 [ 7, 4, 19, 4 ],
		 [ 7, 20, 19, 4 ],
		 [ 12, 15, 19, 4 ],
		 [ 4, 16, 19, 12 ],
		 [ 15, 22, 19, 20 ],
		 [ 21, 15, 19, 20 ],
		 [ 7, 21, 19, 8 ],
		 [ 4, 21, 19, 8 ],
		 [ 15, 12, 7, 15 ],
		 [ 20, 8, 7, 15 ],
		 [ 22, 20, 7, 4 ],
		 [ 16, 22, 7, 21 ],
		 [ 21, 22, 15, 15 ],
		 [ 12, 4, 15, 4 ],
		 [ 4, 21, 15, 12 ],
		 [ 16, 21, 15, 20 ],
		 [ 22, 8, 4, 4 ],
		 [ 8, 12, 4, 12 ],
		 [ 16, 20, 12, 8 ],
		 [ 21, 16, 20, 16 ],
		 [ 16, 22, 20, 22 ],
		 [ 21, 22, 8, 22 ],
		]

		# Fixed piece,space,rotation

		self.fixed = [
			[ 138,135,2 ], # as the last one, so that it is on masks[2]
		]

		# Add extra fixed
		self.fixed.extend(extra_fixed)

		puzzle.Puzzle.__init__( self )

puzzle.global_list.append(Tomy_EternityII_Blackwood)
