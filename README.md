!['Logo_Misic-14small.png'](./images/Logo_Misic-14small.png)

MiSiC & MiSiCgui Handbook
=========================

# 1 - Introduction 

!['handbook_workflow.png'](./images/handbook_workflow.png)

MiSiC is a tool that allows generating a segmentation mask from microscopic images of bacterial cells. MiSiC has the capacity to detect and segment bacterial cells in microcolonies and/or dense images, which is not achievable using intensity thresholds. MiSiC can handle a wide range of bacterial morphologies and microscope modalities such as phase contrast, brightfield and fluorescence. MiSiC functions upstream of specialised tools for bacterial cell biology dedicated to measuring cellular features like area, length, position, etc (some convenient tools for this are MicrobeJ and Oufti). A graphical user interface named 'MiSiCgui"is available  (see below point 3). The main advantages of MiSiC are :

- Provide a pre-trained model with general detection capacities under various imaging modalities

- Provide an easy parameter handling with a graphical user interface


## a) Recommended images: size, resolution and cells density

MiSiC is based ona pre-trained convolutional network (CNN). It works for images obtained at high magnification and resolution (> 60x and N.A > 1.25), common CMOS cameras with a photosite size of around 6 µm yield a 60-100nm/pixel resolution. The CNN model was trained with synthetic cell shapes with a width of 10 pixels. This value was chosen to match the average width of bacterial cells observed at this resolution (1 µm). Therefore, the size parameter  is meant to adjust the size of the source image to the size of the objects used to train the model (see below).

## b) Phase Contrast, Brightfield, Fluorescence

The MiSiC model was trained with a representation of the image ("Shape Index") to obtain binary masks from any three imaging modalities, phase contrast, bright-field and fluorescence.  MiSiC only needs to be set to detect bright objects in a dark background (Brightfield and fluorescence) or dark objects in a light background (phase contrast)

## c) Pre-processing

In most cases, pre-processing is not required. However some low quality images or images with a wide range of intensities (i.e. fluorescence signal with an heterogeneous protein expression) may yield better results with a pre-processing modification. For Phase Contrast images a slight gamma correction over 1.0 may improve the contrast of light cells. For fluorescence images a gamma correction close to 0.2 and a Gaussian of Laplacian modification may increase the detectivity with MiSiC. An example is shown below:

!['handbook_pre_processing.png'](./images/handbook_pre_processing.png)

In this example the pre-processing of the fluorescence images improves the quality of the prediction (100X NA 1.43 microscope objective, 0.06 µm/pixel; gamma correction = 0.25 ; Laplacian filter ; Gaussian filter r = 2 px)

## d) Parameters : size and noise

In the training data set for MiSiC the objects had a mean width of 10^4 pixels. So a scale parameter called "size" is provided to adjust the mean size of the source data to a value close to 10 pixels.
A noise parameter (in the GUI see below the value is divided by 104) can also be adjusted  to prevent false positive artifacts in the Phase Contrast images with high contrast and high quality. This is due to the "halo effect" of Phase Contrast technique (see below):

!['handbook_noise2.png'](./images/handbook_noise2.png)

## e) Post-processing.

MiSiCgui (see below) saves the probability map as an 8 bits image that can be thresholded for semantic cell recognition and saved a 32 bits labeled mask.Post processing depends on desired application. In dense regions, when not fully resolved cell separation and septa can be improved by applying algorithms on the mask such as watershed or even supersegger. Cells may also be filtered by available softwares such as MicrobeJ and Oufti. 

# 2 - MiSiC

Based on MiSiC ("https://github.com/pswapnesh/MiSiC")

## a) Installation
Requires version python version 3.6/7

`pip install misic`


### use package

```python
from misic.misic import *
from skimage.io import imsave,imread
from skimage.transform import resize,rescale

filename = 'awesome_image.tif'

# read image using your favorite package
im = imread(filename)

# Parameters that need to be changed
## Ideally, use a single image to fine tune two parameters : mean_width and noise_variance (optional)

#input the approximate mean width of microbe under consideration
mean_width = 8

# compute scaling factor
scale = (10/mean_width)

# Initialize MiSiC
mseg = MiSiC()

# preprocess using inbuit function or if you are feeling lucky use your own preprocessing
im = rescale(im,scale,preserve_range = True)

# add local noise
img = add_noise(im,sensitivity = 0.13,invert = True)

# segment
yp = mseg.segment(img,invert = True)
yp = resize(yp,[sr,sc,-1])

# watershed based post processing
yp = postprocess_ws(img,yp)

# save 8-bit segmented image and use it as you like
imsave('segmented.tif', yp.astype(np.uint8))

### In case of gpu error, one might need to disabple gpu before importing MiSiC [ os.environ["CUDA_VISIBLE_DEVICES"]="-1" ]
```

# 3 - MiSiCgui

A Graphic User Interface (GUI) for MiSiC

## a) Installation

Requires version python version 3.7 install via [pip]:
We strongly recommend creating a specific environment with conda/miniconda (https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html).

After conda installation open a terminal and :

`conda create --name MiSiCgui git python=3.7`

`conda activate MiSiCgui`

`pip install git+https://github.com/leec13/MiSiCgui.git`

`MISIC`

## b) Troubleshooting

Windows :

Sometimes you will need to re-install numpy

`conda activate MiSiCgui`

`conda install numpy`

Mac : 

PyQt5 needs mac os > 10.13 (or manage to install pyqt5 example : https://gist.github.com/guillaumevincent/10983814)

Sometimes you will need to install Xcode.

or at least the gcc compiler :

`conda activate MiSiCgui`

`conda install clang_osx-64`

`conda install -c anaconda psutil`

(not tested yet)

Linux :

Some linux systems need :

`conda activate MiSiCgui`

`conda install gcc_linux-64`

`sudo apt-get install --reinstall libxcb-xinerama0`

Know bugs : error while quit the application

## c) Usage

### Start the GUI app
type MISIC in the terminal:

```bash
$ conda activate MiSiCgui
$ MISIC
```

## d) 
### How to use it
The Napari site explain how to use the interface, please see :

("https://napari.org/tutorials/")

The images folder contains some images exemples and the resulting masks with the parameters used in the file name.

Specific commands for MISICgui (respect the order)

1 - Drag and drop one images

2 - Select a default directory

3 - Measure roughly the mean width of cell (steps 2, 3, 4 in the screenshot below)

5 - Set the mean width with the upper right button

6 - click "get_mask" button

To process all slides of one stack select "process all"

The screenshots below explain each step :

First step, determine a starting value for the mean width parameter

!['screen1.png'](./images/screen1.png)

Generate a mask for the current slide or for the whole time lapse stack

!['screen2.png'](/images/screen2.png)

Generate a threshold image labeled (works also for stacks)

!['screen3.png'](./images/screen3.png)


