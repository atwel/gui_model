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

    def __init__(self, urn, productRule_Net, RNG, id, Sprite, screen_dimensions, space_dimensions, border_size,
                    selective_intelligence=False, reproduction_type="source",
                    topology="spatial", radius=3,LABELS=True,mobile=True):
        """ The contents of the cell. Most things just track what is going
        on with the cell and the global parameters. 
        """

        self.isAlive = True
        self.scaling_x = (screen_dimensions[0]-border_size*2)/float(space_dimensions[0])
        self.scaling_y = (screen_dimensions[1]-border_size*2)/float(space_dimensions[1])
        self.border_size = border_size
        self.Sprite = Sprite
        self.location = (-1,-1)
        self.neighbors = []            # added after locations are assigned
        self.product_rules = collections.defaultdict(lambda: collections.defaultdict(list))
        self.product_netrules = collections.defaultdict(list)
        self.products = collections.defaultdict(list)
        self.ordered_products = []
        self.count_rules = 0
        self.active_rule = None      # rule used in case it's to be reproduced
        self.id = id
        self.RNG = RNG              # so we can easily reproduce runs.
        self.repro_type= reproduction_type          # key parameter
        self.intel = selective_intelligence              # key parameter
        self.topology = topology                        # key parameter
        self.radius = radius
        self.urn = urn                                         # key parameter
        self.productRule_Net = productRule_Net
        self.myspace = None         # we'll add this once the cells are made.
        self.LABELS = LABELS
        self.mobile = mobile
        self.tracked = False



    def __str__(self):
        """ Print checks for the version of the model with cell movement.
        """

        return "cell with " + str(self.count_rules) + " rules"

    def update_labels(self):
	labels = []

	for input_key in self.product_rules.keys():
		for output_key in self.product_rules[input_key].keys():
			rule = str(input_key) +"->" + str(output_key)
			labels.append(rule)
	self.Sprite.label = " ".join(labels)[:19]
	if not self.tracked:
		self.Sprite.color = (0,255-155*math.log(1 + 1.71*self.count_rules/200.),250)

    def set_location(self, x, y):
        """ The method for setting the location of the cell in the space. It's
        used in the static grid setup (no movement) because freshly
        created cells do not have a location.
        """
        
        self.location = (x,y)
        self.Sprite.x = (x-1) * self.scaling_x + self.border_size
        self.Sprite.y = (y-1) * self.scaling_y + self.border_size
        
        #int(self.count_rules*255/200.)

    def get_location(self):
        """ The method for querying a cell's location.
        """
        
        return self.location


    def add_Space(self, space):
        """ This method allows us to provide a handle for the cellNet to
        the cell. It can't be done upon initialization because we make the
        cellNet after we make the cells.
        """

        self.myspace = space

    def add_Product(self, product, reload_=False):
        """This method allows the cell to put a product in a stack so that it
        can be used later.
        """

        self.products[product.get_type()].append(product)
        self.ordered_products.append(product.get_type())

        if len(self.ordered_products) > 1:
            if reload_:
                print "dumping "
                print self.ordered_products
            prod = self.remove_Product(self.ordered_products.pop(0))
            if prod != None:
                self.urn.return_product(prod)


    def remove_Product(self, product_type):
        """ This method allows the cell pull out a product of the requested
        type.
        """
        try:
            return self.products[product_type].pop()
        except:
            return None



    def has_Product(self):
        """ A method to get a product type from the cell's storage. We need
        to check that there is still a compatible rule for any product because
        there is a very good chance the rule was deleted since the product was
        received. If there are any products and rules that can use them, one 
        is grabbed uniform at random and the type of the product is returned. 
        The product itself will not be returned because it is picked up later.

        """ 
        has = []
        for content in self.products.keys():
            if content in self.product_rules.keys():
                has.extend(self.products[content])
            else:
                self.products[content] = []
        try:
            return self.RNG.choice(has).get_type()
        except:
            return None


    def has_rule(self, product):
        """ This method just checks to see if this cell has a rule that is
        compatible with the product it just received. It allows the explicit
        argument to be the product itself or just the integer that identifies
        its type.
        """

        if type(product) == int:
            if product in self.product_rules.keys(): 
                #indexError if no rules for that type
                return True
            else:
                return False
        else:
            if product.get_type() in self.product_rules.keys(): 
                #indexError if no rules for that type
                return True
            else:
                return False


    def add_ProductRule(self, aProductRule):
        """ The method for adding a product rule to the collection the cell
        currently owns.
        """
        
        # making sure nothing inappropriate sneaks in.
        if isinstance(aProductRule, AC_ProductRules.ProductRule):

            # Because we're using dictionaries to hold everything,
            # a nested set of try/except expressions  is used to set the
            # dictionaries up correctly. Possibly rewrite using Collections
            # module dictionaries.

            in_put = aProductRule.get_input()
            output = aProductRule.get_output()
            # try:
            self.product_rules[in_put][output].append(aProductRule)
            #except:
            #    try:
            #        self.product_rules[in_put][output] = [aProductRule]
            #    except:
            #        self.product_rules[in_put] = {}
            #        self.product_rules[in_put][output] = [aProductRule]

            self.count_rules +=1
            self.myspace.add_rule("-".join([str(in_put), str(output)]))
            self.add_ProductNetRule(aProductRule)
        else:
            raise TypeError("Argument is not of type AC_Products.ProductRule")

            

    def remove_ProductRule(self, a_ProductRule):
	""" The method used to remove a product rule from the Cell's
	collection.
	"""

	# Figuring out what type of rule it is
	in_put = a_ProductRule.get_input()
	output = a_ProductRule.get_output()

	# This pulls the actual instance out of the cell's collection
	self.product_rules[in_put][output].remove(a_ProductRule)
	#print "%d: cell %d removed rule of type %d -> %d" %(self.myspace.master_count, self.id, in_put, output)
	# This count just saves us from having to count the collection
	self.count_rules -= 1
	self.myspace.remove_rule("-".join([str(in_put), str(output)]))


	# Doing some clean up: If that was the last of that type of rule...
	if self.product_rules[in_put][output] == []:
		netrule = self.product_netrules["-".join([str(in_put), str(output)])]
		self.productRule_Net.remove_ProductNetRule(netrule, self.myspace.master_count)

		# We also remove that key from the outer dictionary
		# in the rules collection. pop() on a dict removes the key.
		del self.product_rules[in_put][output]
		if self.active_rule != None:
			active = (self.active_rule.get_input(), self.active_rule.get_output())
			if active == (in_put, output):
				self.active_rule=None

		# If the outer dict. is also empty, we remove it as well.
		if self.product_rules[in_put] == {}:
			del self.product_rules[in_put]

		if self.count_rules <=0:
			self.ordered_products = []
			for vals in self.products.values():
				for pro in vals:
					self.urn.return_product(pro)
			self.isAlive = False


    def add_ProductNetRule(self, a_ProductRule):
        """ The method to add a NetRule to the productRule_Net. The bulk of
        the work of adding a new rule happens in the add_ProductNetRule()
        method of the productRule_Net class.
        """

        # A check to make sure nothing that shouldn't be in here slips in.
        if isinstance(a_ProductRule, AC_ProductRules.ProductRule):
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
                self.productRule_Net.add_ProductNetRule(new)
        
        else:
            raise TypeError("Argument is not of type AC_Products.ProductRule")
            
            
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

        self.add_ProductRule((AC_ProductRules.ProductRule(r.get_input(),
            r.get_output())))

        #self.myspace.last_added_rule = self.myspace.master_count

        # This is just part of the deal.
        #print "%d: random rule removal... " %(self.myspace.master_count)
        self.myspace.remove_random_rule()
        #self.active_rule = None

    
    def chain_step(self, debug):
        """ This method is used to start up a passing chain. An agent is
        selected at random. It is then asked to select a random rule using
        the get_random_rule() method. It then (tries to) selects an input
        according to the INTELLIGENCE parameter. If it finds a usable
        input in the urn, it transforms it and passes it onto a neighbor.
        """
        self.myspace.master_count +=1
       
        if  self.myspace.master_count % 10000 == 0:
            print "steps: ", self.myspace.master_count
            self.save_checkpoint()
        
        # now we have a rule and we need to try to get a product it can use
        product = self.remove_Product(self.active_rule.get_input())
        if product != None:
            #print "%d: cell %d got product type %d from itself" %(self.myspace.master_count, self.id, product.get_type())
            self.ordered_products.remove(product.get_type())
        else:
            product = self.urn.request_product(self.active_rule.get_input(), 
                self.intel)
            #try:
                #print "%d: cell %d got product type %d from urn" %(self.myspace.master_count, self.id, product.get_type())
            #except:
                #print "%d: cell %d failed to get a product" %(self.myspace.master_count, self.id)
        if product != None:
            #actually changing the product
            
             # Start Block 1
            cost = self.myspace.energy_costs["transform"]
            if product.get_energy() >= cost:
                product.apply_ProductRule(self.active_rule, cost)

                # start block 2
                cost = self.myspace.energy_costs["pass"]
                if product.get_energy() >= cost:
                    product.use_energy(cost)
                    #self.Sprite.active = True
                    if self.topology == "spatial":
                        # passes to a neighbor in von Neuman neighborhood.
                        random_neighbor = self.get_neighbor()
                        
                    else:
                        random_neighbor = self.myspace.get_random_cell()
                    if random_neighbor != None:
                        #print "%d: cell %d got random neighbor %d" %(self.myspace.master_count, self.id,random_neighbor.id)
                        #print "(active rule is %d -> %d)" %(self.active_rule.get_input(), self.active_rule.get_output())

                        random_neighbor.receive_product(self,  
                            product, product.get_type())
                    else:
                        self.urn.return_product(product)
                        #print "%d: cell %d failed to get a neighbor and returned a product to the urn" %(self.myspace.master_count, self.id)
                        #self.add_Product(product)
                else:
                    self.urn.return_product(product)
                    #print "%d: cell %d returned a product to the urn" %(self.myspace.master_count, self.id)
                    # End Block 2
            else:
                self.urn.return_product(product)
                #print "%d: cell %d returned a product to the urn" %(self.myspace.master_count, self.id)
                # End block 1

        else:
            if debug:
                print "%s didn't get the right product, %d" %(str(
                    self.get_location()), self.active_rule.get_input()) 
    
    
    def receive_product(self, sender, product, prohibited_return_output,
        who=None, debug=False):
        """ This method takes in a product and checks to see if the cell can
        transform it. If it can, it does. If not, it's passed back to the urn.
        """
        self.myspace.master_count +=1
       
        if  self.myspace.master_count % 10000 == 0:
            print "steps: ", self.myspace.master_count
            self.save_checkpoint()

        start = product.get_type()
        #####
        if self.has_rule(start) and product.get_energy() > 0:

            # picking the rule that will transform the product
            #print "%d: cell %d has rule for product type %d" %(self.myspace.master_count, self.id, start)
            self.active_rule = self.get_random_rule_of_type(start)
            #print "%d: cell %d has active rule of type %d -> %d" %(self.myspace.master_count, self.id, self.active_rule.get_input(), self.active_rule.get_output())
           
            # Transformation and passing happen later
            cost = self.myspace.energy_costs["reproduce"]
            if product.get_energy() >= cost:
                product.use_energy(cost)
                self.Sprite.active = True
                if self.repro_type == "target":
                    self.reproduce_active_rule()
                    #print "%d: cell %d reproduced active rule" %(self.myspace.master_count, self.id)

                elif self.repro_type == "source":
                    #print "%d: cell %d will reproduce active rule %d -> %d" %(self.myspace.master_count, sender.id, sender.active_rule.get_input(), sender.active_rule.get_output())
                    sender.reproduce_active_rule()

                self.add_Product(product)
                #self.Sprite.active = False
            else:
                self.urn.return_product(product)
                #print "%d: cell %d returned a product of type " %(self.myspace.master_count, self.id, product.get_type())

        else:
            if debug:
                mystr = " ".join([str(i) for i in\
                    self.product_netrules.keys()])
                print "%s passed a %d to %s but nothing could be done;%s" %(
                    str(who), product.get_type(),str(self.get_location()), 
                    mystr)
            
            # Passing the unusable product back into the environment (the urn)
            self.urn.return_product(product)
            #print "%d: cell %d returned a product of type %d " %(self.myspace.master_count, self.id, product.get_type())

        #sender.Sprite.active = False


            
    def get_random_rule(self):
        """ An important method: Sometimes a cell loses a rule because someone
        else created a new rule. We want to remove the actual rule uniform at
        random. This means that it is effectively weighted by netrule type 
        because there can be more than one instance of an actual rule of each
        net rule type.
        """   
        candidates = []

        for input_ in self.product_rules.keys():
            for output in self.product_rules[input_].keys():
                for rule in self.product_rules[input_][output]:
                    candidates.append(rule)

        return self.RNG.choice(candidates)

    
    def get_random_rule_of_type(self,type):
        """ An important method: When a cell is capable of using an input it
        has received, the rule it ultimately uses is selected uniform-at-
        random from among all of the rules that can possibly use it. This 
        means that it is effectively weighted by netrule type because there 
        can be more than one instance of an actual rule of each net rule type.
        """ 

        candidates = []

        for output in self.product_rules[type].keys():
            for rule in self.product_rules[type][output]:
                    candidates.append(rule)

        return self.RNG.choice(candidates)

    def get_neighbor(self):
        if self.mobile:
            try:
                return self.RNG.choice(self.neighbors)
            except:
                return None
        else:
            a = [i for i in self.neighbors if i.isAlive]
            b = [None for i in range(8-len(a))]
    
            return self.RNG.choice(a+b)

    def save_contents(self):
        json_rules = {}
        for in_ in self.product_rules.keys():
            for out, list_of in self.product_rules[in_].items():
                count = len(list_of)
                json_rules[str(in_)+str(out)] = count

        json_products = {}
        for prod_type in self.products.keys():
            if self.products[prod_type]!=[]:
                json_products[prod_type]=[]
                for prod in self.products[prod_type]:
                    json_products[prod_type].append(prod.get_energy())

       
        if self.active_rule != None:
            active = (self.active_rule.get_input(),self.active_rule.get_output())
        else:
            active = []
        self.neighbors.sort()
        neighbs = [i.id for i in self.neighbors]
        #neighbs.sort()
        json_other = {"x":self.location[0], "y":self.location[1], "ord_prod":self.ordered_products, "neighbors":neighbs, "active_rule":active, "isAlive":self.isAlive}

        return {"rules":json_rules,"products":json_products, "other":json_other}

    
    def reload_data(self, data, cells):
        self.products=collections.defaultdict(list)
        self.product_rules = collections.defaultdict(lambda: collections.defaultdict(list))
        self.product_netrules = collections.defaultdict(list)
        self.ordered_products = []
        self.count_rules = 0
        self.active_rule = None
        for prod_type, nrgs in data["products"].items():
            for nrg in nrgs:
                self.add_Product(AC_Products.Product(self.urn, int(prod_type),int(nrg)))


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
        for cell in cells:
            if cell.id in n_data:
                neighs.append(cell)
        self.neighbors=sorted(neighs)
        x = data["other"]["x"]
        y = data["other"]["y"]
        self.set_location(x,y)
        #print self.id, " is at ", self.get_location()
        try:
            self.myspace.neighbor_grid[y-1][x-1].append(self)
        except:
            self.myspace.neighbor_grid[y-1][x-1] = [self]

        a_rul = data["other"]["active_rule"]
        if a_rul != []:
            self.active_rule = self.product_rules[a_rul[0]][a_rul[1]][0]
            #print self.id, self.active_rule.get_output(), self.active_rule.get_input()
        else:
            pass

        self.isAlive=data["other"]["isAlive"]

        self.update_labels()

    def save_checkpoint(self):
        """We'll use this function is output all of the state contigent data into a json file
        so that we can load it back in later.
        First, we package up the cell states
        Second, we package up the urn.
        Third, we save the states of the random number generators
        """
        cells = self.myspace.cells
        out_name = str(self.myspace.checkpoint)
        
        big_dict = {}
        cells_save = {}
        for cell in cells:
            cells_save[cell.id] = cell.save_contents()
        big_dict["cells"] = cells_save

        the_rest = {}
        the_rest["step_count"] = self.myspace.master_count

        urn = {}
        for key, values in self.urn.collection.items():
            urn[key] = len(values)

        the_rest["urn"] = urn
        the_rest["rng_state"] = self.RNG.getstate()
        the_rest["checkpoint"] = self.myspace.checkpoint

        big_dict["the_rest"] = the_rest

        out = open(out_name +".json","w")
        json.dump(big_dict,out,indent=4,encoding="ascii")
        out.close()

        self.myspace.checkpoint +=1
