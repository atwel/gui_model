""" This module contains the classes Product and Urn. The former is the core
object of exchange, the latter is a collection of individual units dispersed
according to the rules of the Urn. See EOM (Padgett and Powell 2012)
p.76 for definitions of Urn rules.


Written by Jon Atwell
"""

import collections

class Product:
	""" This class is for the fundamental extra-cellular unit, some sort of
	distinguishable goods that are passed around by the cells and transformed
	along the way.
	"""


	def __init__(self, type, VARS,energy=None):
		self.VARS = VARS
		self.x = 0
		self.y = 0
		if energy == None:
			self.energy = self.VARS.INITIAL_ENERGY
		else: 
			self.energy = energy
	
		self.type = int(type)



	def __str__(self):
		a = "Product is type %d and has energy %d" %(self.type,
			self.energy)
		return a

	def set_location(self, loc):
		self.x = loc[0]
		self.y = loc[1]

	def get_type(self):
		""" Simple reporter for the product's current type."""
		return self.type
    
    
	def apply_ProductRule(self, product_rule, cost):
		""" A method for transforming the Product's type based on the skill
		embodied in the ProductRule argument 'product_rule'.
		"""
		try:
			if self.type != product_rule.get_input():
				print "This ProductRule can't transform this Product."
			else:
				self.type = product_rule.get_output()
				self.use_energy(cost)
		except:
			a = ("%s is not a ProductRule and therefore can't transform"+
				" a Product.") %type(product_rule)
			raise TypeError(a)


	def replenish_energy(self):
		self.energy = self.VARS.INITIAL_ENERGY


	def use_energy(self, amount):
		self.energy -= amount


	def get_energy(self):
		return self.energy




