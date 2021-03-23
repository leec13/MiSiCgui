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
#from magicgui._qt.widgets import QDoubleSlider
from magicgui import event_loop, magicgui

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from MiSiC.MiSiC import *
#import MiSiCgui

global
gdict = {"gDir":"", "gfilename" : os.path.join("~", "out.tif"), "gdims" : None, "width" : None, "gnoise" : None, "gthresh":220, "ginvert" : None, "gpos" : None, "gsave_all" : None}

misic = MiSiC()
viewer = None

def updatemeta(metadict = gdict, idx = 1):
    viewer.layers[idx].metadata = metadict


def seg_img(im, scale=1, noise="0.000", invert=True, frame=0, save=False, threshold=220):
    
    noise = float(noise)
    rtim = np.zeros(gdict["gdims"])
    p = gdict["gpos"]
    global thresh
    thresh = threshold

    if save:
        print("running...")
        hyperS = np.zeros(im.shape)
        for iT in range(im.shape[0]) :
            imp = im[iT,:,:]
            sr,sc = imp.shape
            imp = rescale(imp,scale)
            if noise > 0 : imp = random_noise(imp,mode = 'gaussian',var = noise)
            imp = normalize2max(imp)
            y1 = misic.segment(imp,invert = invert)
            y = np.zeros((sr,sc,2))
            y[:,:,0] = resize(rescale(y1[:,:,0],1.0/scale),(sr,sc))
            y[:,:,1] = resize(rescale(y1[:,:,1],1.0/scale),(sr,sc))
            if rtim.ndim == 3 : rtim[iT,:,:] = (y[:,:,0])
            elif rtim.ndim == 4 : rtim[iT,p[1],:,:] = (y[:,:,0])
            else: rtim[iT,p[1],p[2],:,:] = (y[:,:,0])
            hyperS[iT,:,:] =  (y[:,:,0])
            print("time = ", iT)
            #print("Finish")
            savestr = "all"
    
    else :
        print("running...")
        hyperS = np.zeros(im.shape)
        sr,sc = im.shape
        im = rescale(im,scale)
        if noise > 0 : im = random_noise(im, mode = 'gaussian', var = noise)
        im = normalize2max(im)
        y1 = misic.segment(im,invert = invert)
        y = np.zeros((sr,sc,2))
        y[:,:,0] = resize(rescale(y1[:,:,0],1.0/scale),(sr,sc))
        y[:,:,1] = resize(rescale(y1[:,:,1],1.0/scale),(sr,sc))
        if rtim.ndim == 2 : rtim[:,:] = (y[:,:,0])
        elif rtim.ndim == 3 : rtim[p[0],:,:] = (y[:,:,0])
        elif rtim.ndim == 4 : rtim[p[0],p[1],:,:] = (y[:,:,0])
        else: rtim[p[0],p[1],p[2],:,:] = (y[:,:,0])
        hyperS =  (y[:,:,0])
        savestr = str(frame)
    

    gshape = viewer.layers[-1].metadata["gdims"]
    gshape = "_".join([str(i) for i in gshape])

    width = str(gdict["width"])

    imsave(str(gdict["gfilename"])+"_W="+width+"_N="+str(noise)+"_DIM="+gshape+"_frame="+savestr+"_mask.tif",(255.0*hyperS).astype(np.uint8))
    print("Finish")
    return((255.0*hyperS).astype(np.uint8))

