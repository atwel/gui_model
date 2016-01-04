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
import AC_Variables
import AC_Params
import AC_Sprites
import pyglet
import math


VARS = AC_Variables.VARS()

AC_Params.Gatherer(VARS)

try:
	sconfig = pyglet.gl.Config(sample_buffers=1, samples=4,
		depth_size=16, double_buffer=True)
except:
	sconfig = None

# At this point, we have everything for the model. Now we need to start up the graphics
main_window = pyglet.window.Window(width=VARS.MAIN_WINDOW_WIDTH,
	height=VARS.MAIN_WINDOW_HEIGHT,resizable=True,
	caption="Cartesian Space",visible=False, config=sconfig)
main_window.set_location(0,int(VARS.SCREEN_HEIGHT*.06))
pyglet.gl.glClearColor(.95, .95, .95, .2)



rule_plot_window = pyglet.window.Window(width=VARS.RULE_WINDOW_WIDTH,
	height=VARS.RULE_WINDOW_HEIGHT,resizable=True,
	caption="Cell Rule Counts",visible=False,config=sconfig)
rule_plot_window.set_location(int(VARS.SCREEN_WIDTH*.69),int(VARS.SCREEN_HEIGHT*.06))
pyglet.gl.glClearColor(.95, .95, .95, .2)


product_plot_window = pyglet.window.Window(width=VARS.PRODUCT_WINDOW_WIDTH,
	height=VARS.PRODUCT_WINDOW_HEIGHT,resizable=True,
	caption="Count Product Types",visible=False,config=sconfig)
product_plot_window.set_location(int(VARS.SCREEN_WIDTH*.69),int(VARS.SCREEN_HEIGHT*.56))
pyglet.gl.glClearColor(.95, .95, .95, .2)


cell_batch = pyglet.graphics.Batch()
product_label_batch = pyglet.graphics.Batch()
rule_bar_batch = pyglet.graphics.Batch()
control_batch = pyglet.graphics.Batch()
cell_label_batch = pyglet.graphics.Batch()

control_sprites = []
control_sprites.append(AC_Sprites.Control_Sprite(pyglet.image.load("oval.png"), VARS,
	int(VARS.SCREEN_WIDTH*.39), 3,.25,
	"active", control_batch,main_window))
control_sprites.append(AC_Sprites.Control_Sprite(pyglet.image.load("counts.png"), VARS,
	int(VARS.SCREEN_WIDTH*.44), 1,.38,
	"counts", control_batch,main_window))
control_sprites.append(AC_Sprites.Control_Sprite(pyglet.image.load("Networks.png"),VARS,
	int(VARS.SCREEN_WIDTH*.48),1,.38,
	"network",control_batch,main_window))
control_sprites.append(AC_Sprites.Control_Sprite(pyglet.image.load("labels.png"),VARS,
	int(VARS.SCREEN_WIDTH*.52), 1,.38,
	"labels",control_batch,main_window))
control_sprites.append(AC_Sprites.Control_Sprite(pyglet.image.load("rewind.png"),VARS,
	int(VARS.SCREEN_WIDTH*.56), 1,.38,
	"backward",control_batch,main_window))
control_sprites.append(AC_Sprites.Control_Sprite(pyglet.image.load("pause.png"),VARS,
	int(VARS.SCREEN_WIDTH*.60),1,.38,
	"pause",control_batch,main_window))
control_sprites.append(AC_Sprites.Control_Sprite(pyglet.image.load("play.png"),VARS,
	int(VARS.SCREEN_WIDTH*.64),1,.38,
	"play",control_batch,main_window))
control_sprites.append(pyglet.text.Label("Active",x=VARS.MAIN_WINDOW_WIDTH*.58,
		y=20, color=(0,0,0,150),font_size=10,batch=control_batch))