class Urn:
	""" An Urn is a collection of products that has 8 different possible
	search methods for determining whether the the input product is available
	when requested. Definitions appear in EOM, p.76. The constructor creates
	the appropriate collection of products but the request_product() method is
	what really implements the search methods based on the Urn type
	(fixed-rich, fixed-poor, endo-rich and endo-poor) [where 'endo' means
	endogenous] and the calling Cell's search intelligence 
	(selective or random).
	"""

	def __init__(self, VARS):
		""" urn_type = rule structure for determining product availability
		count_product_types = number of possible products
		count_products = how many actual units in the collection
		"""
		self.VARS = VARS
		self.collection = collections.defaultdict(list)

		if  "fixed-rich" in self.VARS.URN_TYPE:
			self.type = 1
			self.probability = (self.VARS.PRODUCT_COUNT/
				float(self.VARS.TYPES))/float(self.VARS.PRODUCT_COUNT)
			counts = {}
			for i in range(1,self.VARS.TYPES+1):
				self.collection[i] = [Product(i,self.VARS)
					for j in range(self.VARS.PRODUCT_COUNT+1)]
				counts[i] = self.VARS.PRODUCT_COUNT + 1

			self.VARS.PRODUCT_COUNTS[(1,1)] = counts

		elif "fixed-poor" in self.VARS.URN_TYPE:
			self.type = 2
			counts = {}
			for i in range(1,self.VARS.TYPES+1):
				if i ==1:
					self.collection[i] = ([Product(i,self.VARS)
						for j in range(self.VARS.PRODUCT_COUNT+1)])
					counts[1] = self.VARS.PRODUCT_COUNT
				else:
					self.collection[i] = []
					counts[i] = 0
			self.VARS.PRODUCT_COUNTS[(1,1)] = counts

		if self.VARS.HOMOGENEOUS:
			counts = {}
			if "endo-rich" in self.VARS.URN_TYPE:
				self.type = 3
				for i in range(1,self.VARS.TYPES+1):
					self.collection[i] = ([Product(i,self.VARS)
						for j in range(int(self.VARS.PRODUCT_COUNT/float(self.VARS.TYPES)))])
					counts[i] = int(self.VARS.PRODUCT_COUNT/float(self.VARS.TYPES))


			elif  "endo-poor" in self.VARS.URN_TYPE:
				self.type = 4
				self.collection = ({1:[Product(1, self.VARS) 
					for i in range(self.VARS.PRODUCT_COUNT)]})
				counts[i] = int(self.VARS.PRODUCT_COUNT)
				for i in range(self.VARS.TYPES-1):
					self.collection[i+2] = []
					counts[i] = 0
			self.VARS.PRODUCT_COUNTS[(1,1)] = counts
		else:
			holder  = []
			for i in range(1,self.VARS.SPACE_WIDTH+1):
				for j in range(1,self.VARS.SPACE_HEIGHT+1):
					holder.append((i,j))
			hldr = {}
			for point in holder:
				hldr[point] = []

			counts = {}
			if "endo-rich" in self.VARS.URN_TYPE:
				self.type = 5
				for i in range(1,self.VARS.TYPES+1):
					
					for j in range(int(self.VARS.PRODUCT_COUNT/float(self.VARS.TYPES))):
						spot = self.VARS.RNG.choice(holder)
						prod = Product(i,self.VARS)
						prod.set_location(spot)
						self.collection[i].append(prod)
						hldr[spot].append(prod)
						self.VARS.PRODUCT_COUNTS[spot][i] +=1
					

			elif  "endo-poor" in self.VARS.URN_TYPE:
				self.type = 6
				for j in range(int(self.VARS.PRODUCT_COUNT)):
					spot = self.VARS.RNG.choice(holder)
					prod = Product(1,self.VARS)
					prod.set_location(spot)
					self.collection[1] = prod
					hldr[spot].append(prod)
					self.VARS.PRODUCT_COUNTS[spot][j] +=1
				for i in range(2,self.VARS.TYPES+1):
					self.collection[i] = []

			self.VARS.RESOURCE_GRID = hldr



	def __str__(self):
		return str(self.collection)

    
	def request_product(self, desired_output,loc):
		""" The method for cells to request the specific product the activate
		rule calls for. It returns a Product instance of type DESIRED_OUTPUT
		if it is available (i.e. selective search)."""
        
		if not(0 < desired_output <= self.VARS.TYPES):
			raise ValueError("%s is an invalid Product type" %desired_output)

		# Selective search always get exactly what the active rule calls for
		if self.VARS.HOMOGENEOUS:
			if self.VARS.INTEL:
	            
				if self.type == 1: # type = Rich
					return Product(desired_output, self.VARS)

				# if the active rule calls for a 1, hand one over
				elif self.type == 2: # type = Poor
					if desired_output == 1:
						return Product(1, self.VARS)
					else:
						return None

				# This urn started with all products. 
				elif self.type == 3: # type = Endo-Rich
					try:
						self.VARS.PRODUCT_COUNTS[(1,1)][desired_output] -=1
						return self.collection[desired_output].pop()
					except:
						return None

				# Return what is asked for if it is available.      
				elif self.type == 4: #Type = Endo-Poor
					try:
						self.VARS.PRODUCT_COUNTS[(1,1)][desired_output] -=1
						return self.collection[desired_output].pop()
					except:
						return None

			# random search returns the desired product with uniform probability
			else:
	            
				if self.type == 1: #type=rich
					if self.VARS.RNG.random() <= self.probability:

						return Product(desired_output, self.VARS)
					else:
						return None


				# Return a 1-product if it is asked for (there is only 
				# 1-product so random search is still intelligent search.        
				elif self.type == 2: #type=poor
					if desired_output == 1:
						return Product(1, self.VARS)
					else:
						return None
	            

				# If the urn isn't filled, return the desired product with uniform
				# probability. If it is filled, return desired product with a
				# probability proportional to the current distribution of product
				# types.

				elif self.type == 3: #type=Endo-rich
					if desired_output in self.collection.keys():
						count = len(self.collection[desired_output])
						try:
							if self.VARS.RNG.randint(1, self.VARS.PRODUCT_COUNT) <= count:
								self.VARS.PRODUCT_COUNTS[(1,1)][desired_output] -=1
								return self.collection[desired_output].pop()
						except:
							return None
					else:
						return None


				# Returns the desired product with probability proportional to
				# the current distribution of product types. The initial 
				# distribution is all ones.
				elif self.type == 4: #type=Endo-poor
					poss = []
					for i in self.collection.keys():
						for j in range(len(self.collection[i])):
							poss.append(i)
					try:
						if self.VARS.RNG.sample(poss,1)[0] == desired_output:
							self.VARS.PRODUCT_COUNTS[(1,1)][desired_output] -=1
							return self.collection[desired_output].pop()
					except:
						return None
				else:
					raise ValueError("%s is an invalid Urn type" %self.type)
		else:
			if self.VARS.INTEL:
				for prod in self.VARS.RESOURCE_GRID[loc]:
					if prod.type == desired_output:
						self.VARS.PRODUCT_COUNTS[loc][desired_output] -=1
						return self.VARS.RESOURCE_GRID[loc].pop(prod)
				return None
			else:
				here = self.VARS.RESOURCE_GRID[loc]
				if here != []:
					prod = self.VARS.RNG.choice(here)
					if prod.type == desired_output:
						self.VARS.PRODUCT_COUNTS[loc][desired_output] -=1
						self.VARS.RESOURCE_GRID[loc].remove(prod)
						return prod
				return None

    
	def return_product(self, product,loc):
		""" A method for placing transformed Products back into the Urn.
		This only really matters when the Urn is of the endogenous type
		because we need to change the distribution of available Products.
		If the Urn is of type fix, we just 'drop the ball'.
		"""
		if self.type == 3 or self.type == 4:
			product.replenish_energy()
			self.collection[product.get_type()].append(product)
		elif self.type == 5 or self.type == 6:
			product.replenish_energy()

			self.collection[product.get_type()].append(product)
			self.VARS.RESOURCE_GRID[loc].append(product)
			self.VARS.PRODUCT_COUNTS[loc][product.get_type()] +=1




        



    