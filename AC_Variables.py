
import sys
import random
import math
import pyglet
import collections

class VARS:

	def __init__(self):

		#  INDEPENDENT VARIABLES
		# Set on start up
		self.URN_TYPE = None
		self.REPRO = None
		self.SIMPLE = None
		self.CHEM = None
		self.TYPES = None
		self.STEPS = None
		self.CELL_COUNT = None
		self.RULE_COUNT = None
		self.TOPO = None
		self.MOBILE = None
		self.HOMOGENEOUS = False
		self.FRACT_HEADLESS = None
		self.NON_VIZ_STEPS = None
		self.RNG_SEED = random.randint(0,sys.maxint)
		self.RNG = random.Random(self.RNG_SEED)
		self.SCREEN_WIDTH = None
		self.SCREEN_HEIGHT = None
		self.MAIN_WINDOW_HEIGHT= None
		self.MAIN_WINDOW_WIDTH = None
		self.RULE_WINDOW_HEIGHT = None
		self.RULE_WINDOW_WIDTH = None
		self.PRODUCT_WINDOW_HEIGHT = None
		self.PRODUCT_WINDOW_WIDTH = None
		self.SPACE_WIDTH = None
		self.SPACE_HEIGHT = None
		self.BORDER = None
		self.X_SCALING = None
		self.Y_SCALING = None
		self.VERTS = None
		self.LABEL_VERTS = None
		self.LINK_VERTS = None
		self.COLORS = None
		self.GRID_LINES = None
		self.PRODUCT_ANCHORS = None
		self.PRODUCT_COUNTS = collections.defaultdict(lambda: collections.defaultdict(int))
		self.X_INC = None
		self.Y_INC = None
		self.PRODUCT_COLORS = ({1:(0,0,255),2:(0,200,255),
			3:(0,250,0),4:(200,50,0),5:(0,255,100),6:(250,0,250),
			7:(150,50,150),8:(125,125,125),9:(85,170,255)})
		self.FONT_SIZE = None


		# Object References
		self.SPACE = None
		self.URN = None
		self.CELL_NET = None
		self.PRODUCT_RULE_NET = None
		self.CELLS = None
		self.SPRITES = None
		self.CLOCK = None

		# Constants
		self.INTEL = False
		self.PRODUCT_COUNT = 200
		self.ENERGY_COSTS = {"pass":1, "transform":1, "reproduce": 1}
		self.INITIAL_ENERGY = 30
		self.RADIUS = 1.5
		self.ACTION_RATE = 1/1000.
		self.NEIGHBORHOOD = "Moore"

		# DYNAMIC STATE VARIABLES
		self.RATE = 1
		self.LABELS = False
		self.LINKS = False
		self.COUNTS = False
		self.REWOUND = False
		self.ACTION_SCHEDULED = False
		self.PRODUCT_BARS_DATA = False
		self.MASTER_COUNT = 0
		self.CHECKPOINT = 0
		self.DATA_LABELS = []
		self.ACTIVE = True
		self.ACTIVEA = None
		self.ACTIVEB = None
		self.RULE_COUNTS = None

	def set_var(self,name, value):

		if name == "URN_TYPE":
			self.URN_TYPE = value
		if name == "REPRO":
			self.REPRO = value
		if name == "SIMPLE":
			self.SIMPLE = value
		if name == "CHEM":
			self.CHEM = value
		if name == "TYPES":
			self.TYPES = value
			self.set_step_count()
			if self.FRACT_HEADLESS != None:
				self.NON_VIZ_STEPS = self.FRACT_HEADLESS * self.STEPS
		if name == "CELL_COUNT":
			self.CELL_COUNT = value
		if name == "RULE_COUNT":
			self.RULE_COUNT = value
		if name == "TOPO":
			self.TOPO = value
		if name == "MOBILE":
			self.MOBILE = value
		if name == "FRACT_HEADLESS":
			self.FRACT_HEADLESS = value
			if self.TYPES != None:
				self.NON_VIZ_STEPS = value* self.STEPS
		if name == "SCREEN_WIDTH":
			self.SCREEN_WIDTH = value
		if name == "SCREEN_HEIGHT":
			self.SCREEN_HEIGHT = value
		if name == "SPACE_WIDTH":
			self.SPACE_WIDTH = value
		if name == "SPACE_HEIGHT":
			self.SPACE_HEIGHT = value
		if name == "BORDER":
			self.BORDER = value
		if name == "X_SCALING":
			self.X_SCALING = value
		if name == "Y_SCALING":
			self.Y_SCALING = value
		if name == "HETERO":
			self.HOMOGENEOUS = not value


	def set_step_count(self):

		if self.TYPES == 3:
			self.STEPS = 410000
		elif self.TYPES == 4:
			self.STEPS = 580000
		elif self.TYPES == 5:
			self.STEPS = 770000
		elif self.TYPES == 6:
			self.STEPS = 980000
		elif self.TYPES == 7:
			self.STEPS = 1210000
		elif self.TYPES == 8:
			self.STEPS = 1460000
		elif self.TYPES == 9:
			self.STEPS = 1720000
		else:
			self.STEPS = 270000



	def setup(self):

		self.BORDER = int(self.SCREEN_HEIGHT*.06)
		self.MAIN_WINDOW_WIDTH = int(self.SCREEN_WIDTH*.68)
		self.MAIN_WINDOW_HEIGHT = int(self.SCREEN_HEIGHT*.93)
		self.X_SCALING= self.MAIN_WINDOW_WIDTH/float(self.SPACE_WIDTH)
		self.Y_SCALING = ((self.MAIN_WINDOW_HEIGHT-self.BORDER)
			/float(self.SPACE_HEIGHT))

		self.RULE_WINDOW_WIDTH = int(self.SCREEN_WIDTH *.31)
		self.RULE_WINDOW_HEIGHT = int(self.SCREEN_HEIGHT *.47)

		self.PRODUCT_WINDOW_WIDTH = int(self.SCREEN_WIDTH *.31)
		self.PRODUCT_WINDOW_HEIGHT = int(self.SCREEN_HEIGHT *.44)

		self.set_verts()
		self.set_colors()
		self.set_resource_grid()


	def set_verts(self):

		## This part sets up the geometry of the rules circle,
		## labels and links.
		height = self.RULE_WINDOW_HEIGHT

		centerx = self.RULE_WINDOW_WIDTH/2.
		centery = height/2.

		diameter = height/2.55
		diameter2 = height/2.15
		diameter3 = height/2.05
		diameter4 = height/1.80

		rads = 0
		verts = []
		verts2 = []
		for i in range(199):
			verts.append(centerx + diameter*math.cos(rads))
			verts.append(centery + diameter*math.sin(rads))
			verts.append(centerx + diameter2*math.cos(rads))
			verts.append(centery + diameter2*math.sin(rads))

			verts2.append((centerx + diameter*math.cos(rads),
				centery + diameter*math.sin(rads)))

			rads += .031415

		verts.append(centerx + diameter*math.cos(0))
		verts.append(centery + diameter*math.sin(0))
		verts.append(centerx + diameter2*math.cos(0))
		verts.append(centery + diameter2*math.sin(0))
		verts2.append((centerx + diameter*math.cos(0),
			centery + diameter*math.sin(0)))
		
		self.VERTS = verts
		self.LINK_VERTS = verts2

		verts = []
		rads = 0
		for i in range(60):
			verts.append((centerx + diameter3*math.cos(rads),
				centery + diameter3*math.sin(rads)))
			rads += .031415
		for i in range(100):
			verts.append((centerx + diameter4*math.cos(rads),
				centery + diameter3*math.sin(rads)))
			rads += .031415
		for i in range(40):
			verts.append((centerx + diameter3*math.cos(rads),
				centery + diameter3*math.sin(rads)))
			rads += .031415

		self.LABEL_VERTS = verts

	def set_colors(self):
		## This part defines a lot of colors to associate with rule types
		colors = []
		r,g,b = 255, 255,255
		if self.CHEM == "ALL":
			count_types = self.TYPES*(self.TYPES-1)
		else:
			count_types = self.TYPES

		inc = 255/(int(count_types**(.333))+1)
		count_incs = 0
		while r >= inc:
			while g >= inc:
				while b >= inc:
					colors.append([r,g,b])
					b -= inc
					count_incs +=1
				b = 255
				g -= inc
			b=255
			g=255
			r -= inc 

		self.RNG.shuffle(colors)
		self.COLORS = colors


	def set_resource_grid(self):
		## This sets up things for the resource visualization grid.
		window_width = self.PRODUCT_WINDOW_WIDTH
		border = 5
		space_width = window_width - 2 * border
		inc_x = space_width/self.SPACE_WIDTH
		window_height = self.PRODUCT_WINDOW_HEIGHT
		space_height = window_height - 2 * border
		inc_y = space_height/self.SPACE_HEIGHT


		

		lines = pyglet.graphics.Batch()
		if not self.HOMOGENEOUS and "endo" in self.URN_TYPE:
			y_start = border 
			y_end = border + inc_y*self.SPACE_HEIGHT
			x_start = border
			x_end = border + inc_x*self.SPACE_WIDTH
		
			x = border
			for i in range(self.SPACE_WIDTH+1):
				lines.add(2, pyglet.gl.GL_LINES, None,
					('v2f', (x,y_start, x, y_end)),
					('c3B',(50,50,50,50,50,50)))
				x += inc_x

			y = border
			for i in range(self.SPACE_HEIGHT + 1):
				lines.add(2, pyglet.gl.GL_LINES,None,
					('v2f',(x_start,y, x_end, y)),
					('c3B',(50,50,50,50,50,50)))
				y += inc_y



			corners = {}
			x= border
			for i in range(1,self.SPACE_WIDTH+1):
				y = border
				for j in range(1,self.SPACE_HEIGHT+1):
					corners[i,j] = (x,y)
					y += inc_y
				x+= inc_x
			self.CORNERS = corners
			
		else:
			border_x = window_width/6
			border_y = window_height/6
			lines.add(2, pyglet.gl.GL_LINES, None,
					('v2f', (border_x,border_y, border_x*5, border_y)),
					('c3B',(50,50,50,50,50,50)))
			lines.add(2, pyglet.gl.GL_LINES, None,
					('v2f', (border_x,border_y*5, border_x*5, border_y*5)),
					('c3B',(50,50,50,50,50,50)))
			lines.add(2, pyglet.gl.GL_LINES, None,
					('v2f', (border_x,border_y, border_x, border_y*5)),
					('c3B',(50,50,50,50,50,50)))
			lines.add(2, pyglet.gl.GL_LINES, None,
					('v2f', (border_x*5,border_y, border_x*5, border_y*5)),
					('c3B',(50,50,50,50,50,50)))
			pyglet.text.Label(self.URN_TYPE+" homogeneous urn",
				x=border_x*1.2,y=border_y*5+5,
				color=(0,0,0,150),font_size=14, bold=True, batch=lines)
			self.CORNERS = {(1,1): (border_x,border_y)}
			inc_x = border_x*4
			inc_y = border_y*4

			

		self.GRID_LINES = lines

		if self.TYPES <=4:
			anch = {1:(0,0),
				2:(inc_x/2,0),
				3:(0,inc_y/2),
				4:(inc_x/2,inc_y/2)}
			self.X_INC = inc_x/2
			self.Y_INC = inc_y/2
			if self.HOMOGENEOUS:
				self.FONT_SIZE = 20
			else:
				self.FONT_SIZE = 7
		elif self.TYPES <=6:
			x_inc = int(inc_x/3.)
			y_inc = int(inc_y/2.)
			anch = {1:(0,0),
				2:(x_inc,0),
				3:(x_inc*2,0),
				4:(0,y_inc),
				5:(x_inc,y_inc),
				6:(x_inc*2,y_inc)}
			self.X_INC = x_inc
			self.Y_INC = y_inc
			self.PRODUCT_ANCHORS = anch
			if self.HOMOGENEOUS:
				self.FONT_SIZE = 20
			else:
				self.FONT_SIZE = 6

		else:
			x_inc = int(inc_x/3.)
			y_inc = int(inc_y/3.)
			self.X_INC = x_inc
			self.Y_INC = y_inc
			anch = {1:(0,0),
				2:(x_inc,0),
				3:(x_inc*2,0),
				4:(0,y_inc),
				5:(x_inc,y_inc),
				6:(x_inc*2,y_inc),
				7:(0, y_inc*2),
				8:(x_inc,y_inc*2),
				9:(x_inc*2,y_inc*2)}
			if self.HOMOGENEOUS:
				self.FONT_SIZE = 18
			else:
				self.FONT_SIZE = 4

		self.PRODUCT_ANCHORS = anch
