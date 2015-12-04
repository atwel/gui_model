""" This is the model initializer and controller. Parameters are specified
herein and the progression through the different combinations of 
parameters happens here as well. The final data from the run are gathered
and printed to file.


Written by Jon Atwell
"""


import AC_Products
import AC_ProductRules
import AC_ProductRuleNet
import AC_Cells
import AC_Space
import random
import numpy as np
import networkx as nx
import json
import sys
import pyglet as pyg
from pyglet import window, image, graphics, text
from pyglet.text import caret, layout
from Tkinter import *
import math



class Parameter_App:
        def __init__(self, master):
            self.master = master
            self.master.minsize(width=570, height=400)
            frame = Frame(master).grid()

            environment = [("   Fixed-Rich","fixed-rich"),("   Fixed-Poor",
                "fixed-poor"),("   Endo-Rich","endo-rich"),("   Endo-Poor","endo-poor")]
            self.urn = StringVar()
            self.urn.set("fixed-rich")
            
            learning = [("Source","source"), ("Target","target")]
            self.repro = StringVar()
            self.repro.set("source")

            chemistry = [("ALL","ALL"),("SoloH","SOLOH")]
            self.chem = StringVar()
            self.chem.set("ALL")

            topology = [("Spatial","spatial"),("Non-spatial","nonspatial")]
            self.topo = StringVar()
            self.topo.set("spatial")

            self.product_count = IntVar()
            self.product_count.set(4)

            self.cell_count = IntVar()
            self.cell_count.set(20)

            self.rule_count = IntVar()
            self.rule_count.set(200)

            self.mobile = BooleanVar()
            self.mobile.set(True)

            self.fract_headless=DoubleVar()
            self.fract_headless.set(.80)

            self.labels_on = BooleanVar()
            self.labels_on.set(False)

            
            Label(frame, text="""\n\nType of Environment:\n""").grid(row=0,column=0)
            i = 0
            for txt, val in environment:
                i += 1
                Radiobutton(frame, text=txt, variable=self.urn, value=val).grid(row=i, column=0)

            Label(frame, text="""\n\nReproduction Method:\n""").grid(row=0,column=1)
            j=0
            for txt, val in learning:
                j+=1
                Radiobutton(frame, text=txt, variable=self.repro,value=val).grid(row=j, column=1)

            Label(frame, text="""\n\nChemistry Type:\n""").grid(row=0,column=2)
            k=0
            for txt, val in chemistry:
                k+=1
                Radiobutton(frame, text=txt, variable=self.chem,value=val).grid(row=k, column=2)

            i = max(max(i,j),k)+1

            Label(frame, text="""\n\nNumber of Cells:\n""").grid(row=i, column=0)
            Scale(frame, from_=20, to=500, resolution=10, variable=self.cell_count, orient=HORIZONTAL, label="20               500").grid(row=i+1,column=0)

            Label(frame, text="""\n\nNumber of Product Types:\n""").grid(row=i, column=1)
            Scale(frame, from_=2, to=9,variable=self.product_count, orient=HORIZONTAL, label="2                     9").grid(row=i+1, column=1)

            Label(frame, text="""\n\nNumber of Rule Instances:\n""").grid(row=i, column=2)
            Scale(frame, from_=100, to=500, resolution=10, variable=self.rule_count, orient=HORIZONTAL, label="100              500").grid(row=i+1,column=2)

            i +=2

            Label(frame, text="""\n\nTopology:\n""").grid(row=i,column=0)
            k=i
            for txt, val in topology:
                k+=1
                Radiobutton(frame, text=txt, variable=self.topo,value=val,command=self.topo_check).grid(row=k, column=0)


            Label(frame, text="""\n\nMobile Cells?:\n""").grid(row=i, column=1)
            Checkbutton(frame, variable=self.mobile,command=self.mobile_check).grid(row=i+1,column=1)

            Label(frame, text="""\n\nFraction of Run w/o Graphics:\n""").grid(row=i, column=2)
            Scale(frame, from_=0, to=1, resolution=.05, variable=self.fract_headless, orient=HORIZONTAL, label="0                      1").grid(row=i+1,column=2)


            i += 3
            Label(frame, text="\n\n\nClick submit to start the simulation\n").grid(row=i,column=1)
            Button(frame, text="Submit", command=self.quit).grid(row=i+1, column=1)

            Label(frame, text="   ").grid(row=i+2, column=1)

        def topo_check(self):
            if self.topo.get() == "nonspatial":
                self.mobile.set(False)

        def mobile_check(self):
            if self.mobile.get() == True:
                self.topo.set("spatial")
                self.cell_count.set(20)
            else:
            	self.cell_count.set(100)

        def get_parameters(self):
            return [self.urn.get(), self.repro.get(), self.chem.get(), self.product_count.get(), self.cell_count.get(), self.rule_count.get(), self.topo.get(), self.mobile.get(), self.fract_headless.get()]

        def quit(self):
            self.master.destroy()