@main_window.event
def on_draw():
	main_window.clear()
	pyglet.text.Label(str(VARS.MASTER_COUNT),x=5, y=6,
		color=(0,0,0,150), font_size=20, bold=True).draw()
	control_batch.draw()



	for i in VARS.DATA_LABELS:
		i.draw()

	if VARS.LINKS:
		pyglet.graphics.glColor3f(0, 0, 0)
		pyglet.graphics.glLineWidth(3)
		for source,target in VARS.PRODUCT_RULE_NET.net.edges():
			s = source.owner.Sprite
			t = target.owner.Sprite
			if s.x == t.x:
				pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2f', 
					(s.x+ s.width/3,s.y+s.height/2.,t.x
					+t.width/3,t.y+t.height/2.)))
			else:
				pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2f',
					(s.x+ s.width/2,s.y+s.height/2.,t.x
					+ t.width/2,t.y+t.height/2.)))
	top = []
	for i in VARS.SPRITES:
		if i.cell.isAlive:
			if i.tracked == True:
				top.append(i)
			if i.id == VARS.ACTIVEA:
				top.append(i)
			elif i.id == VARS.ACTIVEB:
				top.append(i)
			else:
				i.color = (200,200,200)
				i.draw()
			if VARS.LABELS:
				anchor = i.position
				center = (anchor[0] + i.width/2., anchor[1] +i.height/2.)
				pyglet.text.Label(str(i.label), x=center[0]-12,
					y=center[1]+9,width=15, multiline=True,
					font_size=8,color=(0,0,0,255)).draw()
			if VARS.COUNTS:
				anchor = i.position
				center = (anchor[0] + i.width/2., anchor[1] +i.height/2.)
				pyglet.text.Label(str(i.cell.count_rules), x=center[0]-10,
					y=center[1]-4,font_size=12,color=(0,0,0,255)).draw()

	for i in top:
		if (i.id == VARS.ACTIVEA or i.id == VARS.ACTIVEB):
			if VARS.ACTIVE:
				i.color = (100,255,90)
			else:
				i.color = (200,200,200)

		if i.tracked:
			i.color = (150,150,150)

		i.draw()
		if VARS.LABELS:
			anchor = i.position
			center = (anchor[0] + i.width/2., anchor[1] +i.height/2.)
			pyglet.text.Label(str(i.label), x=center[0]-12, y=center[1]+9,
				width=15, multiline=True, font_size=8,
				color=(0,0,0,255)).draw()
		if VARS.COUNTS:
			anchor = i.position
			center = (anchor[0] + i.width/2., anchor[1] +i.height/2.)
			pyglet.text.Label(str(i.cell.count_rules), x=center[0]-10,
				y=center[1]-4,font_size=12,color=(0,0,0,255)).draw()




@main_window.event
def on_resize(width,height):
	x_scale = width/float(VARS.MAIN_WINDOW_WIDTH)
	y_scale = height/float(VARS.MAIN_WINDOW_HEIGHT)
	if x_scale<1 and y_scale <1:
		scale = min(x_scale,y_scale)
	else:
		scale = max(x_scale,y_scale)
	for sprt in VARS.SPRITES:
		sprt.x *= x_scale
		sprt.y *= y_scale
		sprt.scale *= scale

	VARS.MAIN_WINDOW_WIDTH = width
	VARS.MAIN_WINDOW_HEIGHT = height
	VARS.BORDER *= y_scale
	VARS.X_SCALING = width/float(VARS.SPACE_WIDTH)
	VARS.Y_SCALING = (height-VARS.BORDER)/float(VARS.SPACE_HEIGHT)

	for sprt in control_sprites:
		sprt.x *= x_scale
		sprt.y *= y_scale
		try:
			sprt.scale *=scale
		except:
			sprt.font_size = int(sprt.font_size*scale)