def main():
    with napari.gui_qt():
        global viewer
        viewer = napari.Viewer()

        def updatelayer(layer):
            viewer.layers[-1].metadata=gdict
            updatelayer.reset_choices("layer")
            viewer.layers[-1].metadata=gdict
            print("event", layer)

        def defaultpath(event_apath):
            apath = filepicker.filename.value
            #viewer.add_image(tifffile.imread(apath))
            #print("avant",os.path.join(apath, viewer.layers[0].name))
            gdict["gDir"] = apath
            if len(viewer.layers) > 0 :

            gdict["gfilename"] = os.path.join(apath, viewer.layers[0].name)
            #print("apres",gdict["gfilename"])
        
        def changelabels(event_thr):
            #& ("seg" not in laynames)
            print(make_labels.threshold.value)
            thresh = make_labels.threshold.value
            laynames = [ l.name for l in viewer.layers]
            if ('seg' in laynames):
                i = laynames.index("seg")
                viewer.layers.pop(i)

            if ('image_mask result' in laynames)  :
                im = viewer.layers['image_mask result'].data > (thresh)
                label_image = label(im)
                viewer.add_labels(label_image, name="seg")
                gdict["gthresh"] = thresh



        @magicgui(call_button="get_mask", layout="vertical")
        def image_mask(layer: Image, mean_width = 6, noise = "0.00", PhaseContrast = True, process_all = False) -> 'napari.types.ImageData':
            global gdict
            laynames = [ l.name for l in viewer.layers]
            idx = laynames.index(viewer.active_layer.name)

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

                updatemeta(gdict, idx)
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

                updatemeta(gdict, idx)

                return seg_img(img, scale=round(10/mean_width, 2), noise=noise, invert=PhaseContrast, frame = viewer.dims.point[0], save=process_all)
        

        #viewer.grid_view()
        # instantiate the widget
        #gui = image_mask.Gui()
        #image_mask.show(run = True)
        # add our new widget to the napari viewer
        #viewer.window.add_dock_widget(gui, area="right")
        viewer.window.add_dock_widget(image_mask, area="right")
        
        # keep the dropdown menus in the gui in sync with the layer model
        #viewer.layers.events.changed.connect(lambda x: gui.refresh_choices("layer"))
        viewer.layers.events.changed.connect(updatelayer)


        @magicgui(
            auto_call=True,
            threshold={"widget_type": "IntSlider", 'min': 1, 'max': 255, 'orientation':"horizontal"},
            #value = {"fixedWidth": 50}
        )
        def make_labels(threshold = 220, value = "220"):
            return threshold
        #gui1 = make_labels.Gui(show = True)
        #viewer.window.add_dock_widget(gui1)
        #make_labels.show(run = True)
        viewer.window.add_dock_widget(make_labels)
        #viewer.window.add_dock_widget(label={'widget_type': QLabel, 'text':"label"})
        #gui1.threshold_changed.connect(changelabels)
        make_labels.threshold.changed.connect(changelabels)
        


        @magicgui(call_button="save_labels")
        def funcsave_labels():
            imsave(str(gdict["gfilename"])+"_thresh_"+str(gdict["gthresh"])+"_labels.tif",(-4294967295.0*viewer.layers["seg"].data).astype(np.uint32))
            return None
        #gui4 = funcsave_labels.Gui(show=True)
        #viewer.window.add_dock_widget(gui4)
        #funcsave_labels.show(run = True)
        viewer.window.add_dock_widget(funcsave_labels)

        @magicgui(call_button="HELP")
        def funcHELP():
            #print("debut")
            msg = QMessageBox()
            msg.setWindowTitle("Help1")
            msg.setText("read Napari : https://napari.org/tutorials/\n"+
            "read the doc : https://github.com/leec13/MiSiCgui\n"+
            "0 - drag and drop the image\n"
            "1 - select default directory\n"+
            "2 - Add a shape layer\n"+
            "3 - trace some widths\n"+
            "4 - get the mean width (button)\n"+
            "5 - set the mean width (field)\n"+
            "6 - get the mask\n"+
            "7 - to create segmentation mouve threshold cursor (only 2D and Time Lapse)")
            msg.exec_()
           
            return None
        #gui5 = funcHELP.Gui(show=True)
        #viewer.window.add_dock_widget(gui5)
        #funcHELP.show(run=True)
        viewer.window.add_dock_widget(funcHELP)

        @magicgui(call_button="get_WIDTH", result_widget=False)
        def meanfunc(mean_width = ""):
            if (viewer.layers[-1].name == "Shapes") & (viewer.layers[-1].selected) :
                data = viewer.layers[-1].data
                c = 0
                for d in data:
                    c += (sum((d[1,:] - d[0,:])**2))**0.5
                return(str(round(c/len(data))))
            else : return ""

        #gui3 = meanfunc.Gui(show=True)
        #viewer.window.add_dock_widget(gui3, area="right")
        #meanfunc.show(run = True)
        viewer.window.add_dock_widget(meanfunc, area="right")

        #gui3.called.connect(lambda result: gui3.set_widget("mean_width", result))
        #meanfunc.called.connect(lambda result: gui3.set_widget("mean_width", result))

        @magicgui(filename={"mode": "d"})
        def filepicker(filename=Path("~")):
            """doc string test"""
            return filename
        # instantiate the widget
        #filepicker.show(run = True)
        #viewer.window.add_function_widget(filepicker)
        viewer.window.add_dock_widget(filepicker, area="right")
        filepicker.filename.changed.connect(defaultpath)

        # magicgui v 2.0
        #with event_loop():
        #    gui2 = filepicker.Gui(show=True)
        #    viewer.window.add_dock_widget(gui2, area="right")
        #    gui2.filename_changed.connect(defaultpath)
            
        #viewer.grid_view()

if __name__ == "__main__":
    # execute only if run as a script
    main()
