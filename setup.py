import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MiSiCgui", # Replace with your own username
    version="0.3.7-alpha",
    author="L.Espinosa",
    author_email="leonespcast@gmail.com",
    description="Microbe segmentation in dense colonies graphical interface using Napari",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://imm.cnrs.fr",
    #packages=setuptools.find_packages(),
    packages=['MiSiCgui', 'models'],
    package_dir={'MiSiCgui': 'MiSiCgui', 'models': 'models'},
    py_modules = ['models.*'],
    include_package_data=True,
    install_requires=[
        'numpy',
        'PyQt5',
        'napari',
        'magicgui',
        'tiffile',
        'scikit-image',
        'tensorflow',
        'tqdm',
        'h5py'
    ],
    package_data={"": ["*.png"],"MiSiCgui": ["images/*.png"]},
    data_files=[('images', ['images/screen1.png'])],
    entry_points = {
        'console_scripts': ['MISIC=MiSiCgui.MiSiCgui_main:main'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)

