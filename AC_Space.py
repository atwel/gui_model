""" This is a module that constructs a 2-dimensional space the 
cells can move around in. Currently, it only supports Brownian
motion with a periodic boundary condition.


Written by Jon Atwell
"""
import numpy
import json


def within_radius(radius, point):

	the_list = []
	for x in range(int(point[0] - numpy.ceil(radius)),
		int(point[0] + numpy.ceil(radius) + 1)):
		for y in range(int(point[1]- numpy.ceil(radius)),
			int(point[1] + numpy.ceil(radius) + 1)):
			if ((point[0]-x)**2 + (point[1]-y)**2)**.5 <= radius:
				if (x,y) != point:
					the_list.append((x,y))
	return the_list



def create_overlap_lists(radius):
	""" This creates a lookup table so that we can quickly
	send updates to the right locations on the grid.
	"""
	vals = {}
	for i in range(-1,2):
		for j in range(-1,2):
			original = within_radius(radius, (0,0))
			new = within_radius(radius, (i,j))
			diffs = []
			for nw in new:
				if nw not in original:
					diffs.append(nw)
			vals[(i,j)] = diffs

	return vals



class Space:
	""" The  grid the cells move around on.
	"""

	def __init__(self, VARS):

		self.VARS = VARS

		self.cell_radius = .005

		self.last_added_rule = 0
		self.rule_counts = {}
		self.neighbor_grid = numpy.empty(shape=
			(self.VARS.SPACE_HEIGHT, self.VARS.SPACE_WIDTH),
			dtype = list)
		self.overlap_lists = create_overlap_lists(self.VARS.RADIUS)

		self.distribute_into_space()


	def add_rule(self, r_type):

		try:
			self.rule_counts[r_type] += 1
		except:
			self.rule_counts[r_type] = 1


	def remove_rule(self, r_type):
		self.rule_counts[r_type] -= 1


	def taurus_map(self, (new_x, new_y)):
		""" A method that establishes the periodic boundary condition.
		"""

		if self.VARS.SPACE_WIDTH < new_x:    
			new_x = new_x - self.VARS.SPACE_WIDTH
		elif new_x < 1:
			new_x = self.VARS.SPACE_WIDTH + new_x

		if self.VARS.SPACE_HEIGHT < new_y:
			new_y = new_y - self.VARS.SPACE_HEIGHT
		elif new_y < 1:
			new_y = self.VARS.SPACE_HEIGHT + new_y

		return new_x, new_y


	def map_list(self, loc, the_list):

		new_list = []

		for spot in the_list:
			x = spot[0] + loc[0]
			y = spot[1] + loc[1]
			new_list.append(self.taurus_map((x, y)))

		return new_list


	def distribute_into_space(self):
		""" A method to array the cells onto the space. There is
		no problem with multiple cells occupying the same 
		spot, so they are distributed uniform-at-random.
		"""
		if self.VARS.MOBILE:
			for cl in self.VARS.CELLS:
				someone_here = True
				while someone_here:
					x = self.VARS.RNG.randint(1, self.VARS.SPACE_WIDTH)
					y = self.VARS.RNG.randint(1, self.VARS.SPACE_HEIGHT)
					someone_here = self.is_some_one_here(x,y)

				cl.set_location(x,y)
				try:
					self.neighbor_grid[y-1][x-1].append(cl)
				except:
					self.neighbor_grid[y-1][x-1] = [cl]
		else:

			x,y = (1,1)
			for cl in self.VARS.CELLS:
				if x <= self.VARS.SPACE_WIDTH:
					cl.set_location(x,y)
					try:
						self.neighbor_grid[y-1][x-1].append(cl)
					except:
						self.neighbor_grid[y-1][x-1] = [cl]
					x +=1
				else:
					x = 1
					y += 1
					cl.set_location(x,y)
					try:
						self.neighbor_grid[y-1][x-1].append(cl)
					except:
						self.neighbor_grid[y-1][x-1] = [cl]
					x +=1

		#Setting up an initial list of neighbors    
		for cl in self.VARS.CELLS:
			area = within_radius(self.VARS.RADIUS, cl.get_location())
			for point in area:
				x, y = self.taurus_map(point)
				try:
					cl.neighbors.extend(self.neighbor_grid[y-1][x-1])
				except:
					pass


	def is_some_one_here(self, x,y):
		the_list = []
		area = within_radius(self.cell_radius, (x, y))
		for point in area:
			x, y = self.taurus_map(point)
			try:
				the_list.extend(self.neighbor_grid[y-1][x-1])
			except:
				pass

		if the_list == []:
			return False
		return True


	def print_grid(self):
		y,x = self.neighbor_grid.shape
		for i in range(y):
			row = ""
			for j in range(x):
				cells = self.neighbor_grid[i][j]
				if cells== None:
					row += "|______|"
				else:
					if cells== []:
						row += "|______|"
				cnt = len(cells)
				if cnt == 1:
					row += "|__" + str(cells[0].id)+"___|"
				elif cnt == 2:
					row += "|_"
					for k in cells:
						row += str(k.id) + "-"
					row += "_|"
				elif cnt == 3:
					row += "|"
					for k in cells:
						row += str(k.id) + "-"
					row += "|"
		print row

	def transport_cell(self, cell, location):

		current = cell.get_location()
		self.neighbor_grid[current[1]-1][current[0]-1].remove(cell)
		cell.neighbors = []
		cell.set_location(location[0], location[1])

		for loc in self.map_list(location, within_radius(self.VARS.RADIUS,location)):

			news = self.neighbor_grid[loc[1]-1][loc[0]-1]
			if news != []:
				for ngh in news:
					cell.neighbors.append(ngh)
					ngh.neighbors.append(cell)

	
	def move_cell(self, cell,brownian=False):
		current = cell.get_location()

		x_move =  self.VARS.RNG.randint(-1,1)
		y_move =  self.VARS.RNG.randint(-1,1)
		new_x, new_y = self.taurus_map((current[0] + x_move,
			current[1] +  y_move))

		cell.set_location(new_x, new_y)

		self.update_grid(current, cell, x_move, y_move)


	def update_grid(self, old_spot, cell, x_move, y_move):

		new = cell.get_location()
		self.neighbor_grid[old_spot[1]-1][old_spot[0]-1].remove(cell)
		try:
			self.neighbor_grid[new[1]-1][new[0]-1].append(cell)
		except:
			self.neighbor_grid[new[1]-1][new[0]-1] = [cell]

		old_spots= self.map_list(cell.get_location(), 
			self.overlap_lists[(-1*x_move, -1*y_move)])

		to_remove = []
		for ngh in cell.neighbors:
			if ngh.get_location() in old_spots:
				ngh.neighbors.remove(cell)
				to_remove.append(ngh)

		for ngh in to_remove:
			cell.neighbors.remove(ngh)

		new_spots = self.map_list(old_spot, 
			self.overlap_lists[(x_move,y_move)])

		for loc in new_spots:
			try:
				news = self.neighbor_grid[loc[1]-1][loc[0]-1]
				for ngh in news:
					if ngh not in cell.neighbors:
						cell.neighbors.append(ngh)
						ngh.neighbors.append(cell)

			except:
				pass


	def get_random_cell(self, who=None):
		""" A function to select a cell, weighted by the number
		of rules it has. The who argument is used to prevent self
		pass backs in the non-spatial variant."""

		candidates = []
		cnts = []
		for i in self.VARS.CELLS:
			if i != who:
				cnts.append(i.count_rules)
				for j in range(i.count_rules):
					candidates.append(i)

		return self.VARS.RNG.choice(candidates)



	def activate_random_rule(self, debug=False):
		"""A function to select a random rule from within a cell. It first
		randomly selects a cell, weighted by rule counts. Then it selects
		a rule from that cell, weighted by the rules' frequencies."""

		candidate = self.get_random_cell()
		self.VARS.ACTIVEA = candidate.id
		candidate.set_active_rule(candidate.get_random_rule())
		if self.VARS.MOBILE:
			self.move_cell(candidate)
		candidate.chain_step(debug)


	def activate_random_cell(self, debug=False):
		"""A function to select a random rule from within a cell. It first
		randomly selects a cell, weighted by rule counts. Then it selects
		a rule from that cell, weighted by the rules' frequencies."""

		candidate = self.get_random_cell()

		if self.VARS.MOBILE:
			self.move_cell(candidate)
		has = candidate.has_Product()
		if has != None:
			candidate.set_active_rule(candidate.get_random_rule_of_type(has))
			candidate.chain_step(debug)
		else:
			candidate.set_active_rule(candidate.get_random_rule())
			candidate.chain_step(debug)


	def remove_random_rule(self):
		"""This method is the main way in which selection pressure is
		implemented. If a rule is reproduced, this method removes one
		uniform-at-random."""

		a = self.get_random_cell()
		a.remove_ProductRule(a.get_random_rule())


	def load_checkpoint(self, in_name):
		self.neighbor_grid = numpy.empty(shape=(self.VARS.SPACE_HEIGHT,
			self.VARS.SPACE_WIDTH), dtype=list)
		in_ = open(str(in_name)+".json", "r")
		data = json.load(in_,encoding="ascii")

		self.rule_counts = {}
		for cell in self.VARS.CELLS:
			cell.reload_data(data["cells"][str(cell.id)])

		the_rest = data["the_rest"]
		self.VARS.MASTER_COUNT = the_rest["step_count"]

		urn_data = the_rest["urn"]
		urn = {}
		for key, count in urn_data:
			hold = []
			urn[key] = []
			for i in count:
				urn[key].append(AC_Products.Product(self,urn,key, self.initial_energy))
		self.VARS.URN.collection = urn
		self.VARS.CHECKPOINT = int(the_rest["checkpoint"]) +1
		rng_pre = the_rest["rng_state"]
		real = (rng_pre[0],tuple(rng_pre[1]),rng_pre[2])
		self.VARS.RNG.setstate(real)
		for cell in self.VARS.CELLS:
			if cell.product_netrules.values() != {}:
				if self.VARS.MOBILE:
					for ngh in self.VARS.CELLS:
						if ngh != cell:
							if ngh.product_netrules.values() != {}:
								for r1 in cell.product_netrules.values():
									for r2 in ngh.product_netrules.values():
										self.VARS.PRODUCT_RULE_NET.add_edge(r1,r2)
				else:
					for ngh in cell.neighbors:
						if ngh.product_netrules.values() != {}:
							for r1 in cell.product_netrules.values():
								for r2 in ngh.product_netrules.values():
									self.VARS.PRODUCT_RULE_NET.add_edge(r1,r2)
	def cell_action(self,inc):
		#n = int(1/float(inc))*10
		for i in range(self.VARS.RATE):
			self.activate_random_rule()

	def clear_data_window(self,inc):
		self.VARS.DATA_LABELS = []
