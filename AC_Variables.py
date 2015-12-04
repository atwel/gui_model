


class VARIABLES:

	def __init__(self):

		#  INDEPENDENT VARIABLES
		# Set on start up
		self.URN = None
		self.REPRO = None
		self.CHEM = None
		self.TYPES = None
		self.STEPS = None
		self.CELL_COUNT = None
		self.RULE_COUNT = None
		self.TOPO = None
		self.MOBILE = None
		self.FRACT_HEADLESS = None
		self.NON_VIZ_STEPS = None

		# Constants
		self.INTEL = False
		self.PRODUCT_COUNT = 200
		self.ENERGY_COSTS = {"pass":1, "transform":1, "reproduce": 1}
		self.INITIAL_ENERGY = 30
		self.RADIUS = 1.5
		self.ACTION_RATE = 1/10.

		# DYNAMIC STATE VARIABLES
		self.LABELS = False
		self.LINKS = False
		self.REWOUND = False
		self.ACTION_SCHEDULED = False
		self.PRODUCT_BARS_DATA = False
		self.CHECKPOINT = 0

	def set_var(self,name, value):

		if name == "URN":
			self.URN = value
		if name == "REPRO":
			self.REPRO = value
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
			self.FRACT_HEADLESS = val
			if self.TYPES != None:
				self.NON_VIZ_STEPS = val * self.STEPS

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
             
