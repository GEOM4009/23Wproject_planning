# planningproj
The workspace and repo for the GEOM4009 'Planning' group project

# Installation
- The following steps assume you have an installation of Anaconda (or one of its variants)
  - https://www.anaconda.com/products/distribution (full GUI available)
  - https://docs.conda.io/en/latest/miniconda.html (lightweight CLI only)
  - https://anaconda.org/conda-forge/mamba (for faster environment solving)  

- Download or clone this repository, navigate to it in an Anaconda Prompt, and type
``` 
  conda env create -f planningproj_env.yml
```
- Once this has completed activate the environment with 
```
  conda activate planningproj_env
``` 
- You can then run the script with
```
  python planning.py
```

# Dependencies
- [*python*](https://www.python.org/) tested with 3.10
- [*geopandas*](https://geopandas.org/) powerful geospatial data handling
- [*tkinter*](https://docs.python.org/3/library/tkinter.html) GUI toolkit
- [*psutil*](https://psutil.readthedocs.io/en/latest/) process and system utilities
- [*sphinx*](https://www.sphinx-doc.org/en/master/) documentation generator



# Resources
- https://www.nunavut.ca/
- https://www.nunavut.ca/land-use-plans/draft-nunavut-land-use-plan
- https://www.nunavut.ca/land-use-plans/interactive-maps
- https://lupit.nunavut.ca/portal/registry.php
- https://marxansolutions.org/

# Files and Directory

- The files and directories of relevance are listed below

│   defs.py --------------------> Contains common definitions, strings, defaults etc. for use in other files \
│   LICENSE.txt \
│   planning.py ----------------> Main script, uses defs.py and util.py \
│   planningproj_env.yml -------> environment file to be used when setting up with Anaconda \
│   util.py --------------------> Contains utility and helper functions to provide file, print, and other useful features to planning.py \
├───data -----------------------> original data \
├───docs -----------------------> sphinx documentaion \
│   ├───build \
│   │   ├───doctrees \
│   │   └───html \
│   │       │   index.html -----> home page to view documention \
│   └───source \
├───Report4_Data ---------------> Small sets of data and instruction to test functionality \
│   ├───ExtractCRS \
│   ├───GenerateGrid \
│   ├───MultiOverlap \
│   └───SimpleOverlap 