class control_Sprite(pyg.sprite.Sprite):

	def __init__(self, cell_image, x, y, scale, name,batch):
		self.name = name
		pyg.sprite.Sprite.__init__(self, cell_image, batch=batch)
		self.scale = scale
		self.color = (0,0,0)
		self.x = x
		self.y = y
		main_window.push_handlers(self.on_mouse_press)

	def on_mouse_press(self, x, y, button, modifiers):
		global action_scheduled
		global rewound
		global action_rate
		global product_bars_data
		global LABELS
		global LINKS
		global COUNTS
		anchor = self.position

		# now we'll get the visual center
		center = (anchor[0] + self.width/2., anchor[1] +self.height/2.)

		# figuring out if the click was within the visual representation 
		# of the cell
		dis = ((x-center[0])**2 + (y-center[1])**2)**.5
		rad = self.width/2.

		if dis <= rad:
			if self.name == "pause":
				pyg.clock.unschedule(cell_action)
				#pyg.clock.unschedule(rupdate_product_count)
				action_scheduled = False
			elif self.name == "play": 
				if not action_scheduled:
					pyg.clock.schedule_interval(cell_action, action_rate)
					#pyg.clock.schedule_interval(update_product_count, 1, product_bars_data, 255)
					action_scheduled = True
					rewound = False
				else:
					pyg.clock.unschedule(cell_action)
					pyg.clock.schedule_interval(cell_action, action_rate/2.)
			elif self.name == "stop":
				pyg.app.exit()
			elif self.name == "labels":
				if LABELS:
					LABELS = False
				else:
					LABELS = True
					COUNTS = False
			elif self.name == "network":
				if LINKS:
					LINKS = False
				else:
					LINKS = True
			elif self.name == "backward":
				if not rewound:
					pyg.clock.unschedule(cell_action)
					#pyg.clock.unschedule(update_product_count)
					myspace.load_checkpoint(cells,(myspace.checkpoint-1))
					rewound= True
				else:
					myspace.load_checkpoint(cells,(myspace.checkpoint-2))
			elif self.name == "counts":
				if COUNTS:
					COUNTS = False
				else:
					COUNTS = True
					LABELS = False



class cell_Sprite(pyg.sprite.Sprite):

    def __init__(self, cell_image, batch, name):
        self.cell = None
        self.name = name
        self.active = False
        self.labels = []
        pyg.sprite.Sprite.__init__(self, cell_image, batch=batch)
        main_window.push_handlers(self.on_mouse_press)

    def add_cell(self, cell):
        self.cell = cell
    
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
            
            rule_str = []
            total_rules = 0
            for input_key in self.cell.product_rules.keys():
                for output_key in self.cell.product_rules[input_key].keys():
                    rls = len(self.cell.product_rules[input_key][output_key])
                    total_rules += rls
                    rule_str.append(str(input_key) +"->" + str(output_key)+ ": " + str(rls))

            data_labels_list[0] = pyg.text.Label("Cell: " + str(self.name) + "  # rules: " +str(total_rules), x=5, y=75,color=(0,0,0,150))

            dataA = []
            dataB = []
            cnt = 0
            for index, string in enumerate(rule_str):
                if cnt < 30:
                    cnt += len(string)
                    dataA.append(string)
                else:
                    dataB.append(string)
            
            try:
                rule_strA = "  ".join(dataA)
            except:
                rule_strA = " "
            try:
                rule_strB = "  ".join(dataB)
            except :
                rule_strB = " "

            data_labels_list[1] = pyg.text.Label(rule_strA, x=5, y=55,color=(0,0,0,150))
            data_labels_list[2] = pyg.text.Label(rule_strB, x=5, y=35,color=(0,0,0,150))
            hld = ""
            for i in self.cell.products.keys():
                cnt = len(self.cell.products[i])
                if cnt != 0:
                    hld += (str(i) + ": " + str(cnt) + "  ")

            data_labels_list[3] = pyg.text.Label("Storage - "+ hld, x=5, y=15,color=(0,0,0,150))
            if not self.cell.tracked:
            	self.color = (100,100,255)
            	for cell in cells:
            		cell.tracked = False
            	self.cell.tracked = True
 
