

## Installation Instructions

Use miniconda or mini forge to manage your python environments.(We advise using miniforge as it is more likely to avoid any license problem in the future)

````bash
conda create -n LBA_Head python=3.11.11 -y
conda activate LBA_Head
conda install -c conda-forge python=3.11.11 pip
pip install scipy==1.15.1 numpy==1.25.2 lxml ezc3d plotly
conda install -c conda-forge pyorerun rerun-sdk=0.21.0
````

Once you have run this commmand, you should clone the biobuddy repository and install the package from source using the following commands:
````bash
pip install .

````
from the root directory of the BioBuddy source code (the folder containing the file setup.py).    
