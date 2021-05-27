
#import argparse 
#import warnings

#import os, sys
#from os.path import dirname, basename, isfile, join
#import importlib
#import importlib.util
#from pathlib import Path

#import glob
#from pathlib import Path

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

#from MiSiC.MiSiC import *
#import models
#import MiSiCgui
#from utils import *

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

gdict = {"gDir":"", "gfilename" : os.path.join("~", "out.tif"), "gdims" : None, "width" : None, "gnoise" : None, "gthresh":220, "ginvert" : None, "gpos" : None, "gsave_all" : None}


p = Path(__file__).parents[1]
p = join(p, "MiSiCgui", "models")
print(p)
modpaths = glob.glob(join(Path(p), "*.py"))
MODELS = [ basename(f)[:-3] for f in modpaths if isfile(f) and not f.endswith('__init__.py')]
print(MODELS)

mmodd = MODELS[0]
#modpath = modpaths[MODELS.index("misic_synthetic_b")]
amodel = "models."+ mmodd
currentModel = importlib.import_module(amodel)

misic = currentModel.SegModel()

