""" This module implements the core logic of action in Padgett and Powell's
model of autocatalysis and hypercycles. Other modules are required for the
model to work, but the Cells and their behaviors are implemented here.


Written by Jon Atwell
"""


import AC_ProductRules
import AC_Products
import collections
import json
import math


class Cell:

	def __init__(self, id, Sprite, VARS):
		""" The contents of the cell. Most things just track what is 
		going on with the cell and the global parameters. 
		"""
		
		self.id = id
		self.Sprite = Sprite
		self.VARS = VARS

		self.isAlive = True
		self.location = (-1,-1)
		self.neighbors = []
		self.product_rules = collections.defaultdict(lambda: collections.defaultdict(list))
		self.product_netrules = collections.defaultdict(list)
		self.products = collections.defaultdict(list)
		self.ordered_products = []
		self.count_rules = 0
		self.active_rule = None
		

	def __str__(self):
		""" Print checks for the version of the 
		model with cell movement.
		"""
		return "cell with %d rules" % self.count_rules


	def clear_cell(self):
		self.product_rules = collections.defaultdict(lambda: collections.defaultdict(list))
		self.product_netrules = collections.defaultdict(list)
		self.products = collections.defaultdict(list)


	def update_labels(self):
		labels = []

		for input_key in self.product_rules.keys():
			for output_key in self.product_rules[input_key].keys():
				rule = str(input_key) +"->" + str(output_key)
				labels.append(rule)
		self.Sprite.label = " ".join(labels)[:19]


	def set_location(self, x, y):
		""" The method for setting the location of the cell in the 
		space. It's used in the static grid setup (no movement) 
		because freshly created cells do not have a location.
		"""

		self.location = (x,y)
		self.Sprite.x = (x-1) * self.VARS.X_SCALING + self.VARS.BORDER*.25
		self.Sprite.y = (y-1) * self.VARS.Y_SCALING + self.VARS.BORDER*1.15


	def get_location(self):
		""" The method for querying a cell's location.
		"""
		return self.location


	def add_Product(self, product, reload_=False):
		"""This method allows the cell to put a product in a 
		stack so that it can be used later.
		"""

		self.products[product.get_type()].append(product)
		self.ordered_products.append(product.get_type())

		if len(self.ordered_products) > 1:
			prod = self.remove_Product(self.ordered_products.pop(0))
			self.VARS.URN.return_product(prod,self.location)


	def remove_Product(self, product_type):
		""" This method allows the cell pull out a product of 
		the requested type.
		"""
		try:
			return self.products[product_type].pop()
		except:
			return None


	def has_Product(self):
		""" A method to get a product type from the cell's storage. 
		We need to check that there is still a compatible rule for any
		product because there is a very good chance the rule was 
		deleted since the product was received. If there are any 
		products and rules that can use them, one is grabbed uniform
		at random and the type of the product is returned. The product
		itself will not be returned because it is picked up later.
		""" 
		
		has = []
		for content in self.products.keys():
			if content in self.product_rules.keys():
				has.extend(self.products[content])
			else:
				self.products[content] = []
		try:
			return self.VARS.RNG.choice(has).get_type()
		except:
			return None


	def has_rule(self, product):
		""" This method just checks to see if this cell has a rule
		that is compatible with the product it just received. It 
		allows the explicit argument to be the product itself or
		just the integer that identifies its type.
		"""

		if type(product) == int:
			if product in self.product_rules.keys(): 
				return True
			else:
				return False
		else:
			if product.get_type() in self.product_rules.keys(): 
				return True
			else:
				return False


	def add_ProductRule(self, aProductRule):
		""" The method for adding a product rule to the
		collection the cell currently owns.
		"""

		in_put = aProductRule.get_input()
		output = aProductRule.get_output()

		self.product_rules[in_put][output].append(aProductRule)

		self.count_rules +=1
		self.VARS.SPACE.add_rule((in_put, output))
		self.add_ProductNetRule(aProductRule)




	def remove_ProductRule(self, a_ProductRule):
		""" The method used to remove a product rule 
		from the Cell's collection.
		"""

		# Figuring out what type of rule it is
		in_put = a_ProductRule.get_input()
		output = a_ProductRule.get_output()

		# This pulls the actual instance out of the cell's collection
		self.product_rules[in_put][output].remove(a_ProductRule)

		# This count just saves us from having to count the collection
		self.count_rules -= 1
		name = "-".join([str(in_put), str(output)])
		self.VARS.SPACE.remove_rule((in_put,output))


		# Doing some clean up: If that was the last of that type of rule...
		if self.product_rules[in_put][output] == []:
			netrule = self.product_netrules[name]
			self.VARS.PRODUCT_RULE_NET.remove_ProductNetRule(netrule,
				self.VARS.MASTER_COUNT)

			# We also remove that key from the outer dictionary
			# in the rules collection. pop() on a dict removes the key.
			del self.product_rules[in_put][output]
			if (self.active_rule != None) and (in_put, output) == (self.active_rule.get_input(),
				self.active_rule.get_output()):
				self.active_rule=None

			# If the outer dict. is also empty, we remove it as well.
			if self.product_rules[in_put] == {}:
				del self.product_rules[in_put]

			if self.count_rules <=0:
				self.ordered_products = []
				for vals in self.products.values():
					for pro in vals:
						self.VARS.URN.return_product(pro,self.location)
				self.isAlive = False


	def add_ProductNetRule(self, a_ProductRule):
		""" The method to add a NetRule to the productRule_Net. The
		bulk of the work of adding a new rule happens in the 
		add_ProductNetRule() method of the productRule_Net class.
		"""
		try:
			self.product_netrules[a_ProductRule.get_name()].add_to_count()
		except:
			# If there isn't a netrule yet, we need to create one.
			# This code is only run during model initialization.
			new = AC_ProductRules.ProductNetRule(\
			a_ProductRule.get_input(), a_ProductRule.get_output(), 1)

			# we set its owner to this cell.
			new.set_owner(self)

			# we add the netrule to the cell's collection.
			self.product_netrules[a_ProductRule.get_name()] = new

			#We also add it to the product rule net.
			self.VARS.PRODUCT_RULE_NET.add_ProductNetRule(new)



	def set_active_rule(self, rule):
		""" A simple method to set the currently active rule in the cell.
		"""

		if rule in self.product_rules[rule.get_input()][rule.get_output()]:
			self.active_rule = rule
		else:
			raise InstanceError("This rule doesn't belong to this cell")


	def reproduce_active_rule(self):
		""" This takes the rule the cell just used and reproduces it.
		"""
		r = self.active_rule
		if self.VARS.SIMPLE:
			dead = self.VARS.SPACE.get_random_cell()
			dead.clear_cell()
			dead.add_ProductRule((AC_ProductRules.ProductRule(r.get_input(),
				r.get_output())))
			x,y = self.get_location()
			self.VARS.SPACE.transport_cell(dead,self.get_location())


		else:
			self.add_ProductRule((AC_ProductRules.ProductRule(r.get_input(),
				r.get_output())))

			self.VARS.SPACE.remove_random_rule()

    
	def chain_step(self, debug):
		""" This method is used to start up a passing chain. An agent is
		selected at random. It is then asked to select a random rule using
		the get_random_rule() method. It then (tries to) selects an input
		according to the INTELLIGENCE parameter. If it finds a usable
		input in the urn, it transforms it and passes it onto a neighbor.
		"""
		self.VARS.MASTER_COUNT +=1

		if  self.VARS.MASTER_COUNT % 10000 == 0:
			print "steps: ", self.VARS.MASTER_COUNT
			self.save_checkpoint()

		# now we have a rule and we need to try to get a product it can use
		product = self.remove_Product(self.active_rule.get_input())
		if product != None:
			self.ordered_products.remove(product.get_type())
		else:
			product = self.VARS.URN.request_product(
				self.active_rule.get_input(),self.location)

		if product != None:
            
			# Start Block 1
			transform, pass_,repro = self.VARS.ENERGY_COSTS.values()
			if product.get_energy() >= transform:
				product.apply_ProductRule(self.active_rule, transform)

				# start block 2
				
				if product.get_energy() >= pass_:
					product.use_energy(pass_)

					if self.VARS.TOPO == "spatial":
						random_neighbor = self.get_neighbor()
					else:
						random_neighbor = self.VARS.SPACE.get_random_cell()

					if random_neighbor != None:
						random_neighbor.receive_product(self,
							product, product.get_type())
					else:
						
						self.VARS.URN.return_product(product, self.location)
				else:
					
					self.VARS.URN.return_product(product,self.location)
					# End Block 2
			else:	
				self.VARS.URN.return_product(product,self.location)

				# End block 1

    
    
	def receive_product(self, sender, product, prohibited_return_output,
		who=None, debug=False):
		""" This method takes in a product and checks to see if the
		cell can transform it. If it can, it does. If not, it's passed 
		back to the urn.
		"""
		self.VARS.MASTER_COUNT +=1
		self.VARS.ACTIVEB = self.id
		if  self.VARS.MASTER_COUNT% 10000 == 0:
			print "steps: ", self.VARS.MASTER_COUNT
			self.save_checkpoint()

		start = product.get_type()
		if self.has_rule(start) and product.get_energy() > 0:

			# picking the rule that will transform the product
			self.active_rule = self.get_random_rule_of_type(start)

			# Transformation and passing happen later
			cost = self.VARS.ENERGY_COSTS["reproduce"]
			if product.get_energy() >= cost:
				product.use_energy(cost)
				if self.VARS.REPRO == "target":
					self.reproduce_active_rule()
				elif self.VARS.REPRO == "source":
					sender.reproduce_active_rule()

				self.add_Product(product)
			else:
				self.VARS.URN.return_product(product,self.location)

		else:
			# Passing the unusable product back into the environment (the urn)
			self.VARS.URN.return_product(product,self.location)
		


	def get_random_rule(self):
		""" An important method: Sometimes a cell loses a rule
		because someone else created a new rule. We want to
		remove the actual rule uniform at random. This means
		that it is effectively weighted by netrule type because
		there can be more than one instance of an actual rule 
		of each net rule type.
		"""   
		candidates = []

		for input_ in self.product_rules.keys():
			for output in self.product_rules[input_].keys():
				candidates.extend(self.product_rules[input_][output])

		return self.VARS.RNG.choice(candidates)

    
	def get_random_rule_of_type(self,type_):
		""" An important method: When a cell is capable of using
		an input it has received, the rule it ultimately uses is 
		selected uniform-at-random from among all of the rules 
		that can possibly use it. This means that it is effectively 
		weighted by netrule type because there can be more 
		than one instance of an actual rule of each net rule type.
		""" 
		candidates = []

		for output in self.product_rules[type_].keys():
			candidates.extend(self.product_rules[type_][output])

		return self.VARS.RNG.choice(candidates)


	def get_neighbor(self):
		if self.VARS.MOBILE:
			try:
				return self.VARS.RNG.choice(self.neighbors)
			except:
				return None
		else:
			a = [i for i in self.neighbors if i.isAlive]
			b = [None for i in range(8-len(a))]

			return self.VARS.RNG.choice(a+b)

	def save_contents(self):
		""" This takes the cell's state and packages it in a JSON 
		friendly format so that we can pickle the whole simulation.
		"""
		rules = {}
		for in_ in self.product_rules.keys():
			for out, list_of in self.product_rules[in_].items():
				rules[str(in_)+str(out)] = len(list_of)

		prods = {}
		for prod_type in self.products.keys():
			if self.products[prod_type]!=[]:
				prods[prod_type]=[]
				for prod in self.products[prod_type]:
					prods[prod_type].append(prod.get_energy())

		if self.active_rule != None:
			active = (self.active_rule.get_input(),
				self.active_rule.get_output())
		else:
			active = []
		
		self.neighbors.sort()
		neighbs = [i.id for i in self.neighbors]

		other = ({"x":self.location[0], "y":self.location[1],
			"ord_prod":self.ordered_products, "neighbors":neighbs,
			"active_rule":active, "isAlive":self.isAlive})

		return {"rules":rules,"products":prods, "other":other}


	def reload_data(self, data):
		self.products=collections.defaultdict(list)
		self.product_rules = collections.defaultdict(lambda: collections.defaultdict(list))
		self.product_netrules = collections.defaultdict(list)
		self.ordered_products = []
		self.count_rules = 0
		self.active_rule = None
		
		for prod_type, nrgs in data["products"].items():
			for nrg in nrgs:
				self.add_Product(AC_Products.Product(int(prod_type),
					self.VARS.URN,energy=int(nrg)))


		for rule, count in data["rules"].items():
			in_ = int(rule[0])
			out = int(rule[1])
			for i in range(count):
				rul = AC_ProductRules.ProductRule(in_,out)
				self.add_ProductRule(rul)
				self.add_ProductNetRule(rul)

		self.ordered_products = data["other"]["ord_prod"]

		neighs=[]
		n_data=data["other"]["neighbors"]
		for cell in self.VARS.CELLS:
			if cell.id in n_data:
				neighs.append(cell)
		self.neighbors=sorted(neighs)

		x = data["other"]["x"]
		y = data["other"]["y"]
		self.set_location(x,y)

		try:
			self.VARS.SPACE.neighbor_grid[y-1][x-1].append(self)
		except:
			self.VARS.SPACE.neighbor_grid[y-1][x-1] = [self]

		a_rul = data["other"]["active_rule"]
		if a_rul != []:
			self.active_rule = self.product_rules[a_rul[0]][a_rul[1]][0]

		self.isAlive=data["other"]["isAlive"]

		self.update_labels()

	def save_checkpoint(self):
		"""We'll use this function is output all of the state contigent
		data into a json file so that we can load it back in later.
		First, we package up the cell states. Second, we package 
		up the urn. Third, we save the states of the random
		number generators.
		"""
		out_name = str(self.VARS.CHECKPOINT)

		big_dict = {}
		cells_save = {}
		for cell in self.VARS.CELLS:
			cells_save[cell.id] = cell.save_contents()
		big_dict["cells"] = cells_save

		the_rest = {}
		the_rest["step_count"] = self.VARS.MASTER_COUNT

		urn = {}
		for key, values in self.VARS.URN.collection.items():
			urn[key] = len(values)
		the_rest["urn"] = urn

		the_rest["rng_state"] = self.VARS.RNG.getstate()
		the_rest["checkpoint"] = self.VARS.CHECKPOINT

		big_dict["the_rest"] = the_rest

		out = open(out_name +".json","w")
		json.dump(big_dict,out,indent=4,encoding="ascii")
		out.close()

		self.VARS.CHECKPOINT +=1
