MiSiC & MiSiCgui Handbook
=========================

# 1 - Introduction 

!['handbook_workflow.png'](./images/handbook_workflow.png)

MiSiC is a tool that allows generating a segmentation mask from microscopic images of bacterial cells. MiSiC has the capacity to detect and segment bacterial cells in microcolonies and/or dense images, which is not achievable using intensity thresholds.. MiSiC can handle a wide range of bacterial morphologies and microscope modalities such as phase contrast, brightfield and fluorescence. MiSiC functions upstream of specialised tools for bacterial cell biology dedicated to measuring cellular features like area, length, position, etc (some convenient tools for this are MicrobeJ and Oufti). A graphical user interface named 'MiSiCgui"is available  (see below point 3). The main advantages of MiSiC are :

- Provide a pre-trained model with general detection capacities under various imaging modalities

- Provide an easy parameter handling with a graphical user interface


## a) Recommended images: size, resolution and cells density

MiSiC is based in a pre-trained convolutional network (CNN). It works for images obtained at high magnification and resolution (> 60x and N.A > 1.25), common CMOS cameras with a photosite size of around 6 µm yield a 60-100nm/pixel resolution. The CNN model was trained with synthetic data with a width of 10 image pixels. This value is in the range of bacteria cells size (≈ 1 µm). The size parameter adjusts the size of the source image to be close to the training conditions (see below).

## b) Phase Contrast, Brightfield, Fluorescence

These modalities are mostly used in photonic microscopy. The MiSiC model was trained with a representation of the image ("Shape Index") independent from the microscope modality, allowing to predict the binary masks from any of these three kinds of images. MiSiC need to set if there are bright objects in a dark background (Brightfield and fluorescence) or dark objects in a light background (phase contrast)

## c) Pre-processing

Usually any pre processing step is required. However some low quality images or images with a wide range of intensities (i.e. fluorescence signal with an heterogeneous protein expression) may yield better results with a pre processing modification. For Phase Contrast images usually a slight correction of gamme over 1.0 could increase the contrast of light cells. For fluorescence images a gamma correction close to 0.2 and a Gaussian of Laplacian modification could increase the detectivity with MiSiC (see below) :

!['handbook_pre_processing.png'](./images/handbook_pre_processing.png)

In this example the pre processing of the fluorescence images improves the quality of the prediction (100X NA 1.43 microscope objective, 0.06 µm/pixel; gamma correction = 0.25 ; Laplacian filter ; Gaussian filter r = 2 px)

## d) Parameters : size and noise

In the training data set for MiSiC the objects had a mean width of 10 pixels. So a scale factor called "size" has been provided to adjust the mean size of the source data to a value close to 10 pixels.
The noise parameter has been provide in order to prevent some false positive artifacts in the Phase Contrast images with high contrast and high quality. This is due to the "halo effect" of Phase Contrast technique (see below):

!['handbook_noise2.png'](./images/handbook_noise2.png)

## e) Post-processing.

Generally the masks yielded by MiSiC for rod shape bacteria could be used as it. The MiSiCgui (see below) allows you to save the probability map as a 8 bits image that could be simply threshold or threshold it inside the GUI (labels generations) and save it as a 32 bits labeled mask. No image post-processing algorithm was implemented because the process depends on the desired result for a specific project, so the for user is more convenient to start with a raw mask (see supp data in ref.).

# 2 - MiSiC
## a) Installation
Requires version python version 3.6

`pip install git+https://github.com/pswapnesh/MiSIC.git`

or 

`pip install https://github.com/pswapnesh/MiSiC/archive/master.zip`



## b) Usage
### command line
`mbnet --light_background True --mean_width 8 --src '/path/to/source/folder/\*.tif' --dst '/path/to/destination/folder/'`

`mbnet -lb True -mw 8 -s /path/to/source/folder/*.tif -d /path/to/destination/folder/`

### use package
```python
from MiSiC.MiSiC import *
from skimage.io import imsave,imread

filename = 'awesome_image.tif'

# read image using your favorite package
im = imread(filename)

# Parameters that need to be changed
## Ideally, use a single image to fine tune two parameters : mean_width and noise_variance (optional)

#input the approximate mean width of microbe under consideration
mean_width = 8
noise_variance = 0.0001

# compute scaling factor
scale = (10/mean_width)

# Initialize MiSiC
misic = MiSiC()

# preprocess using inbuit function or if you are feeling lucky use your own preprocessing
im = pre_processing(im,scale = scale, noise_var = noise_variance)

# segment the image with invert = True for light backgraound images like Phase contrast
y = misic.segment(im,invert = True)

# if you need both the body y[:,:,0] and contour y[:,:,1] skip the post processing.
y = post_processing(y,im.shape)

# save 8-bit segmented image and use it as you like
imsave('segmented.tif', (y*255).astype(np.uint8))

```

# 3 - MiSiCgui


A GUI for MiSiC tool

Based on MiSiC ("https://github.com/pswapnesh/MiSiC")

Please cite: ("https://www.biorxiv.org/content/10.1101/2020.10.07.328666v1")


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



