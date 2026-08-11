# Project Notes

## Setup: virtual environment and dependencies

### Why a virtual environment
Python packages install globally by default, so every project shares one pool.
Different projects eventually need different versions of the same package and
conflict. A venv is an isolated package folder for this project only.

### The four commands
Run from the project folder, in the VS Code terminal (Terminal > New Terminal).
python -m venv venv # creates the venv folder
venv\Scripts\activate # switches into it - prompt shows (venv)
pip install pandas numpy matplotlib statsmodels yfinance
pip freeze > requirements.txt
Same four steps for any Python project. The venv must be activated every
time the terminal is reopened.

### What requirements.txt does
`pip freeze` lists installed packages with versions. `>` writes that output
to a file instead of the screen. Result:
numpy==1.26.4
pandas==2.2.1
statsmodels==0.14.1
Anyone cloning the repo runs `pip install -r requirements.txt` and gets the
same environment. Without it the code fails on the first import.

### How imports connect to this
`pip install pandas` downloads the package into the venv. `import pandas as pd`
in a script tells Python to load it from there. Install once per environment,
import once per file that uses it.

If a script raises `ModuleNotFoundError`, either the package isn't installed
or the venv isn't active.

### Packages used here
- pandas - dataframes, time series handling
- numpy - numerical arrays and maths
- matplotlib - plots
- statsmodels - OLS regression, cointegration tests
- yfinance - price data download

### VS Code interpreter
Ctrl+Shift+P > "Python: Select Interpreter" > choose the one with `venv` in
the path. Without this VS Code runs system Python and won't find the packages.