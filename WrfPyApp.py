import tkinter as tk
from tkinter import filedialog,messagebox
from tkinter import ttk
from wrf import (to_np,interplevel, getvar, smooth2d, get_cartopy, cartopy_xlim,get_basemap,
                 cartopy_ylim, latlon_coords)
from netCDF4 import Dataset
from tkinter import simpledialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
class WrfPyApp:
    def __init__(self, master):

        menubar = tk.Menu(window)
        window.config(menu=menubar)
        file = tk.Menu(menubar)
        menubar.add_cascade(label="file", menu=file)
        file.add_command(label="new file", command=self.chooseData)

        self.Header = False
        self.contourLevelsBool = False
        self.pal = "jet"
        self.timeidx = 0
        self.list = []

        # FRAMES
        frame_left = tk.Frame(window, width=300, height=640, bg="grey")
        frame_left.grid(row=0, column=0, padx=2, pady=2)
        frame_mid = tk.Frame(window, width=540, height=640, bg="grey")
        frame_mid.grid(row=0, column=1, padx=2, pady=2)
      # frame_right = tk.Frame(window, width=300, height=640, bg="blue")
      # frame_right.grid(row=0, column=2, padx=2, pady=2)

        frame1 = tk.LabelFrame(frame_mid, width=540, height=500, bg="grey")
        frame1.grid(row=0, column=0, padx=2, pady=2)
        frame2 = tk.LabelFrame(frame_mid, width=540, height=140, bg="yellow")
        frame2.grid(row=1, column=0, padx=2, pady=2)

        # Buttons
        self.frame = frame1
        self.button_left = tk.Button(frame1,text="< Decrease TimeStep",command=self.decrease,state=tk.DISABLED,bg="gray70")
        self.button_left.grid(row=2,column=0)
        self.button_mid = tk.Button(frame1,text="Draw",command=self.draw,state=tk.DISABLED,bg="gray70")
        self.button_mid.grid(row=2,column=1)
        self.button_right = tk.Button(frame1, text="Increase TimeStep >", command=self.increase,state=tk.DISABLED,bg="gray70")
        self.button_right.grid(row=2, column=2)

        #Figure
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)

        self.LabelTimeStep = tk.Label(frame_left, text="TimeStep")
        self.LabelTimeStep.grid(row=0, column=0)
        #TimeStep Entry
        self.entryTimeStep = tk.Entry(frame_left,width = 10)
        self.entryTimeStep.insert(string="Timestep",index=0)
        self.entryTimeStep.grid(row=1,column = 0)

        self.LabelVariable = tk.Label(frame_left, text="Variable")
        self.LabelVariable.grid(row=2, column=0)

        self.variables = tk.StringVar()
        self.comboVariableBox = ttk.Combobox(frame_left, textvariable=self.variables,
                                     values=("slp","pressure", "tc", "ctt", "rh","rh2","pw", "cloudfrac","helicity","updraft_helicity", "cape_2d","dbz", "mdbz","avo","pvo","omega","eth","th","tv","ter","UaVa"),
                                     state="readonly")
        self.comboVariableBox.grid(row=3, column=0)
        self.ComboButton = tk.Button(frame_left, text="Choose", height=2, width=10, command=self.comboVariableBoxFunction,bg="gray70") #state=tk.DISABLED)
        self.ComboButton.grid(row=4, column=0)

        # RadioButton
        self.radioButton2 = tk.Button(frame_left, text="Choose", height=2, width=10, command=self.radioButtonFunction2,bg="gray70",
                                      state=tk.DISABLED)
        self.radioButton2.grid(row=9, column=0)

        # Palette Entry
        self.paletteButton = tk.Button(master=frame2, text="Pal Choose", height=2, width=10,
                                       command=self.paletteButtonFunction,bg="gray70")
        self.paletteButton.grid(row=1, column=0)

        self.drawMethods = tk.StringVar()  # For Adding String
        tk.Radiobutton(frame_left, text="contour" , value="1", height=2, width=8, variable=self.drawMethods).grid(row=5, column=0)
        tk.Radiobutton(frame_left, text="shade", value="2", height=2, width=8, variable=self.drawMethods).grid(row=6, column=0)
        tk.Radiobutton(frame_left, text="Con & Shade", value="3", height=2, width=12, variable=self.drawMethods).grid(row=7, column=0)
        tk.Radiobutton(frame_left, text="U-V", value="4", height=2, width=8, variable=self.drawMethods).grid(row=8, column=0)

        # Level Entry
        self.entryContourLevel = tk.Entry(frame2, width=25)
        self.entryContourLevel.insert(string="Levels,Levels", index=0)
        self.entryContourLevel.grid(row=0, column=2)
        self.contourLevelButton = tk.Button(master=frame2,text="Level Choose", height=2, width=10, command=self.levelButtonFunction,bg="gray70")
        self.contourLevelButton.grid(row=1, column=2)

        # Palette Entry
        self.Palettes = tk.StringVar()
        self.comboBox = ttk.Combobox(frame2,textvariable = self.Palettes,values= ("jet","ocean","gist_earth","terrain","rainbow","gist_rainbow","gnuplot","gnuplot2","brg"
                                                                                  ,"viridis","plasma","inferno","nipy_spectral","gist_ncar",
                                                                                  "magma","cividis","CMRmap","cubehelix","flag","prism","gist_stern","twilight","twilight_shifted",
                                                                                  "PiYG","PRGn","BrBG","PuOr","RdGy","RdBu","RdYlBu","hsv",
                                                                                  "RdYlGn","coolwarm","bwr","seismic"),state="readonly")
        self.comboBox.grid(row=0, column=0)
        self.paletteButton = tk.Button(master=frame2, text="Pal Choose", height=2, width=10,command=self.paletteButtonFunction,bg="gray70")
        self.paletteButton.grid(row=1, column=0)

        #Empty Lines For Grids
        self.LabelLeftUst = tk.Label(frame2, text="-------")
        self.LabelLeftUst.grid(row=0, column=1)
        self.LabelLeftAlt = tk.Label(frame2, text="-------")
        self.LabelLeftAlt.grid(row=1, column=1)

        self.LabelMidUst = tk.Label(frame2, text="-------")
        self.LabelMidUst.grid(row=0, column=3)
        self.LabelMidAlt = tk.Label(frame2, text="-------")
        self.LabelMidAlt.grid(row=1, column=3)

        self.LabelRightUst = tk.Label(frame2, text="-------")
        self.LabelRightUst.grid(row=0, column=5)
        self.LabelRightAlt = tk.Label(frame2, text="-------")
        self.LabelRightAlt.grid(row=1, column=5)

        #Save Button
        self.saveButton = tk.Button(master= frame2,text="Save Figure!", height=2, width=10,command = self.saveButtonFunction,bg="gray70")
        self.saveButton.grid(row=1,column = 6)

        # Header Entry
        self.entryHeader = tk.Entry(frame2, width=15)
        self.entryHeader.insert(string="Header", index=0)
        self.entryHeader.grid(row=0, column=4)

        # Header Fontsize
        self.entryHeaderFontSize = tk.Entry(frame2, width=15)
        self.entryHeaderFontSize.insert(string="Header FontSize", index=0)
        self.entryHeaderFontSize.grid(row=1, column=4)

        # Header Button
        self.headerButton = tk.Button(frame2, text="Header Plot", height=2, width=10, command=self.headerButtonFunction,bg="gray70")
        self.headerButton.grid(row=2, column=4)

        # Cizim #
        self.emptyDraw()
    def chooseData(self):
        self.path = filedialog.askopenfilename(title="select a file", initialdir="/home/onurhdogan/Downloads/wrf_veri/vdfcreatedeneme")
    def emptyDraw(self):
        self.canvas = FigureCanvasTkAgg(self.fig, master= self.frame) #master)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=1)
        self.frame.grid(row=0, column=0)  # pack()
        self.chooseData()
    def comboVariableBoxFunction(self):
        self.variable = self.variables.get()
        print("radioButtonVariable : ", self.variable)

        value = self.entryTimeStep.get()
        print("value: ", value)
        self.timeidx = int(value)
        if self.radioButton2['state'] == tk.DISABLED:
            print("buton2 kısmındayim")
            self.radioButton2['state'] = tk.NORMAL
    def radioButtonFunction2(self):
        self.drawMethod = self.drawMethods.get()
        print("radioButton2Variable : ", self.drawMethod)
        if self.button_mid['state'] == tk.DISABLED:
            print("buton3 kısmındayim")
            self.button_mid['state'] = tk.NORMAL
    def levelButtonFunction(self):
        if len(self.entryContourLevel.get()) != 0:
            self.list = []
            myStr = self.entryContourLevel.get().split(",")
            for i in myStr:
                self.list.append(i)
            self.contourLevelsBool = True
        if len(self.entryContourLevel.get()) == 0:
            self.contourLevelsBool = False
            self.list == []
    def paletteButtonFunction(self):
        self.pal = self.Palettes.get()
    def saveButtonFunction(self):
        self.savePath = filedialog.askdirectory(title="select a directory", initialdir="/home/onurhdogan/Desktop")
        self.fileName = simpledialog.askstring("Input","File Name.(pdf or png)",parent=window)
        self.type     = simpledialog.askstring("Input","Type(pdf,png)",parent=window)
        self.dpi      = simpledialog.askinteger("Input", "Quality", parent=window)
        self.fig.savefig(self.savePath+"/"+self.fileName,type=self.type,dpi=self.dpi)
    def headerButtonFunction(self):
        self.Header = True
        self.header = self.entryHeader.get()
        self.headerFontsize = self.entryHeaderFontSize.get()
        if self.headerFontsize == "Header FontSize":
            self.headerFontsize = 16

        print("self.header : ", self.header)
        print("self.headerFontsize : ", self.headerFontsize)
    def decrease(self):
        try :
            self.ax.clear()
        except AttributeError:
            pass

        if len(self.fig.axes) >= 2:
            self.fig.delaxes(self.fig.axes[1])

        if len(self.fig.axes) >= 1:
            self.fig.delaxes(self.fig.axes[0])

        self.ax = self.fig.add_subplot(111)


        if self.timeidx == 0:
            print("Kucuk Zaman Adımı")
        else:
            self.timeidx -= 1
            file = Dataset(str(self.path))
            # Get the sea level pressure
            if self.variable == "cloudfrac":
                self.i = simpledialog.askinteger("Input", "Cloud Level(0-2",
                                                 parent=window)  # messagebox.Dialog()   #askquestion("Question","Which level of Clouds")
                slp = getvar(file, "cloudfrac", timeidx=self.timeidx)[int(self.i), :, :]
                smooth_slp = smooth2d(slp, 3, cenweight=4)
                # Get the latitude and longitude points
                lats, lons = latlon_coords(slp)
                bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)

                # Add geographic outlines
                bm.drawcoastlines(linewidth=0.25)
                bm.drawstates(linewidth=0.25)
                bm.drawcountries(linewidth=0.25)
                x, y = bm(to_np(lons), to_np(lats))
            elif self.variable == "cape_2d":
                self.i = simpledialog.askinteger("Input", "Type(0:mcape,1:mcin,2:LCL,3:lfc)", parent=window)
                slp = getvar(file, "cape_2d", timeidx=self.timeidx)[int(self.i), :, :]
                smooth_slp = smooth2d(slp, 3, cenweight=4)
                # Get the latitude and longitude points
                lats, lons = latlon_coords(slp)
                bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
                # Add geographic outlines
                bm.drawcoastlines(linewidth=0.25)
                bm.drawstates(linewidth=0.25)
                bm.drawcountries(linewidth=0.25)
                x, y = bm(to_np(lons), to_np(lats))
            elif self.variable == "slp":
                slp = getvar(file, "slp", timeidx=self.timeidx)
                smooth_slp = smooth2d(slp, 3, cenweight=4)
                # Get the latitude and longitude points
                lats, lons = latlon_coords(slp)
                bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
                # Add geographic outlines
                bm.drawcoastlines(linewidth=0.25)
                bm.drawstates(linewidth=0.25)
                bm.drawcountries(linewidth=0.25)
                x, y = bm(to_np(lons), to_np(lats))
            elif self.variable == "helicity":
                slp = getvar(file, "helicity", timeidx=self.timeidx)
                smooth_slp = smooth2d(slp, 3, cenweight=4)
                # Get the latitude and longitude points
                lats, lons = latlon_coords(slp)
                bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
                # Add geographic outlines
                bm.drawcoastlines(linewidth=0.25)
                bm.drawstates(linewidth=0.25)
                bm.drawcountries(linewidth=0.25)
                x, y = bm(to_np(lons), to_np(lats))
            elif self.variable == "updraft_helicity":
                slp = getvar(file, "updraft_helicity", timeidx=self.timeidx)
                smooth_slp = smooth2d(slp, 3, cenweight=4)
                # Get the latitude and longitude points
                lats, lons = latlon_coords(slp)
                bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
                # Add geographic outlines
                bm.drawcoastlines(linewidth=0.25)
                bm.drawstates(linewidth=0.25)
                bm.drawcountries(linewidth=0.25)
                x, y = bm(to_np(lons), to_np(lats))
            elif self.variable == "pressure":
                self.i = simpledialog.askinteger("Input", "Height Level(0-MaxLev)", parent=window)
                slp = getvar(file, "pressure", timeidx=self.timeidx)[int(self.i), :, :]
                smooth_slp = smooth2d(slp, 3, cenweight=4)
                # Get the latitude and longitude points
                lats, lons = latlon_coords(slp)
                bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
                # Add geographic outlines
                bm.drawcoastlines(linewidth=0.25)
                bm.drawstates(linewidth=0.25)
                bm.drawcountries(linewidth=0.25)
                x, y = bm(to_np(lons), to_np(lats))
            elif self.variable == "dbz":
                self.i = simpledialog.askinteger("Input", "Height Level(0-MaxLev)", parent=window)
                slp = getvar(file, "dbz", timeidx=self.timeidx)[int(self.i), :, :]
                smooth_slp = smooth2d(slp, 3, cenweight=4)
                # Get the latitude and longitude points
                lats, lons = latlon_coords(slp)
                bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
                # Add geographic outlines
                bm.drawcoastlines(linewidth=0.25)
                bm.drawstates(linewidth=0.25)
                bm.drawcountries(linewidth=0.25)
                x, y = bm(to_np(lons), to_np(lats))
            elif self.variable == "tv":
                slp = getvar(file, "th", timeidx=self.timeidx, units=self.j)[int(self.i), :, :]
                smooth_slp = smooth2d(slp, 3, cenweight=4)
                # Get the latitude and longitude points
                lats, lons = latlon_coords(slp)
                bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
                # Add geographic outlines
                bm.drawcoastlines(linewidth=0.25)
                bm.drawstates(linewidth=0.25)
                bm.drawcountries(linewidth=0.25)
                x, y = bm(to_np(lons), to_np(lats))
            elif self.variable == "mdbz":
                slp = getvar(file, "mdbz", timeidx=self.timeidx)
                smooth_slp = smooth2d(slp, 3, cenweight=4)
                # Get the latitude and longitude points
                lats, lons = latlon_coords(slp)
                bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
                # Add geographic outlines
                bm.drawcoastlines(linewidth=0.25)
                bm.drawstates(linewidth=0.25)
                bm.drawcountries(linewidth=0.25)
                x, y = bm(to_np(lons), to_np(lats))
            elif self.variable == "pvo":
                slp = getvar(file, "pvo", timeidx=self.timeidx)[int(self.i), :, :]
                smooth_slp = smooth2d(slp, 3, cenweight=4)
                # Get the latitude and longitude points
                lats, lons = latlon_coords(slp)
                bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
                # Add geographic outlines
                bm.drawcoastlines(linewidth=0.25)
                bm.drawstates(linewidth=0.25)
                bm.drawcountries(linewidth=0.25)
                x, y = bm(to_np(lons), to_np(lats))
            elif self.variable == "rh":
                slp = getvar(file, "rh", timeidx=self.timeidx)[int(self.i), :, :]
                smooth_slp = smooth2d(slp, 3, cenweight=4)
                # Get the latitude and longitude points
                lats, lons = latlon_coords(slp)
                bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
                # Add geographic outlines
                bm.drawcoastlines(linewidth=0.25)
                bm.drawstates(linewidth=0.25)
                bm.drawcountries(linewidth=0.25)
                x, y = bm(to_np(lons), to_np(lats))
            elif self.variable == "rh2":
                slp = getvar(file, "rh2", timeidx=self.timeidx)
                smooth_slp = smooth2d(slp, 3, cenweight=4)
                # Get the latitude and longitude points
                lats, lons = latlon_coords(slp)
                bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
                # Add geographic outlines
                bm.drawcoastlines(linewidth=0.25)
                bm.drawstates(linewidth=0.25)
                bm.drawcountries(linewidth=0.25)
                x, y = bm(to_np(lons), to_np(lats))
            elif self.variable == "omega":
                slp = getvar(file, "omega", timeidx=self.timeidx)[int(self.i), :, :]
                smooth_slp = smooth2d(slp, 3, cenweight=4)
                # Get the latitude and longitude points
                lats, lons = latlon_coords(slp)
                bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
                # Add geographic outlines
                bm.drawcoastlines(linewidth=0.25)
                bm.drawstates(linewidth=0.25)
                bm.drawcountries(linewidth=0.25)
                x, y = bm(to_np(lons), to_np(lats))
            elif self.variable == "pw":
                slp = getvar(file, "pw", timeidx=self.timeidx)
                smooth_slp = smooth2d(slp, 3, cenweight=4)
                # Get the latitude and longitude points
                lats, lons = latlon_coords(slp)
                bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
                # Add geographic outlines
                bm.drawcoastlines(linewidth=0.25)
                bm.drawstates(linewidth=0.25)
                bm.drawcountries(linewidth=0.25)
                x, y = bm(to_np(lons), to_np(lats))
            elif self.variable == "ctt":
                slp = getvar(file, "ctt", timeidx=self.timeidx)
                smooth_slp = smooth2d(slp, 3, cenweight=4)
                # Get the latitude and longitude points
                lats, lons = latlon_coords(slp)
                bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
                # Add geographic outlines
                bm.drawcoastlines(linewidth=0.25)
                bm.drawstates(linewidth=0.25)
                bm.drawcountries(linewidth=0.25)
                x, y = bm(to_np(lons), to_np(lats))
            elif self.variable == "tc":
                slp = getvar(file, "tc", timeidx=self.timeidx)[int(self.i), :, :]
                smooth_slp = smooth2d(slp, 3, cenweight=4)
                # Get the latitude and longitude points
                lats, lons = latlon_coords(slp)
                bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
                # Add geographic outlines
                bm.drawcoastlines(linewidth=0.25)
                bm.drawstates(linewidth=0.25)
                bm.drawcountries(linewidth=0.25)
                x, y = bm(to_np(lons), to_np(lats))
            elif self.variable == "eth":
                self.i = simpledialog.askinteger("Input", "Height Level(0-MaxLev)", parent=window)
                self.j = simpledialog.askstring("Input", "Unit: 'degC','K' or 'degF'", parent=window)
                slp = getvar(file, "eth", timeidx=self.timeidx, units=self.j)[int(self.i), :, :]
                smooth_slp = smooth2d(slp, 3, cenweight=4)
                # Get the latitude and longitude points
                lats, lons = latlon_coords(slp)
                bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
                # Add geographic outlines
                bm.drawcoastlines(linewidth=0.25)
                bm.drawstates(linewidth=0.25)
                bm.drawcountries(linewidth=0.25)
                x, y = bm(to_np(lons), to_np(lats))
            elif self.variable == "th":
                slp = getvar(file, "th", timeidx=self.timeidx, units=self.j)[int(self.i), :, :]
                smooth_slp = smooth2d(slp, 3, cenweight=4)
                # Get the latitude and longitude points
                lats, lons = latlon_coords(slp)
                bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
                # Add geographic outlines
                bm.drawcoastlines(linewidth=0.25)
                bm.drawstates(linewidth=0.25)
                bm.drawcountries(linewidth=0.25)
                x, y = bm(to_np(lons), to_np(lats))
            elif self.variable == "avo":
                self.i = simpledialog.askinteger("Input", "Height Level(0-MaxLev)", parent=window)
                slp = getvar(file, "avo", timeidx=self.timeidx)[int(self.i), :, :]
                smooth_slp = smooth2d(slp, 3, cenweight=4)
                # Get the latitude and longitude points
                lats, lons = latlon_coords(slp)
                bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
                # Add geographic outlines
                bm.drawcoastlines(linewidth=0.25)
                bm.drawstates(linewidth=0.25)
                bm.drawcountries(linewidth=0.25)
                x, y = bm(to_np(lons), to_np(lats))
            elif self.variable == "UaVa":
                self.i = simpledialog.askinteger("Input", "Geo Height", parent=window)
                self.j = simpledialog.askstring("Input", "Unit: 'kt' or 'ms-1'", parent=window)
                P = getvar(file, "pressure")
                Z = getvar(file, "z")
                U = getvar(file, "ua", units=self.j)
                V = getvar(file, "va", units=self.j)

                GPint = interplevel(Z, P, self.i)
                Uint = interplevel(U, P, self.i)
                Vint = interplevel(V, P, self.i)
                lats, lons = latlon_coords(P)
                # Get the basemap object
                bm = get_basemap(GPint, ax=self.ax, resolution='l')
                # Add geographic outlines
                bm.drawcoastlines(linewidth=0.25)
                bm.drawstates(linewidth=0.25)
                bm.drawcountries(linewidth=0.25)
                # Convert the lats and lons to x and y.  Make sure you convert the lats and lons to numpy arrays via to_np, or basemap crashes with an undefined
                x, y = bm(to_np(lons), to_np(lats))
            elif self.variable == "ter":
                pass

            if self.drawMethod == "1":
                if self.contourLevelsBool == False:
                    bm.contour(x, y, to_np(smooth_slp), 10, colors="black")
                else:
                    bm.contour(x, y, to_np(smooth_slp), 10, levels=self.list, colors="black")
            elif self.drawMethod == "2":
                if self.contourLevelsBool == False:
                    s = bm.contourf(x, y, to_np(smooth_slp), 10, cmap=get_cmap(self.pal))
                    self.fig.colorbar(s, ax=self.ax, orientation="horizontal", shrink=0.72)
                else:
                    s = bm.contourf(x, y, to_np(smooth_slp), 10, levels=self.list, cmap=get_cmap(self.pal))
                    self.fig.colorbar(s, ax=self.ax, orientation="horizontal", shrink=0.72)
            elif self.drawMethod == "3":
                if self.contourLevelsBool == False:
                    bm.contour(x, y, to_np(smooth_slp), 10, colors="black")
                    s = bm.contourf(x, y, to_np(smooth_slp), 10, cmap=get_cmap(self.pal))
                    self.cb = self.fig.colorbar(s, ax=self.ax, orientation="horizontal", shrink=0.72)
                else:
                    bm.contour(x, y, to_np(smooth_slp), 10, levels=self.list, colors="black")
                    s = bm.contourf(x, y, to_np(smooth_slp), 10, levels=self.list, cmap=get_cmap(self.pal))
                    self.cb = self.fig.colorbar(s, ax=self.ax, orientation="horizontal", shrink=0.72)
            elif self.drawMethod == "4":
                bm.barbs(x[::45, ::45], y[::45, ::45], to_np(Uint[::45, ::45]), to_np(Vint[::45, ::45]), length=6)

            self.timeLabel1 = tk.Label(self.frame, text="TimeStep :")
            self.timeLabel1.grid(row=0, column=2)
            self.timeLabel2 = tk.Label(self.frame, text=self.timeidx)
            self.timeLabel2.grid(row=1, column=2)

            self.canvas.draw()
            self.canvas.get_tk_widget().grid(row=0, column=1)
            self.frame.grid(row=0, column=0)  # pack()
    def increase(self):
        try:
            self.ax.clear()
        except AttributeError:
            pass

        if len(self.fig.axes) >= 2:
            self.fig.delaxes(self.fig.axes[1])

        if len(self.fig.axes) >= 1:
            self.fig.delaxes(self.fig.axes[0])

        self.ax = self.fig.add_subplot(111)

        self.timeidx += 1
        file = Dataset(str(self.path))
        # Get the sea level pressure
        if self.variable == "cloudfrac":
            self.i = simpledialog.askinteger("Input", "Cloud Level(0-2",
                                             parent=window)  # messagebox.Dialog()   #askquestion("Question","Which level of Clouds")
            slp = getvar(file, "cloudfrac", timeidx=self.timeidx)[int(self.i), :, :]
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)

            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "cape_2d":
            self.i = simpledialog.askinteger("Input", "Type(0:mcape,1:mcin,2:LCL,3:lfc)", parent=window)
            slp = getvar(file, "cape_2d", timeidx=self.timeidx)[int(self.i), :, :]
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "slp":
            slp = getvar(file, "slp", timeidx=self.timeidx)
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "helicity":
            slp = getvar(file, "helicity", timeidx=self.timeidx)
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "updraft_helicity":
            slp = getvar(file, "updraft_helicity", timeidx=self.timeidx)
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "tv":
            slp = getvar(file, "th", timeidx=self.timeidx,units = self.j)[int(self.i), :, :]
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "pressure":
            self.i = simpledialog.askinteger("Input", "Height Level(0-MaxLev)", parent=window)
            slp = getvar(file, "pressure", timeidx=self.timeidx)[int(self.i), :, :]
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "dbz":
            self.i = simpledialog.askinteger("Input", "Height Level(0-MaxLev)", parent=window)
            slp = getvar(file, "dbz", timeidx=self.timeidx)[int(self.i), :, :]
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "rh":
            slp = getvar(file, "rh", timeidx=self.timeidx)[int(self.i), :, :]
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "pw":
            slp = getvar(file, "pw", timeidx=self.timeidx)
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "pvo":
            slp = getvar(file, "pvo", timeidx=self.timeidx)[int(self.i), :, :]
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "mdbz":
            slp = getvar(file, "mdbz", timeidx=self.timeidx)
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "rh2":
            slp = getvar(file, "rh2", timeidx=self.timeidx)
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "omega":
            slp = getvar(file, "omega", timeidx=self.timeidx)[int(self.i), :, :]
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "ctt":
            slp = getvar(file, "ctt", timeidx=self.timeidx)
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "tc":
            slp = getvar(file, "tc", timeidx=self.timeidx)[int(self.i), :, :]
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "eth":
            self.i = simpledialog.askinteger("Input", "Height Level(0-MaxLev)", parent=window)
            self.j = simpledialog.askstring("Input", "Unit: 'degC','K' or 'degF'", parent=window)
            slp = getvar(file, "eth", timeidx=self.timeidx, units=self.j)[int(self.i), :, :]
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "th":
            slp = getvar(file, "th", timeidx=self.timeidx,units = self.j)[int(self.i), :, :]
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "avo":
            self.i = simpledialog.askinteger("Input", "Height Level(0-MaxLev)", parent=window)
            slp = getvar(file, "avo", timeidx=self.timeidx)[int(self.i), :, :]
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "UaVa":
            self.i = simpledialog.askinteger("Input", "Geo Height", parent=window)
            self.j = simpledialog.askstring("Input", "Unit: 'kt' or 'ms-1'", parent=window)
            P = getvar(file, "pressure")
            Z = getvar(file, "z")
            U = getvar(file, "ua", units=self.j)
            V = getvar(file, "va", units=self.j)

            GPint = interplevel(Z, P, self.i)
            Uint = interplevel(U, P, self.i)
            Vint = interplevel(V, P, self.i)
            lats, lons = latlon_coords(P)
            # Get the basemap object
            bm = get_basemap(GPint, ax=self.ax, resolution='l')
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            # Convert the lats and lons to x and y.  Make sure you convert the lats and lons to numpy arrays via to_np, or basemap crashes with an undefined
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "ter":
            pass

        if self.drawMethod == "1":
            if self.contourLevelsBool == False:
                bm.contour(x, y, to_np(smooth_slp), 10, colors="black")
            else:
                bm.contour(x, y, to_np(smooth_slp), 10, levels=self.list, colors="black")
        elif self.drawMethod == "2":
            if self.contourLevelsBool == False:
                s = bm.contourf(x, y, to_np(smooth_slp), 10, cmap=get_cmap(self.pal))
                self.fig.colorbar(s, ax=self.ax, orientation="horizontal", shrink=0.72)
            else:
                s = bm.contourf(x, y, to_np(smooth_slp), 10, levels=self.list, cmap=get_cmap(self.pal))
                self.fig.colorbar(s, ax=self.ax, orientation="horizontal", shrink=0.72)
        elif self.drawMethod == "3":
            if self.contourLevelsBool == False:
                bm.contour(x, y, to_np(smooth_slp), 10, colors="black")
                s = bm.contourf(x, y, to_np(smooth_slp), 10, cmap=get_cmap(self.pal))
                self.cb = self.fig.colorbar(s, ax=self.ax, orientation="horizontal", shrink=0.72)
            else:
                bm.contour(x, y, to_np(smooth_slp), 10, levels=self.list, colors="black")
                s = bm.contourf(x, y, to_np(smooth_slp), 10, levels=self.list, cmap=get_cmap(self.pal))
                self.cb = self.fig.colorbar(s, ax=self.ax, orientation="horizontal", shrink=0.72)
        elif self.drawMethod == "4":
            bm.barbs(x[::45, ::45], y[::45, ::45], to_np(Uint[::45, ::45]), to_np(Vint[::45, ::45]), length=6)

        if self.Header == True:
            self.fig.axes[0].set_title(self.header, fontsize=self.headerFontsize)

        self.timeLabel1 = tk.Label(self.frame, text="TimeStep :")
        self.timeLabel1.grid(row=0, column=2)
        self.timeLabel2 = tk.Label(self.frame, text=self.timeidx)
        self.timeLabel2.grid(row=1, column=2)

        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=1)
        self.frame.grid(row=0, column=0)  # pack()
    def draw(self):

        if len(self.fig.axes) >= 2 :
            self.fig.delaxes(self.fig.axes[1])

        if len(self.fig.axes) >= 1 :
            self.fig.delaxes(self.fig.axes[0])

        self.ax = self.fig.add_subplot(111)

        file = Dataset(str(self.path))
        if self.variable == "cloudfrac":
            self.i = simpledialog.askinteger("Input","Cloud Level(0-2",parent=window) #messagebox.Dialog()   #askquestion("Question","Which level of Clouds")
            slp = getvar(file, "cloudfrac", timeidx=self.timeidx)[int(self.i),:,:]
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution = 'l', area_thresh = 1000)

            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "cape_2d":
            self.i = simpledialog.askinteger("Input", "Type(0:mcape,1:mcin,2:LCL,3:lfc)", parent=window)
            slp = getvar(file, "cape_2d", timeidx=self.timeidx)[int(self.i), :, :]
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "slp":
            slp = getvar(file, "slp", timeidx=self.timeidx)
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "pw":
            slp = getvar(file, "pw", timeidx=self.timeidx)
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "helicity":
            slp = getvar(file, "helicity", timeidx=self.timeidx)
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "updraft_helicity":
            slp = getvar(file, "updraft_helicity", timeidx=self.timeidx)
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "pressure":
            self.i = simpledialog.askinteger("Input", "Height Level(0-MaxLev)",parent=window)
            slp = getvar(file, "pressure", timeidx=self.timeidx)[int(self.i), :, :]
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "dbz":
            self.i = simpledialog.askinteger("Input", "Height Level(0-MaxLev)",parent=window)
            slp = getvar(file, "dbz", timeidx=self.timeidx)[int(self.i), :, :]
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "mdbz":
            slp = getvar(file, "mdbz", timeidx=self.timeidx)
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "rh":
            self.i = simpledialog.askinteger("Input", "Height Level(0-MaxLev)",parent=window)
            slp = getvar(file, "rh", timeidx=self.timeidx)[int(self.i), :, :]
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "rh2":
            slp = getvar(file, "rh2", timeidx=self.timeidx)
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "ter":
            slp = getvar(file, "ter", timeidx=self.timeidx,units="m")
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "omega":
            self.i = simpledialog.askinteger("Input", "Height Level(0-MaxLev)", parent=window)
            slp = getvar(file, "omega", timeidx=self.timeidx)[int(self.i), :, :]
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "pvo":
            self.i = simpledialog.askinteger("Input", "Height Level(0-MaxLev)", parent=window)
            slp = getvar(file, "pvo", timeidx=self.timeidx)[int(self.i), :, :]
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "ctt":
            slp = getvar(file, "ctt", timeidx=self.timeidx)
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "tc":
            self.i = simpledialog.askinteger("Input", "Height Level(0-MaxLev)", parent=window)
            slp = getvar(file, "tc", timeidx=self.timeidx)[int(self.i), :, :]
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "eth":
            self.i = simpledialog.askinteger("Input", "Height Level(0-MaxLev)", parent=window)
            self.j = simpledialog.askstring("Input", "Unit: 'degC','K' or 'degF'", parent=window)
            slp = getvar(file, "eth", timeidx=self.timeidx,units = self.j)[int(self.i), :, :]
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "tv":
            self.i = simpledialog.askinteger("Input", "Height Level(0-MaxLev)", parent=window)
            self.j = simpledialog.askstring("Input", "Unit: 'degC','K' or 'degF'", parent=window)
            slp = getvar(file, "th", timeidx=self.timeidx,units = self.j)[int(self.i), :, :]
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "th":
            self.i = simpledialog.askinteger("Input", "Height Level(0-MaxLev)", parent=window)
            self.j = simpledialog.askstring("Input", "Unit: 'degC','K' or 'degF'", parent=window)
            slp = getvar(file, "th", timeidx=self.timeidx,units = self.j)[int(self.i), :, :]
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "avo":
            self.i = simpledialog.askinteger("Input", "Height Level(0-MaxLev)", parent=window)
            slp = getvar(file, "avo", timeidx=self.timeidx)[int(self.i), :, :]
            smooth_slp = smooth2d(slp, 3, cenweight=4)
            # Get the latitude and longitude points
            lats, lons = latlon_coords(slp)
            bm = get_basemap(slp, ax=self.ax, resolution='l', area_thresh=1000)
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            x, y = bm(to_np(lons), to_np(lats))
        elif self.variable == "UaVa":
            self.i = simpledialog.askinteger("Input", "Geo Height", parent=window)
            self.j = simpledialog.askstring("Input", "Unit: 'kt' or 'ms-1'", parent=window)
            P = getvar(file,"pressure")
            Z = getvar(file, "z")
            U = getvar(file,"ua",units = self.j)
            V = getvar(file,"va",units = self.j)

            GPint = interplevel(Z,P,self.i)
            Uint = interplevel(U,P,self.i)
            Vint = interplevel(V,P,self.i)
            lats, lons = latlon_coords(P)
            # Get the basemap object
            bm = get_basemap(GPint, ax=self.ax, resolution='l')
            # Add geographic outlines
            bm.drawcoastlines(linewidth=0.25)
            bm.drawstates(linewidth=0.25)
            bm.drawcountries(linewidth=0.25)
            # Convert the lats and lons to x and y.  Make sure you convert the lats and lons to numpy arrays via to_np, or basemap crashes with an undefined
            x, y = bm(to_np(lons), to_np(lats))

        if self.drawMethod == "1":
            if self.contourLevelsBool == False:
                bm.contour(x, y, to_np(smooth_slp), 10, colors="black")
            else :
                bm.contour(x, y, to_np(smooth_slp), 10,levels=self.list, colors="black")
        elif self.drawMethod == "2":
            if self.contourLevelsBool == False:
                s = bm.contourf(x, y, to_np(smooth_slp), 10, cmap=get_cmap(self.pal))
                self.fig.colorbar(s,ax=self.ax,orientation="horizontal",shrink = 0.72)
            else :
                s = bm.contourf(x, y, to_np(smooth_slp), 10, levels=self.list, cmap=get_cmap(self.pal))
                self.fig.colorbar(s, ax=self.ax, orientation="horizontal", shrink=0.72)
        elif self.drawMethod == "3":
            if self.contourLevelsBool == False:
                bm.contour(x, y, to_np(smooth_slp), 10, colors="black")
                s = bm.contourf(x, y, to_np(smooth_slp), 10, cmap=get_cmap("jet"))
                self.cb = self.fig.colorbar(s,ax=self.ax,orientation="horizontal",shrink = 0.72)
            else:
                bm.contour(x, y, to_np(smooth_slp), 10,levels=self.list, colors="black")
                s = bm.contourf(x, y, to_np(smooth_slp),10,levels=self.list, cmap=get_cmap("jet"))
                self.cb = self.fig.colorbar(s, ax=self.ax, orientation="horizontal", shrink=0.72)
        elif self.drawMethod == "4":
            bm.barbs(x[::45, ::45], y[::45, ::45], to_np(Uint[::45,::45]), to_np(Vint[::45,::45]), length=6)

        if self.Header == True:
            self.fig.axes[0].set_title(self.header, fontsize=self.headerFontsize)

        self.timeLabel1 = tk.Label(self.frame, text="TimeStep :")
        self.timeLabel1.grid(row=0, column=2)
        self.timeLabel2 = tk.Label(self.frame, text=self.timeidx)
        self.timeLabel2.grid(row=1, column=2)

        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=1)
        self.frame.grid(row=0, column=0)  # pack()

        if self.button_left['state'] == tk.DISABLED :
            self.button_left['state'] = tk.NORMAL
        if  self.button_right['state'] == tk.DISABLED:
            self.button_right['state'] = tk.NORMAL

window = tk.Tk()
window.title("WrfPyApp")
app = WrfPyApp(window)
window.mainloop()