def get_step_count(PRODUCT_TYPES):
    """A utility function to determine how long to run the model.
    """

    STEPS = 270000
    
    if PRODUCT_TYPES == 3:
        STEPS = 410000
    elif PRODUCT_TYPES == 4:
        STEPS = 580000
    elif PRODUCT_TYPES == 5:
        STEPS = 770000
    elif PRODUCT_TYPES == 6:
        STEPS = 980000
    elif PRODUCT_TYPES == 7:
        STEPS = 1210000
    elif PRODUCT_TYPES == 8:
        STEPS = 1460000
    elif PRODUCT_TYPES == 9:
        STEPS = 1720000
                         
    return STEPS
    
def print_data(name, myspace, myRuleNet, cells):

    try:
        output_file = open(name+".csv", "a+")
    except:
        output_file = open(name+".csv", "w+")

    if (myspace.last_added_rule + STEPS*.1 > myspace.master_count):  

    #Creating a network object for compatible rules
        myRuleNet = AC_ProductRuleNet.ProductRuleNet()

        for cell in cells:
            for inpt in cell.product_rules.keys():
                for otpt in cell.product_rules[inpt].keys():
                    cell.add_ProductNetRule(
                        cell.product_rules[inpt][otpt][0])

    #Filling in the actual compatible rule network. 
        for cell in cells:
            if cell.product_netrules.values() != {}:
                for ngh in cell.neighbors:
                    if ngh.product_netrules.values() != {}:
                        for r1 in cell.product_netrules.values():
                            for r2 in ngh.product_netrules.values():
                                # check of compatibility in funct.
                                myRuleNet.add_edge(r1,r2) 

        myRuleNet.net.edges()
        myRuleNet.update_cycle_counts(myspace.master_count)

        count_alive = 0

        for cell in cells:
            if cell.count_rules  > 0:
                count_alive += 1

        # Quick output of key data for sweep analysis

        data =  (str(count_run)+","+ 
            str(myRuleNet.cycle_counts)+","+
            str(myRuleNet.get_plus3cell_complexity())+","+
            str(myRuleNet.get_plus3rule_complexity())+","+
            str(count_alive)+","+str(myspace.last_added_rule)+"\n")
        output_file.write(data)
        output_file.close()

        print "writing html"
        for cell in myspace.cells:
            x,y = cell.get_location()
            cell.set_location(x*.5, y*.5)
        # Creating an HTML file to visualize the network
        AC_grapher.output_JSON(myspace,myRuleNet, name 
            +"-"+str(count_run)+ ".html")

    else:
        data =  (str(count_run)+","+ 
            str(0)+","+
            str(0)+","+
            str(0)+","+
            str(0)+","+str(myspace.last_added_rule)+"\n")
        output_file.write(data)
        output_file.close()





#******************************
# Above are a bunch of utility functions. Below is everything that runs the model and graphics
#
#******************************
root = Tk()

root.title("Basic Autocatalysis Parameters")
app=Parameter_App(root)
root.mainloop()


URN, REPRO, CHEM, TYPES, CELL_COUNT, RULE_COUNT, TOPO, MOBILE, FRACT_HEADLESS = app.get_parameters()
#URN="fixed-rich"
#REPRO="source"
#TYPES=4
#FRACT_HEADLESS=.1
#MOBILE =True
#TOPO = "spatial"
#CHEM = "ALL"
#RULE_COUNT = 200

non_viz_steps = FRACT_HEADLESS * get_step_count(TYPES)




INTEL= False
PRODUCT_COUNT = 200

if MOBILE:
    CELL_COUNT = 20
else:
    CELL_COUNT = 100

if MOBILE:
    LABELS = False #True
    LINKS = False
else:
    LABELS = False
    LINKS = False
COUNTS = False

ENERGY_COSTS = {"pass":1, "transform":1, "reproduce": 1}
INITIAL_ENERGY = 30
RADIUS = 1.5
action_rate = 1/10.


 ## Start setting up the run                       
name =  "-".join([str(TYPES), CHEM, str(INTEL), URN, TOPO])
print name

# as rng to reproduce runs if desired
seed = random.randint(0,sys.maxint)
RNG = random.Random(seed)

window_width = 950
window_height = 700
space_width = 10
space_height = 10
border_size = int(window_width/ float(space_width*1.1))


