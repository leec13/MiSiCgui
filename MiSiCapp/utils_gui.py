# -*- coding: utf-8 -*-

import os, sys
from pathlib import Path

from skimage.io import imsave,imread
import skimage.io
from skimage.measure import label
#from skimage.external import tifffile as tifffile
import tiffile as tiffile
import numpy as np
#from skimage.transform import resize,rescale
#from skimage.filters import gaussian, laplace, threshold_otsu, median
#from skimage.util import random_noise,pad
#from skimage.feature import shape_index
#from skimage.feature import hessian_matrix, hessian_matrix_eigvals
#from skimage.exposure import adjust_gamma

#from tensorflow.keras.models import load_model
#from tensorflow.keras.utils import get_file 


import napari
from napari.layers import Image
from magicgui import magicgui
from magicgui._qt.widgets import QDoubleSlider
from magicgui import event_loop, magicgui
from PyQt5.QtWidgets import QDoubleSpinBox
from PyQt5.QtCore import Qt

#import PIL
#from PIL.TiffTags import TAGS

from MiSiC.MiSiC import *

pass