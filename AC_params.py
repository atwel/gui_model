from Tkinter import *

class Parameter_App:

	def __init__(self, master):

		self.master = master

		self.screen_width = IntVar()
		self.screen_width.set(self.master.winfo_screenwidth())
		self.screen_height = IntVar()
		self.screen_height.set(self.master.winfo_screenheight())

		self.space_width = IntVar()
		self.space_width.set(10)
		self.space_height = IntVar()
		self.space_height.set(10)

		self.border = IntVar()
		self.x_scaling = IntVar()
		self.y_scaling = IntVar()


		self.master.minsize(width=int(self.screen_width.get()*.40),
			height=int(self.screen_height.get()*.80))

		frame = Frame(master).grid()

		environment = [("   Fixed-Rich","fixed-rich"),("   Fixed-Poor",
			"fixed-poor"),("   Endo-Rich",
			"endo-rich"),("   Endo-Poor","endo-poor")]
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
		self.fract_headless.set(.00)

		self.labels_on = BooleanVar()
		self.labels_on.set(False)


		Label(frame, text="""\n\nType of Environment:
			\n""").grid(row=0,column=0)
		i = 0
		for txt, val in environment:
			i += 1
			Radiobutton(frame, text=txt, variable=self.urn,
				value=val).grid(row=i, column=0)

		Label(frame, text="""\n\nReproduction Method:
			\n""").grid(row=0,column=1)
		j=0
		for txt, val in learning:
			j+=1
			Radiobutton(frame, text=txt, variable=self.repro,
				value=val).grid(row=j, column=1)

		Label(frame, text="""\n\nChemistry Type:
			\n""").grid(row=0,column=2)
		k=0
		for txt, val in chemistry:
			k+=1
			Radiobutton(frame, text=txt,variable=self.chem,
				value=val).grid(row=k, column=2)

		i = max(max(i,j),k)+1

		Label(frame, text="""\n\nNumber of Cells:
			\n""").grid(row=i, column=0)
		Scale(frame, from_=20, to=500, resolution=10,
			variable=self.cell_count, orient=HORIZONTAL,
			label="20               500").grid(row=i+1,column=0)

		Label(frame, text="""\n\nNumber of Product Types:
			\n""").grid(row=i, column=1)
		Scale(frame, from_=2, to=9,variable=self.product_count,
			orient=HORIZONTAL,
			label="2                     9").grid(row=i+1, column=1)

		Label(frame, text="""\n\nNumber of Rule Instances:
			\n""").grid(row=i, column=2)
		Scale(frame, from_=100, to=500, resolution=10,
			variable=self.rule_count, orient=HORIZONTAL,
			label="100              500").grid(row=i+1,column=2)

		i +=2

		Label(frame, text="""\n\nTopology:\n""").grid(row=i,column=0)
		k=i
		for txt, val in topology:
			k+=1
			Radiobutton(frame, text=txt, variable=self.topo,
				value=val,command=self.topo_check).grid(row=k, column=0)


		Label(frame, text="""\n\nMobile Cells?:\n""").grid(row=i, column=1)
		Checkbutton(frame, variable=self.mobile,
			command=self.mobile_check).grid(row=i+1,column=1)

		Label(frame, text="""\n\nFraction of Run w/o Graphics:
			\n""").grid(row=i, column=2)
		Scale(frame, from_=0, to=1, resolution=.05,
			variable=self.fract_headless, orient=HORIZONTAL,
			label="0                      1").grid(row=i+1,column=2)


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

	def get_parameters(self):
		self.border.set(int(self.screen_height.get()*.06))
		x = int((self.screen_width.get()*.68)/float(self.space_width.get()))
		self.x_scaling.set(x)

		y = int((self.screen_height.get()*.89)/float(self.space_height.get()))
		self.y_scaling.set(y)
		return ({"URN_TYPE": self.urn.get(), 
			"REPRO": self.repro.get(),
			"CHEM": self.chem.get(),
			"TYPES": self.product_count.get(),
			"CELL_COUNT": self.cell_count.get(),
			"RULE_COUNT": self.rule_count.get(),
			"TOPO":self.topo.get(),
			"MOBILE": self.mobile.get(),
			"FRACT_HEADLESS": self.fract_headless.get(),
			"SCREEN_WIDTH":self.screen_width.get(),
			"SCREEN_HEIGHT":self.screen_height.get(),
			"SPACE_WIDTH":self.space_width.get(),
			"SPACE_HEIGHT":self.space_height.get(),
			"BORDER":self.border.get(),
			"X_SCALING": self.x_scaling.get(),
			"Y_SCALING": self.y_scaling.get()})

	def quit(self):
		self.master.destroy()

class Gatherer:

	def __init__(self, VARS):
		self.root = Tk()
		self.VARS = VARS
		self.root.title("Basic Autocatalysis Parameters")
		app=Parameter_App(self.root)
		self.root.mainloop()
		self.set_variables(app)

	def set_variables(self,app):
		variables = app.get_parameters()
		for var, val in variables.items():
			self.VARS.set_var(var,val)
		self.VARS.set_verts()