# At this point, we have everything for the model. Now we need to start up the graphics
main_window = window.Window(width=window_width, height=window_height, caption="Cartesian Space",style=window.Window.WINDOW_STYLE_TOOL)#,)
main_window.set_location(0,40)
pyg.gl.glClearColor(.85, .85, .85, .2)
main_window.clear()

rule_plot_window = window.Window(width=400, height=285, caption="Cell Rule Counts",style=window.Window.WINDOW_STYLE_TOOL)
rule_plot_window.set_location(955,155)
rule_plot_window.clear()
pyg.gl.glClearColor(.85, .85, .85, .2)

product_plot_window = window.Window(width=400, height=285, caption="Count Product Types",style=window.Window.WINDOW_STYLE_TOOL)
product_plot_window.set_location(955,455)
product_plot_window.clear()
pyg.gl.glClearColor(.85, .85, .85, .2)

data_window = window.Window(width=400, height=95, caption="Cell Data",style=window.Window.WINDOW_STYLE_TOOL)
data_window.set_location(955, 40)
data_window.clear()
pyg.gl.glClearColor(.85, .85, .85, .2)


STEPS = 0
cell_batch = graphics.Batch()
product_label_batch = graphics.Batch()
rule_bar_batch = graphics.Batch()
control_batch = graphics.Batch()
data_batch = graphics.Batch()
cell_label_batch = graphics.Batch()

cell_list = []
hld = pyg.text.Label(" ", x=5, y=55, color=(0,0,0,150))
cell_labels_list = [hld]
data_labels_list = [hld, hld, hld, hld]


control_list = []

control_list.append(control_Sprite(image.load("backward.png"), x=575, y=-10,scale=.5, name="counts", batch=control_batch))
control_list.append(control_Sprite(image.load("random.png"), x=620, y=-10,scale=.5, name="network", batch=control_batch))
control_list.append(control_Sprite(image.load("infinity.png"), x=665, y=-10,scale=.5, name="labels", batch=control_batch))
control_list.append(control_Sprite(image.load("left.png"), x=730, y=-10,scale=.5, name="backward", batch=control_batch))
control_list.append(control_Sprite(image.load("pause.png"), x=775, y=-10, scale=.5, name="pause", batch=control_batch))
control_list.append(control_Sprite(image.load("play.png"), x=820, y=-10,scale=.5, name="play", batch=control_batch))
control_list.append(control_Sprite(image.load("stop.png"),x=885, y=-10,scale=.5, name="stop", batch=control_batch))



@main_window.event
def on_draw():
	main_window.clear()
	steps = pyg.text.Label("Steps:  " + str(myspace.master_count),
		x=2, y=2, color=(0,0,0,150), font_size=20, bold=True)
	steps.draw()
	control_batch.draw()

	if LINKS:
		graphics.glColor3f(0, 0, 0)
		graphics.glLineWidth(3)
		for source,target in myRuleNet.net.edges():
			s = source.owner.Sprite
			t = target.owner.Sprite
			graphics.glColor3f(0, 0, 0)
			graphics.draw(2, pyg.gl.GL_LINES, ('v2f',
				(s.x+ s.width/2,s.y+s.height/2.,t.x
				+ t.width/2,t.y+t.height/2.)))
    
	for i in cell_list:
		if i.cell.isAlive:
			#if i.active:
			#	i.color = (100,100,100)
			#else:
			#	i.color = (0,255-155*math.log(1 + 1.71*i.cell.count_rules/200.),250)
			i.draw()
			if LABELS:
				i.cell.update_labels()
				anchor = i.position
				center = (anchor[0] + i.width/2., anchor[1] +i.height/2.)
				pyg.text.Label(str(i.label), x=center[0]-12, y=center[1]+5,
					width=15, multiline=True, font_size=8,
					color=(255,255,255,255)).draw()
			if COUNTS:
				anchor = i.position
				center = (anchor[0] + i.width/2., anchor[1] +i.height/2.)
				pyg.text.Label(str(i.cell.count_rules), x=center[0]-9, y=center[1]-4,
					width=15, multiline=True, font_size=12,
					color=(255,255,255,255)).draw()

