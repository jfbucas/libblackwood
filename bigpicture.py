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

import png
import math

# Local Libs
import defs
import puzzle
import scenarios
import data


class BigPicture( defs.Defs ):
	"""Defines exploration"""

	puzzle = None
	valid_pieces_depth = None

	# ----- Init the puzzle
	def __init__( self ):
		"""
		Initialize
		"""

		defs.Defs.__init__( self )

		self.puzzle = data.loadPuzzle()
		self.valid_pieces = self.filterValidPieces( self.puzzle.static_valid_pieces )
		
		#self.fixPiece(self.puzzle, self.valid_pieces)
		#self.getJobs(self.valid_pieces, max_width=128, max_height=128)
		self.getJobs(self.valid_pieces)
		self.getImages()


	# ----- Filter based on edges/patterns the valid_pieces list
	def filterValidPieces( self, valid_pieces ):

		if valid_pieces == None:
			return None

		current_valid_pieces = valid_pieces

		removed = -1
		while removed != 0:
			removed = 0
			new_valid_pieces = [None] * self.puzzle.board_wh

			patterns_border = {"u":{0:True}, "r":{0:True}, "d":{0:True}, "l":{0:True}}
			patterns_seen = [ ]
			for space in range(self.puzzle.board_wh):
				patterns_seen.append( {"u":{}, "r":{}, "d":{}, "l":{}} )

			for space in range(self.puzzle.board_wh):
				for i in range(0, self.MAX_NB_COLORS):
					patterns_seen[ space ]["u"][i] = False
					patterns_seen[ space ]["r"][i] = False
					patterns_seen[ space ]["d"][i] = False
					patterns_seen[ space ]["l"][i] = False

			for space in range(self.puzzle.board_wh):
				for p in current_valid_pieces[ space ]:
					patterns_seen[ space ]["u"][p.u] = True
					patterns_seen[ space ]["r"][p.r] = True
					patterns_seen[ space ]["d"][p.d] = True
					patterns_seen[ space ]["l"][p.l] = True

				#print(space)
				#print(patterns_seen[space]["u"])
				#print(patterns_seen[space]["r"])
				#print(patterns_seen[space]["d"])
				#print(patterns_seen[space]["l"])

			for space in range(self.puzzle.board_wh):
				new_valid_list = []

				space_u_patterns = patterns_border["d"]
				space_r_patterns = patterns_border["l"]
				space_d_patterns = patterns_border["u"]
				space_l_patterns = patterns_border["r"]
					
				
				if ((space % self.puzzle.board_w) != 0          )		: space_l_patterns = patterns_seen[space-1]["r"]
				if ((space % self.puzzle.board_w) != (self.puzzle.board_w-1))	: space_r_patterns = patterns_seen[space+1]["l"]
				if (space >= self.puzzle.board_w)				: space_u_patterns = patterns_seen[space-self.puzzle.board_w]["d"]
				if (space < (self.puzzle.board_wh - self.puzzle.board_w))	: space_d_patterns = patterns_seen[space+self.puzzle.board_w]["u"]



				for p in current_valid_pieces[ space ]:
					if not space_u_patterns[ p.u ] or \
					   not space_r_patterns[ p.r ] or \
					   not space_d_patterns[ p.d ] or \
					   not space_l_patterns[ p.l ]:
						removed += 1
					else:
						new_valid_list.append(p)

				if len(new_valid_list) == 0:
					print("Filter Valid Piece has reached a deadend")
					return None

				new_valid_pieces[space] = new_valid_list

			current_valid_pieces = new_valid_pieces


			
			if self.DEBUG_STATIC > 0:
			#if True:
				self.info( " * New Valid pieces" )
				a = []
				for space in range(self.puzzle.board_wh):
					a.append(len(new_valid_pieces[ space ]))

				self.printArray( a, array_w=self.puzzle.board_w, array_h=self.puzzle.board_h)
				

				#if self.DEBUG_STATIC > 4:
				#	for space in range(self.puzzle.board_wh):
				#		if self.static_spaces_type[ space ] == "border":
				#			print(self.static_valid_pieces[ space ])
		
		return current_valid_pieces

	
	# ----- Fix an piece in the valid_pieces
	def fixPiece( self, valid_pieces, piece_number, piece_space, piece_rotation):

		if valid_pieces == None:
			return None

		new_valid_pieces = [None] * self.puzzle.board_wh
		for space in range(self.puzzle.board_wh):
			new_valid_list = []

			for p in valid_pieces[ space ]:
				if space == piece_space:
					# on the space, we keep only that piece
					if p.p == piece_number and p.rotation == piece_rotation:
						new_valid_list.append(p)
				else:
					# everywhere else, we remove that piece
					if p.p != piece_number:
						new_valid_list.append(p)

			if len(new_valid_list) == 0:
				print("Fix Piece has reached a deadend on space", space)
				return None

			new_valid_pieces[space] = new_valid_list
	
		return new_valid_pieces



	# ----- 
	def getJobs( self, valid_pieces, pre_fixed=[], max_width=1024, max_height=1024):

		if valid_pieces == None:
			return None

		width = {}
		height = {}

		all_valid_pieces = {}
		current_valid_pieces = valid_pieces

		#for x in pre_fixed:
		#	current_valid_pieces = self.fixPiece( current_valid_pieces ....)

		#depth = len(self.puzzle.extra_fixed+self.puzzle.fixed+pre_fixed)
		#new_valid_

		depth = len(self.puzzle.extra_fixed+self.puzzle.fixed)

		all_valid_pieces[ depth-1 ] = [ (0, 0,  current_valid_pieces) ]
		width[ depth-1 ] = 1
		height[ depth-1 ] = 1

		while depth < self.puzzle.board_wh:

			orientation = depth % 2
			width[ depth ] = 0
			height[ depth ] = 0
			all_valid_pieces[ depth ] = []


			new_column_width = [1] * (width[depth-1])
			new_line_height  = [1] * (height[depth-1])

			tmp_valid_pieces = []

			for old_x, old_y, current_valid_pieces in all_valid_pieces[ depth-1 ]:
				
				#print("Depth", depth, "Old coordonates", old_x,",",old_y)


				lowest_valid_pieces = self.puzzle.board_wh*4
				best_space = None

				# Look for the space with the minimum possibilities
				for space in range(self.puzzle.board_wh):
					if  len(current_valid_pieces[ space ]) > 1:
						if  len(current_valid_pieces[ space ]) < lowest_valid_pieces:
							lowest_valid_pieces = len(current_valid_pieces[ space ])
							best_space = space

				if best_space == None:
					print("No best_space found, continuing")
					continue


				# Add the new jobs
				new_x = 0
				new_y = 0
				for  p in current_valid_pieces[ best_space ]:
					new_valid_pieces = self.filterValidPieces( self.fixPiece( current_valid_pieces, p.p, best_space, p.rotation) )
					if new_valid_pieces != None:
						tmp_valid_pieces.append( (old_x, new_x, old_y, new_y, new_valid_pieces ) )

						if orientation == 0:
							new_x += 1
							if new_x > new_column_width[old_x]:
								new_column_width[old_x] = new_x
						else:
							new_y += 1
							if new_y > new_line_height[old_y]:
								new_line_height[old_y] = new_y

				
			# Adjust the coordinates of the jobs
			new_column_position = [0]
			for n in new_column_width:
				new_column_position.append( new_column_position[-1] + n )

			new_line_position = [0]
			for n in new_line_height:
				new_line_position.append( new_line_position[-1] + n )

			for old_x, new_x, old_y, new_y, valid_pieces in tmp_valid_pieces:
				actual_x = new_x+new_column_position[old_x]
				actual_y = new_y+new_line_position[old_y]

				#print("Depth", depth, "Coordonates", old_x,old_y, " -> ", actual_x, actual_y)

				all_valid_pieces[ depth ].append( (actual_x, actual_y, new_valid_pieces ) )


			width[ depth ]  = new_column_position[-1]
			height[ depth ] = new_line_position[-1]

			print("Depth", depth, "Size of the jobs:", width[depth], "x", height[depth])
			print()

			if width[ depth ] > max_width and height[ depth ] > max_height:
					break
				
			depth += 1


		print("Len of valid_pieces:", len(all_valid_pieces[-1]))

		for d in all_valid_pieces:
			output = ""
			for x, y, current_valid_pieces in all_valid_pieces[d]:
				jobid = str(d)+"_"+str(x)+"_"+str(y)
				extra_fixed=[]
				for space in range(self.puzzle.board_wh):
					if  (len(current_valid_pieces[ space ]) == 1) and (self.puzzle.static_spaces_type[space] != "fixed"): 
						piece = current_valid_pieces[ space ][0]
						extra_fixed.append( (piece.p, space, piece.rotation) )
				output += jobid+"|"+str(extra_fixed)+"\n"
			
			jobsfile = open( "jobs/"+self.getFileFriendlyName( self.puzzle.name )+"_"+str(d)+"_"+str(pre_fixed)+".jobs.txt", "w" )
			jobsfile.write(output)
			jobsfile.close()

		return all_valid_pieces[-1]


	def getImages( self, pre_fixed=[] ):

		# Read the data
		for depth in range(-1, self.puzzle.board_wh):
			filename = "jobs/"+self.getFileFriendlyName( self.puzzle.name )+"_"+str(depth)+"_"+str(pre_fixed)+".jobs.txt"

			if os.path.exists(filename):
				coordinates=[]

				jobsfile = open( "jobs/"+self.getFileFriendlyName( self.puzzle.name )+"_"+str(depth)+"_"+str(pre_fixed)+".jobs.txt", "r" )
				max_x = 0
				max_y = 0
				for line in jobsfile:
					if line.startswith('#'):
						continue
					line = line.strip('\n').strip(' ')
					line = line.split("|")
					line = line[0].split("_")
					x=int(line[1])
					y=int(line[2])
					if x > max_x:
						max_x = x
					if y > max_y:
						max_y = y
					coordinates.append( (x, y) )
				jobsfile.close()


				# Create the blank image
				w = png.Writer(max_x+1, max_y+1, greyscale=True)
				img = []
				for h in range(max_y+1):
					l = [ 0 ] * (max_x+1)
					img.append(l)

				# Insert the jobs
				for x,y in coordinates:
					img[y][x] = 255

				# Write the image
				f = open("jobs/"+self.getFileFriendlyName( self.puzzle.name )+"_"+str(depth)+"_"+str(pre_fixed)+".png", 'wb')      # binary mode is important
				w.write(f, img)
				f.close()


if __name__ == "__main__":

	e = BigPicture()



# Lapin