@rule_plot_window.event
def on_draw():
	rule_plot_window.clear()
	pyglet.graphics.glLineWidth(1)

	counts = VARS.RULE_DATA
	a = sum([i[0] for i in counts])
	if a != 200:
		counts = [[i*int(a/200), j, k] for i,j,k in counts]

	a = sum([i[0] for i in counts])
	if a < 200:
		for i in range(200 - a):
			counts[VARS.RNG.randint(len(counts))][0] += 1
	elif a > 200:
		for i in range(a-200):
			counts[VAR.RNG.randint(len(counts))][0] -= 1
	first = True
	start = 0
	label_point = 0
	anchors = {}
	cnts = {}
	viz=False
	if len(counts)<20:
		viz = True

	for rule, color, label in counts:
		if rule > 0:
			lbl = tuple([int(i) for i in label.split("->")])
			if first:
				clr = []
				for i in range(rule*2):
					clr.extend(color)
				pyglet.graphics.draw(rule*2, pyglet.gl.GL_QUAD_STRIP, 
					('v2f', VARS.VERTS[start:start+rule*4]),('c3B', clr))

				first=False
			else:
				clr = []
				for i in range(rule*2 + 2):
					clr.extend(color)
				pyglet.graphics.draw(rule*2+2, pyglet.gl.GL_QUAD_STRIP,
					('v2f', VARS.VERTS[start-4:start+rule*4]),('c3B', clr))
			
			if viz:
				anchors[lbl] = VARS.LINK_VERTS[int(rule/2. + label_point)]

				x,y = VARS.LABEL_VERTS[int(rule/2. + label_point)]
				pyglet.text.Label(label, x=x, y=y,font_size=10,
					color=(0,0,0,255)).draw()
				label_point = rule + label_point

			start = start + rule*4

	if viz:
		pyglet.graphics.glLineWidth(5)
		for in_put, output in anchors.keys():
			for ip, op in anchors.keys():
				if ip == output and in_put == op:
					x1,y1 = anchors[(in_put,output)]
					x2,y2 = anchors[(ip,op)]
					pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
						('v2f', (x1,y1,x2,y2)),
						('c3B',(50,50,255,50,50,255)))
				elif ip == output:
					x1,y1 = anchors[(in_put,output)]
					x2,y2 = anchors[(ip,op)]
					pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
						('v2f', (x1,y1,x2,y2)), 
						('c3B',(150,150,175,50,50,255)))

				elif in_put == op: 
					x1,y1 = anchors[(in_put,output)]
					x2,y2 = anchors[(ip,op)]
					pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
						('v2f', (x1,y1,x2,y2)),
						('c3B',(50,50,255,150,150,150)))

		pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
			('v2f', (VARS.RULE_WINDOW_WIDTH*.805,VARS.RULE_WINDOW_HEIGHT*.97,
			VARS.RULE_WINDOW_WIDTH*.968,VARS.RULE_WINDOW_HEIGHT*.97)),
			('c3B',(50,50,255,150,150,150)))
		pyglet.text.Label("<----------", x=VARS.RULE_WINDOW_WIDTH*.81,
			y=VARS.RULE_WINDOW_HEIGHT*.925, color=(0,0,0,150),
			font_size=10, bold=True).draw()

		pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
			('v2f', (VARS.RULE_WINDOW_WIDTH*.805,VARS.RULE_WINDOW_HEIGHT*.89,
			VARS.RULE_WINDOW_WIDTH*.968,VARS.RULE_WINDOW_HEIGHT*.89)),
			('c3B',(50,50,255,50,50,255)))

		pyglet.text.Label("<--------->", x=VARS.RULE_WINDOW_WIDTH*.81,
			y=VARS.RULE_WINDOW_HEIGHT*.85, color=(0,0,0,150),
			font_size=10, bold=True).draw()

	pyglet.text.Label("Rules: "+str(VARS.RULE_COUNT),
		x=VARS.RULE_WINDOW_WIDTH*.76,y=VARS.RULE_WINDOW_HEIGHT*.02,
		color=(0,0,0,150),font_size=14, bold=True).draw()

	mask.draw()

@rule_plot_window.event
def on_resize(width,height):
	VARS.RULE_WINDOW_WIDTH = width
	VARS.RULE_WINDOW_HEIGHT = height
	VARS.set_verts()
			
@product_plot_window.event
def on_draw():
	product_plot_window.clear()
	VARS.GRID_LINES.draw()
	if "fixed" not in VARS.URN_TYPE:
		
		for loc,prods in VARS.PRODUCT_COUNTS.items():
			x,y = VARS.CORNERS[loc]
			for prod,count in prods.items():
				if count > 0:
					x1,y1 = VARS.PRODUCT_ANCHORS[prod]
					color = VARS.PRODUCT_COLORS[prod]
					pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, 
							('v2f', (x+x1,y+y1,
								x+x1+VARS.X_INC,y+y1,
								x+x1+VARS.X_INC,y+y1+VARS.Y_INC,
								x+x1,y+y1+VARS.Y_INC)),
							("c3B",color*4))
					if count > VARS.PRODUCT_COUNT:
						count = float("inf")
					pyglet.text.Label(str(count),x=x+x1+VARS.X_INC/3,
						y=y+y1+VARS.Y_INC/3.,color=(0,0,0,255),
						font_size=VARS.FONT_SIZE).draw()