@rule_plot_window.event
def on_draw():
	rule_plot_window.clear()
	graphics.glColor3f(0, 0, 255)
	for bar in rule_bars:
		graphics.draw(4, pyg.gl.GL_QUADS, ('v2f', bar))
	size = 20-len(rule_bars)
	for name, anchor in rule_bar_labels:
		if "->" in name:
			pyg.text.Label(name, x=anchor[0], y=anchor[1]-(size*.55),
				color=(0,0,0,150), font_size=size-3, bold=True).draw()
		else:
			pyg.text.Label(name, x=anchor[0], y=anchor[1],
				color=(0,0,0,150), font_size=size, bold=True).draw()


	graphics.glColor3f(0, 0, 0)
	graphics.glLineWidth(3)
	graphics.draw(2, pyg.gl.GL_LINES, ('v2f', (10.,30., 380., 30.)))
	graphics.draw(2, pyg.gl.GL_LINES, ('v2f',(10.,29., 10., 255)))


@product_plot_window.event
def on_draw():

	product_plot_window.clear()
	for bar in product_bars:
		graphics.glColor3f(0, 0, 255)
		graphics.draw(4, pyg.gl.GL_QUADS, ('v2f', bar))
	for count, anchor in product_bars_labels:
		pyg.text.Label(count, x=anchor[0], y=anchor[1], color=(0,0,0,150), font_size=10, bold=True).draw()


	graphics.glColor3f(0, 0, 0)
	graphics.glLineWidth(3)
	graphics.draw(2, pyg.gl.GL_LINES, ('v2f', (10.,30., 380., 30.)))
	graphics.draw(2, pyg.gl.GL_LINES, ('v2f',(10.,29., 10., 255)))
	product_label_batch.draw()
    


@data_window.event
def on_draw():
	data_window.clear()
	for i in data_labels_list:
		i.draw()

@main_window.event
def on_close():
	pyg.app.exit()



def update_product_count(product_bars_data, max_prod_height=225):
	global product_bars_labels
	product_bars_labels = []

	running_count = 0
	prods = len(product_bars_data)
	for product, points in product_bars_data:
		if product < prods:
			count = float(len(myurn.collection[product]))
			height = (count/200.) * max_prod_height
			product_bars[product-1]= (points[0], 30., points[1], 30., points[1], 
				height+30., points[0], height+30.)
			anchor = (points[1]-points[0]) *.3 + points[0]
			product_bars_labels.append((str(int(count)), (anchor, height + 50.)))
			running_count += count
		else:
			height = ((200-running_count)/200.) * max_prod_height
			product_bars[product-1]= (points[0], 30., points[1], 30., points[1], 
				height+30., points[0], height+30.)
			anchor = (points[1]-points[0]) *.3 + points[0]
			product_bars_labels.append((str(int(200-running_count)), (anchor, height + 50.)))


def update_rule_count(max_prod_height=225):
    global rule_bars
    rule_bars=[]
    global rule_bar_labels 
    rule_bar_labels = []
    count_rules = 0
    for rule in myspace.rule_counts.values():
        if rule > 0:
            count_rules += 1
    width_space = 370/((count_rules + 1)  + (2 * count_rules))
    i = 0

    for r_type, count  in myspace.rule_counts.items():
        if count != 0:
            points = ((width_space+10 + (i * 3 * width_space), width_space +10 + (i*3*width_space) + (2 * width_space)))
            height = (int(count)/200.) * max_prod_height
            rule_bars.append((points[0], 30., points[1], 30., points[1], 
                height+30., points[0], height+30.))
            i += 1
            anchor = (points[1]-points[0]) *.3 + points[0]
            rule_bar_labels.append((r_type, (anchor-4, 10.)))
            rule_bar_labels.append((str(count), (anchor, height+50.)))

def update_cells():
	for cell in cells:
		cell.update_labels()

def run_updates(inc):
	update_cells()
	update_rule_count()
	update_product_count(product_bars_data)

def cell_action(inc):
	n = int(1/float(inc))*10
	for i in range(n):
		myspace.activate_random_rule()



#Setting up the environment including the products
myurn = AC_Products.Urn(URN+"-"+REPRO, TYPES, RNG,INITIAL_ENERGY, 
    PRODUCT_COUNT)

# Creating all of the rules 
myrules = AC_ProductRules.create_RuleSet(CHEM,TYPES, RULE_COUNT, RNG)


#Creating a network object for compatible rules
myRuleNet = AC_ProductRuleNet.ProductRuleNet()



# creating the actual cells with Sprites
cell_image = image.load("oval.png")
cells = []
cell_radius = .005
for i in range(CELL_COUNT):
    sprite = cell_Sprite(cell_image,cell_batch, str(i+1))
    sprite.scale = 3.19/ (space_width)
    cell_list.append(sprite)
    new_cell = AC_Cells.Cell(myurn, myRuleNet, RNG, i+1, sprite, (window_width, window_height), (space_width, space_height), border_size, INTEL, REPRO, TOPO, RADIUS,LABELS,MOBILE)
    cells.append(new_cell)
    sprite.add_cell(new_cell)




