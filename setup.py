import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MiSiCapp", # Replace with your own username
    version="0.2.2",
    author="L.Espinosa",
    author_email="leonespcast@gmail.com",
    description="Microbe segmentation in dense colonies graphical interface using Napari",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://imm.cnrs.fr",
    packages=setuptools.find_packages(),
    #packages=[''],
    install_requires=[
   'PyQt5',
   'napari',
   'magicgui',
   'tiffile',
   'MiSiC @ git+https://github.com/pswapnesh/MiSiC.git'
    ],
    dependency_links=['MiSiC @ git+https://github.com/pswapnesh/MiSiC.git'],
    entry_points = {
        'console_scripts': ['MISIC=MiSiCapp.MiSiCapp_main:main'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)