@product_plot_window.event
def on_resize(width,height):
	scale = width/float(VARS.PRODUCT_WINDOW_WIDTH)
	VARS.FONT_SIZE *= scale*2
	VARS.PRODUCT_WINDOW_WIDTH = width
	VARS.PRODUCT_WINDOW_HEIGHT = height
	VARS.set_resource_grid()
    

@main_window.event
def on_close():
	pyglet.app.exit()


def update_rule_count():
	lst = []
	colors = VARS.COLORS
	for r_type, count  in VARS.SPACE.rule_counts.items():
		if count != 0:
			color = colors[r_type]
			lst.append((count,color,str(r_type[0])+"->"+str(r_type[1])))
	VARS.RULE_DATA= lst


def update_cells():
	for cell in VARS.CELLS:
		cell.update_labels()

def run_updates(inc):
	update_cells()
	update_rule_count()
	#update_product_count()



#Setting up the environment including the products
VARS.URN = AC_Products.Urn(VARS)

#Creating a network object for compatible rules
VARS.PRODUCT_RULE_NET = AC_ProductRuleNet.ProductRuleNet()

# mask is a picture drawn over the rule graph circle so that the graph
# looks like balls.
mask = pyglet.sprite.Sprite(pyglet.image.load("ballmask.png"))
mask.x = VARS.RULE_WINDOW_WIDTH/2. - mask.width/2.
mask.y = VARS.RULE_WINDOW_HEIGHT/2. - mask.height/2.


# creating the actual cells with Sprites
cells = []
sprites = []
for i in range(VARS.CELL_COUNT):
	sprite = AC_Sprites.Cell_Sprite(pyglet.image.load("oval.png"),cell_batch, str(i+1),VARS,main_window)
	sprite.scale = 3.25/VARS.SPACE_WIDTH
	sprites.append(sprite)
	new_cell = AC_Cells.Cell(i+1, sprite, VARS)
	cells.append(new_cell)
	sprite.add_cell(new_cell)

VARS.CELLS = cells
VARS.SPRITES = sprites

# Creating a network of neighbors on torus grid
VARS.SPACE = AC_Space.Space(VARS)

# Creating all of the rules and 
# passing out to cells at random
for rule in AC_ProductRules.create_RuleSet(VARS):
	cell = VARS.RNG.choice(VARS.CELLS)
	cell.add_ProductRule(rule)


for cell in VARS.CELLS:
	if cell.count_rules == 0:
		cell.isAlive = False
	else:
		if VARS.MOBILE:
			for ngh in cells:
				if ngh != cell:
					if ngh.product_netrules.values() != {}:
						for r1 in cell.product_netrules.values():
							for r2 in ngh.product_netrules.values():
								VARS.PRODUCT_RULE_NET.add_edge(r1,r2)
		else:
			for ngh in cell.neighbors:
				if ngh.product_netrules.values() != {}:
					for r1 in cell.product_netrules.values():
						for r2 in ngh.product_netrules.values():
							VARS.PRODUCT_RULE_NET.add_edge(r1,r2)


update_rule_count()

print "Running the first %d steps headless . . . " %VARS.NON_VIZ_STEPS
while VARS.MASTER_COUNT < VARS.NON_VIZ_STEPS:
	VARS.SPACE.activate_random_rule()
   

VARS.CLOCK = pyglet.clock
VARS.CLOCK.schedule_interval(VARS.SPACE.cell_action, VARS.ACTION_RATE)
VARS.CLOCK.schedule_interval_soft(run_updates, 1)

main_window.set_visible(True)
rule_plot_window.set_visible(True)
product_plot_window.set_visible(True)

pyglet.app.run()

              