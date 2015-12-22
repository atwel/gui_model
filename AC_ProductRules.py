""" This module contains the constructor for Product rules, the skills that
cells possess for converting one Product type into another. It also contains
the constructor for a NetRule, a class of objects used to help keep track of
autocatalytic cycles. Finally, it has an algorithm for constructing the rule
sets that define the relevant "chemistries."

Written by Jon Atwell
"""

class ProductRule:
	""" The rule that defines a 'skill' a cell might possess. It can be used
	to transform the type of a Product instance from type INPUT to 
	type OUTPUT.
	"""

	def __init__(self, input_, output):
		self.input = input_
		self.output = output

	def __str__(self):
		return "Rule has input %d and output %d" %(self.input, self.output)

	def get_input(self):
		return self.input

	def get_output(self):
		return self.output

	def get_name(self):
		""" Used as the key for the related ProductNetRules."""
		return "-".join([str(self.input), str(self.output)])

        
    
        
class ProductNetRule:
	""" A class of object closely related to ProductRule but used to count 
	autocatalytic cycles. A cell will create a ProductNetRule for every type
	of ProductRule (i.e. unique input and output combination) they have.
	The ProductNetRule keeps track of how many actual ProductRules are of
	that type."""

	def __init__(self, input_, output, count):
		self.input = input_
		self.output = output
		self.count = count
		self.owner = None
		self.location = None
	
	def __str__(self):
		return "%d-%d" %(self.input, self.output)

	def set_location(self, location):
		self.location = location

	def set_owner(self,cell):
		self.owner = cell

	def get_owner(self):
		return self.owner

	def add_to_count(self):
		self.count += 1

	def subtract_from_count(self):
		self.count -= 1

	def get_input(self):
		return self.input

	def get_output(self):
		return self.output

	def get_count(self):
		return self.count


def create_RuleSet(VARS):
	""" A function for creating a collection of ProductRules that define a
	"chemistry." A chemistry is defined by the number of possible products
	(maxProductType) and whether there is a unique progression of
	transformation required (1->2, 2->3,...n->1). The TYPE 'SOLOH'
	is for the unique progression variant. The function creates as uniform of
	a distribution as possible for the specified rule types.
	"""

	myset = []

	if VARS.CHEM == "ALL":
		print "making ALL chem"
		combos = VARS.TYPES**2 - VARS.TYPES
		count_each = 200/combos
		extras = 200-(combos*count_each)
		exs = []
		cnt = 0
		types = []
		for i in range(VARS.TYPES):
			for j in range(VARS.TYPES):
				if i < j:
					exs.append(ProductRule(i+1,j+1))
					for k in range(count_each):
						myset.append(ProductRule(i+1, j+1))
					types.append((i+1,j+1))
		for j in range(VARS.TYPES):
			for i in range(VARS.TYPES):
				if i > j:
					exs.append(ProductRule(i+1,j+1))
					for k in range(count_each):
						myset.append(ProductRule(i+1, j+1))
					types.append((i+1,j+1))

		colors = VARS.COLORS
		holder = {}
		for i in types:
			holder[i] = colors.pop(0)
		VARS.COLORS = holder

		#randomly adding instances to get to 200.
		myset.extend(VARS.RNG.sample(exs, extras))
		return myset


	elif VARS.CHEM == "SOLOH":
		types = []
		count_each = 200/VARS.TYPES
		extras = 200-(VARS.TYPES*count_each)
		exs = []
		print "making SOLOH chemistry"
		count = 0
		for i in range(1,VARS.TYPES):
			for j in range(count_each):

				myset.append(ProductRule(i,i+1))
				exs.append(ProductRule(i,i+1))
			types.append((i,i+1))
		for i in range(count_each):
			myset.append(ProductRule(VARS.TYPES,1))
			exs.append(ProductRule(VARS.TYPES,1))
		types.append((VAR.TYPES,1))

		colors = VARS.COLORS
		holder = {}
		for i in types:
			holder[i] = colors.pop(0)
		VARS.COLORS = holder

		#randomly adding instances to get to 200.
		myset.extend(VARS.RNG.sample(exs, extras))

		return myset
       



        