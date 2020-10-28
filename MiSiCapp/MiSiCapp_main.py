import argparse 
import warnings

import os, sys
from pathlib import Path

from skimage.io import imsave,imread
import skimage.io
from skimage.measure import label

import tiffile as tiffile
import numpy as np

import napari
from napari.layers import Image
from magicgui import magicgui
from magicgui._qt.widgets import QDoubleSlider
from magicgui import event_loop, magicgui
from PyQt5.QtWidgets import QDoubleSpinBox
from PyQt5.QtCore import Qt

from MiSiC.MiSiC import *

#from MiSiCapp import *
#from utils_gui import *

gdict = {"gDir":"", "gfilename" : os.path.join("~", "out.tif"), "gdims" : None, "width" : None, "gnoise" : None, "ginvert" : None, "gpos" : None, "gsave_all" : None}
#thresh = 220

misic = MiSiC()

def main():
    with napari.gui_qt():
        viewer = napari.Viewer()

        def updatelayer(layer):
            viewer.layers[-1].metadata=gdict
            gui.refresh_choices("layer")
            viewer.layers[-1].metadata=gdict
            print("event", layer)

        def defaultpath(apath):
            global gdict    
            #viewer.add_image(tifffile.imread(apath))
            #print("avant",os.path.join(apath, viewer.layers[0].name))
            gdict["gDir"] = apath
            gdict["gfilename"] = os.path.join(apath, viewer.layers[0].name)
            #print("apres",gdict["gfilename"])
        
        def changelabels(thresh):
            #& ("seg" not in laynames)
            laynames = [ l.name for l in viewer.layers]
            if ('seg' in laynames):
                i = laynames.index("seg")
                viewer.layers.pop(i)

            if ('image_mask result' in laynames)  :
                im = viewer.layers['image_mask result'].data > (thresh)
                label_image = label(im)
                viewer.add_labels(label_image, name="seg")



        @magicgui(call_button="get_mask", noise={"fixedWidth": 50}, layout="vertical")
        def image_mask(layer: Image, mean_width = 6, noise = "0.00", PhaseContrast = True, process_all = False) -> Image:
            global gdict
            p = tuple([int(round(x)) for x in viewer.dims.point])
            #print("pressed", viewer.layers)
            if process_all & (layer.data.ndim > 2) :
                if layer.data.ndim == 5 : img = layer.data[:, p[1], p[2],:,:]
                elif layer.data.ndim == 4 : img = layer.data[:, p[1],:,:]
                elif layer.data.ndim == 3 : img = layer.data[:,:,:]
                else: img = layer.data
                gdict["gfilename"] = os.path.join(gdict["gDir"], layer.name)
                gdict["gdims"] = layer.data.shape
                gdict["width"] = mean_width
                gdict["gnoise"] = noise
                gdict["ginvert"] = PhaseContrast
                gdict["gpos"] = p
                gdict["gsave_all"] = process_all

                updatemeta(gdict, 0)
                return seg_img(img, scale=round(10/mean_width, 2), noise=noise, invert=PhaseContrast, frame = viewer.dims.point[0], save=process_all)

            else:
                if layer.data.ndim == 5 : img = layer.data[p[0], p[1], p[2],:,:]
                elif layer.data.ndim == 4 : img = layer.data[p[0], p[1],:,:]
                elif layer.data.ndim == 3 : img = layer.data[p[0],:,:]
                else: img = layer.data
                gdict["gfilename"] = os.path.join(gdict["gDir"], layer.name)
                gdict["gdims"] = layer.data.shape
                gdict["width"] = mean_width
                gdict["gnoise"] = noise
                gdict["ginvert"] = PhaseContrast
                gdict["gpos"] = p
                gdict["gsave_all"] = process_all

                updatemeta(gdict, 0)
                return seg_img(img, scale=round(10/mean_width, 2), noise=noise, invert=PhaseContrast, frame = viewer.dims.point[0], save=process_all)
        

        viewer.grid_view()
        # instantiate the widget
        gui = image_mask.Gui()
        # add our new widget to the napari viewer
        viewer.window.add_dock_widget(gui, area="right")
        
        # keep the dropdown menus in the gui in sync with the layer model
        #viewer.layers.events.changed.connect(lambda x: gui.refresh_choices("layer"))
        viewer.layers.events.changed.connect(updatelayer)

        #viewer.layers[1].metadata = viewer.layers[0].metadata

        #threshold = {'minimum':10, 'maximum':255}
        #, threshold = 220.00

        @magicgui(threshold = {'minimum':10, 'maximum':255})
        def make_labels(threshold = 220):
            return threshold

        @magicgui(filename={"mode": "existing_directory"})
        def filepicker(filename=Path("~")):
            #print("The filename is:", filename)
            #im = tifffile.imread(filename)
            return filename

        # instantiate the widget
        with event_loop():
            gui1 = make_labels.Gui(show = True)
            viewer.window.add_dock_widget(gui1, area="right")
            gui1.threshold_changed.connect(changelabels)

            gui2 = filepicker.Gui(show=True)
            viewer.window.add_dock_widget(gui2, area="right")
            gui2.filename_changed.connect(defaultpath)

        viewer.grid_view()
