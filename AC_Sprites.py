import pyglet

class Control_Sprite(pyglet.sprite.Sprite):


	def __init__(self,cell_image,VARS, x, y, scale, name,batch,window):
		self.VARS = VARS
		self.name = name
		pyglet.sprite.Sprite.__init__(self, cell_image, batch=batch)
		self.scale = scale
		self.color = (0,0,0)
		if name == "active":
			self.color = (100,255,90)
			self.opacity = 150
		self.x = x
		self.y = y
		self.radius = self.width/2.
		window.push_handlers(self.on_mouse_press)


	def on_mouse_press(self, x, y, button, modifiers):
		anchor = self.position

		# now we'll get the visual center
		center = (anchor[0] + self.width/2., anchor[1] +self.height/2.)

		# figuring out if the click was within the visual representation 
		# of the cell
		dis = ((x-center[0])**2 + (y-center[1])**2)**.5

		if dis <= self.radius:

			if self.name == "pause":
				self.color = (0,255,00)
				self.VARS.CLOCK.unschedule(self.VARS.SPACE.cell_action)
				self.VARS.ACTION_SCHEDULED = False
				self.VARS.CLOCK.schedule_once(self.color_reset,.5)

			elif self.name == "play": 
				self.color = (0,255,0)
				if not self.VARS.ACTION_SCHEDULED:
					self.VARS.CLOCK.schedule_interval(
						self.VARS.SPACE.cell_action,self.VARS.ACTION_RATE)
					self.VARS.RATE = 1
					self.VARS.ACTION_SCHEDULED = True
					self.VARS.REWOUND = False
				else:
					self.VARS.CLOCK.unschedule(self.VARS.SPACE.cell_action)
					self.VARS.CLOCK.schedule_interval(
						self.VARS.SPACE.cell_action, self.VARS.ACTION_RATE)
					self.VARS.RATE *=2
				self.VARS.CLOCK.schedule_once(self.color_reset,.5)


			elif self.name == "active":
				if self.VARS.ACTIVE:
					self.VARS.ACTIVE = False
					self.color = (255,255,255)
				else:
					self.VARS.ACTIVE = True
					self.color = (100,255,90)
					self.opacity = 150

			elif self.name == "labels":
				if self.VARS.LABELS:
					self.VARS.LABELS = False
					self.color = (0,0,0)
				else:
					self.VARS.COUNTS = False
					self.VARS.LABELS = True
					self.color = (0,255,0)

			elif self.name == "network":
				if self.VARS.LINKS:
					self.VARS.LINKS = False
					self.color = (0,0,0)
				else:
					self.VARS.LINKS = True
					self.color = (0,255,0)

			elif self.name == "backward":
				self.color= (0,255,0)
				if not self.VARS.REWOUND:
					try:
						self.VARS.CLOCK.unschedule(self.VARS.SPACE.cell_action)
						self.VARS.SPACE.load_checkpoint(self.VARS.CHECKPOINT - 1)
						self.VARS.REWOUND = True
					except:
						pass
				else:
					try:
						self.VARS.SPACE.load_checkpoint(self.VARS.CHECKPOINT-2)
					except:
						pass
				self.VARS.CLOCK.schedule_once(self.color_reset,.5)

			elif self.name == "counts":

				if self.VARS.COUNTS:
					self.color = (0,0,0)
					self.VARS.COUNTS = False
				else:
					self.color = (0,255,0)
					self.VARS.COUNTS = True
					self.VARS.LABELS = False
	def color_reset(self,inc):
		self.color = (0,0,0)




class Cell_Sprite(pyglet.sprite.Sprite):

	def __init__(self, cell_image, batch, name,VARS,window):
		pyglet.sprite.Sprite.__init__(self, cell_image, batch=batch)
		self.cell = None
		self.VARS = VARS
		self.name = name
		self.color  = (150,150,150)
		self.radius = self.width/2.
		self.labels = []
		self.tracked = False
		self.id = None

		window.push_handlers(self.on_mouse_press)

	def add_cell(self, cell):
		self.cell = cell
		self.id = self.cell.id

    	def on_mouse_press(self, x, y, button, modifiers):
		""" This allows us to click on the cell and see its contents in a 
		side window. Every cell goes through this when the mouse is 
		clicked so we have to match the cursor to a single cell. We do
		this with a simple distance check."""

		# this is the cell's true position in the window, which is not 
		# the visual center. 
		anchor = self.position

		# now we'll get the visual center
		center = (anchor[0] + self.width/2., anchor[1] +self.height/2.)

		# figuring out if the click was within the visual representation 
		# of the cell
		dis = ((x-center[0])**2 + (y-center[1])**2)**.5
		rad = self.width/2.

		if dis <= rad:
			self.VARS.CLOCK.unschedule(self.VARS.SPACE.clear_data_window)
			self.VARS.CLOCK.schedule_once(self.VARS.SPACE.clear_data_window,10)
			self.VARS.DATA_LABELS = []
			rule_str = []
			total_rules = 0
			for input_key in self.cell.product_rules.keys():
				for output_key in self.cell.product_rules[input_key].keys():
					rls = len(self.cell.product_rules[input_key][output_key])
					total_rules += rls
					rule_str.append(str(input_key) +"->" + str(output_key)+ ": " + str(rls) + ", ")

			

			hld = ""
			for i in self.cell.products.keys():
				cnt = len(self.cell.products[i])
				if cnt != 0:
					hld += (str(i) + ": " + str(cnt) + "  ")
			if hld != "":
				string = ("Cell " + str(self.name) + " has " +
					str(total_rules) + " rules: " + "".join(rule_str)
					+ "| Storage: " +hld)
			else:
				string = ("Cell " + str(self.name) + " has " +
					str(total_rules) + " rules: " + "".join(rule_str))

			self.VARS.DATA_LABELS.append(pyglet.text.Label(string,
				x=200, y=20,color=(0,0,0,255),width=325,
				multiline=True, font_size=12))
			if not self.tracked:
				for sprite in self.VARS.SPRITES:
					sprite.tracked = False
					sprite.color = (255,255,255)
				self.tracked = True
				self.color = (100,100,255)
			else:
				self.color = (255,255,255)
				self.tracked = False
 
    