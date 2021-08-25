
import argparse 
import warnings

import os, sys
from os.path import dirname, basename, isfile, join
import importlib
import importlib.util
from pathlib import Path
import glob

from skimage.io import imsave,imread
from skimage.transform import resize,rescale
from skimage.util import random_noise
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


import models
#import utils
from MiSiCgui.utils import *

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

gdict = {"gDir":"~", "gfilename" : os.path.join("~", "out.tif"), "gdims" : None, "width" : None, "gnoise" : None, "gthresh":220, "ginvert" : None, "gpos" : None, "gsave_all" : None}


p = Path(__file__).parents[1]
p = join(p, "models")
print(p)
modpaths = glob.glob(join(Path(p), "*.py"))
MODELS = [ basename(f)[:-3] for f in modpaths if isfile(f) and not f.endswith('__init__.py')]
print(MODELS)
mmodd = MODELS[0]
#modpath = modpaths[MODELS.index("MiSiDC04082020")]
amodel = "models."+ mmodd
print(amodel)
currentModel = importlib.import_module(amodel)
misic = currentModel.SegModel()

#misic = MISIC()
viewer = None

def updatemeta(metadict = gdict, idx = 1):
    viewer.layers[idx].metadata = metadict


def seg_img(im, scale=1, noise="0.000", invert=True, frame=0, save=False, threshold=220):
    global gdict

    noise = float(noise)/10000
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
    

    gshape = gdict["gdims"]
    gshape = "_".join([str(i) for i in gshape])

    width = str(gdict["width"])

    imsave(str(gdict["gfilename"])+"_W="+width+"_N="+str(noise)+"_DIM="+gshape+"_frame="+savestr+"_mask.tif",(255.0*hyperS).astype(np.uint8))
    print("Finish")
    return((255.0*hyperS).astype(np.uint8))

def main():
    #with napari.gui_qt():
    global viewer
    global gdict
    viewer = napari.Viewer()

    def updatelayer(layer):
        viewer.layers[-1].metadata=gdict
        updatelayer.reset_choices("layer")
        viewer.layers[-1].metadata=gdict
        print("event", layer)

    def defaultpath(event_apath):
        apath = filepicker.filename.value
        gdict["gDir"] = apath
        if len(viewer.layers) > 0 :
            gdict["gfilename"] = os.path.join(apath, viewer.layers.selection.active.name)
    
    def changelabels(event_thr):

        print(make_labels.threshold.value)
        thresh = make_labels.threshold.value
        laynames = [ l.name for l in viewer.layers]
        #selects = [l.selected for l in viewer.layers]
        idx = laynames.index(viewer.layers.selection.active.name)
        #idx = selects.index(True)
        
        #if ('image_mask result' in laynames)  :
            #im = viewer.layers['image_mask result'].data > (thresh)
        im = viewer.layers[viewer.layers.selection.active.name].data > (thresh)
        label_image = label(im)
            #viewer.add_labels(label_image, name="seg")
        gdict["gthresh"] = thresh
        
        if ('seg' in laynames):
            viewer.layers['seg'].data = label_image
            #i = laynames.index("seg")
            #viewer.layers.pop(i)
            if viewer.layers['seg'] in viewer.layers.selection :
                viewer.layers.selection.remove(viewer.layers['seg'])
            viewer.layers.selection.add(viewer.layers[idx])
        else :
            viewer.add_labels(label_image, name="seg")
            if viewer.layers['seg'] in viewer.layers.selection :
                viewer.layers.selection.remove(viewer.layers['seg'])
            viewer.layers.selection.add(viewer.layers[idx])

        #viewer.layers['seg'].selected = False
        #viewer.layers.selection.remove(viewer.layers['seg'])
        #viewer.layers[idx].selected = True
        #viewer.layers.selection.add(viewer.layers[idx])



    @magicgui(call_button="get_mask", layout="vertical")
    def image_mask(layer: Image, mean_width = 6, noise = "0.00", PhaseContrast = True, process_all = False) -> 'napari.types.ImageData':
        global gdict
        laynames = [ l.name for l in viewer.layers]
        idx = laynames.index(viewer.layers.selection.active.name)

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
    
    viewer.window.add_dock_widget(image_mask, area="right")
    viewer.layers.events.changed.connect(updatelayer)


    @magicgui(
        auto_call=True,
        threshold={"widget_type": "IntSlider", 'min': 1, 'max': 255, 'orientation':"horizontal"},
    )
    def make_labels(threshold = 220):
        return threshold

    viewer.window.add_dock_widget(make_labels, area="bottom")
    make_labels.threshold.changed.connect(changelabels)
    


    @magicgui(call_button="save_labels")
    def funcsave_labels():
        imsave(str(gdict["gfilename"])+"_thresh_"+str(gdict["gthresh"])+"_labels.tif",(-4294967295.0*viewer.layers["seg"].data).astype(np.uint32))
        return None

    viewer.window.add_dock_widget(funcsave_labels, area="bottom")

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
    
    viewer.window.add_dock_widget(funcHELP, area="bottom")

    @magicgui(mean_width = {'bind': ""}, call_button="get_WIDTH", result_widget=True, labels = False)
    def meanfunc(mean_width):
        
        if (viewer.layers[-1].name == "Shapes") & (viewer.layers[-1] in viewer.layers.selection) :
            data = viewer.layers[-1].data
            c = 0
            for d in data:
                c += (sum((d[1,:] - d[0,:])**2))**0.5
                res_mean = (str(round(c/len(data))))
        
        else :
            res_mean = ""
        
        return res_mean

    
    # alternative to mean_width = {'bind': ""} ligne suivante
    # meanfunc.mean_width.bind("")
    viewer.window.add_dock_widget(meanfunc, area="right")


    @magicgui(auto_call=True, filename={"mode": "d"})
    def filepicker(filename=Path("~")):
        """doc string test"""
        return filename
    
    viewer.window.add_dock_widget(filepicker, area="right")
    filepicker.filename.changed.connect(defaultpath)
    napari.run()


if __name__ == "__main__":
    # execute only if run as a script
    main()