# Creating a network of neighbors on torus grid
myspace= AC_Space.Space(cells, cell_radius, RNG, RADIUS, ENERGY_COSTS,MOBILE,myurn, INITIAL_ENERGY, myRuleNet, dimensions=(space_width, space_height))

for i in cells:
    i.add_Space(myspace)

print "made cells"
#passing out the myrules to cells at random
for i in range(len(myrules)):
    cell = RNG.choice(cells)
    cell.add_ProductRule(myrules.pop(0))


for cell in cells:
	if cell.count_rules == 0:
		cell.isAlive = False
	cell.update_labels()
	if cell.product_netrules.values() != {}:
		if MOBILE:
			for ngh in cells:
				if ngh != cell:
					if ngh.product_netrules.values() != {}:
						for r1 in cell.product_netrules.values():
							for r2 in ngh.product_netrules.values():
								myRuleNet.add_edge(r1,r2)
		else:
			for ngh in cell.neighbors:
				if ngh.product_netrules.values() != {}:
					for r1 in cell.product_netrules.values():
						for r2 in ngh.product_netrules.values():
							myRuleNet.add_edge(r1,r2)



saved=False
steps = 0
loaded=False
twosteps = 0
cells[0].save_checkpoint()

print "Running the first %d steps headless . . . " %non_viz_steps
while myspace.master_count < non_viz_steps:
    myspace.activate_random_rule()
    """if myspace.master_count >= 1000 and not saved:
        print "base save is checkpoint %d for step %d" %(myspace.checkpoint, myspace.master_count)
        cells[0].save_checkpoint()
        saved = True
    if saved and steps <=10000:
        if steps % 1000 == 0:
            print "saved Checkpoint %d at step %d" %(myspace.checkpoint, myspace.master_count)
            cells[0].save_checkpoint()
        steps+=1
        
    if saved and steps > 10000 and not loaded:
        print "reloading data now"
        myspace.load_checkpoint(myspace.cells,"1")
        for cell in myspace.cells:
            print "Cell "+str(cell.id)+" has active_rule " + str(cell.active_rule)
        print "The new checkpoint numebr is", myspace.checkpoint
        myspace.checkpoint +=10
        cells[0].save_checkpoint()
        print "Saved Checkpoint %d after load (step %d)" %(myspace.checkpoint-1, myspace.master_count)
        loaded = True
        
    if loaded and twosteps <=10000:
        if twosteps % 1000 == 0:
            print "Saved return checkpoint %d (step %d)" %(myspace.checkpoint, myspace.master_count)
            cells[0].save_checkpoint()
        twosteps +=1
        
    if twosteps > 10000:
        break"""


TOTAL_STEPS = get_step_count(TYPES)
pyg.clock.schedule_interval(cell_action, action_rate)
action_scheduled = True
rewound = False

# Setting up the bars for plotting product counts
count_products = len(myurn.collection.keys()) + 1
width_space = 370/((count_products + 1)  + (2 * count_products))
product_bars = [(0.,0.,0.,0.,0.,0.,0.,0.) for i in range(count_products)]
rule_bars=[]
rule_bar_labels = []
product_bars_labels = []

product_bars_data = []
if "endo" in URN:
    for i in range(count_products):    
        product_bars_data.append((i+1, (width_space + (i * 3 * width_space), width_space + (i*3*width_space) + (2 * width_space))))
        if i < count_products - 1:
            pyg.text.Label(str(i+1), x=(width_space*1.75 + (i * 3 * width_space)), y=5, color=(0,0,0,150), font_size=15, bold=True, batch=product_label_batch)
        else:
            pyg.text.Label("Circ.", x=(width_space*1.1 + (i * 3 * width_space)), y=5, color=(0,0,0,150), font_size=15, bold=True, batch=product_label_batch)
else:
    product_bars_data = []
    pyg.text.Label("Fixed Urn", x=160, y=150, color=(0,0,0,150), font_size=15, bold=True, batch=product_label_batch)


pyg.text.Label("-200", x=9, y=249, color=(0,0,0,150), font_size=15, bold=True, batch=product_label_batch)


pyg.clock.schedule_interval_soft(run_updates, 1)    

pyg.app.run()


print "Stopped at step: %d" %(myspace.master_count)

# print_data(name, myspace, myRuleNet, cells                 
                            

                            



