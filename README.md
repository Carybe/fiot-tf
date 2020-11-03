# FIOT TensorFlow Project

## This Repository:
First of all: clone this repository and go into its directory, from here on all commands are presumed to be run from there:
```bash
https://gitlab.com/carybe/fiot-tf
cd fiot-tf
```
There are 3 main folders inside the repository:
  - `scripts`: where the scrapping scripts are stored;
  - `notebooks`: where the notebook files `ipynb` are stored;
  - `datasets`: where the scraped datasets, (`.csv` files) are stored.

## Scrapping Script (Data Collecting)
This hardcoded script was used for scrapping [Weather Underground](https://www.wunderground.com/) website for weather data from specific locations at specific time periods.
To setup its environment, do as follows:

```bash
cd scripts
virtualenv -p python3 env
source env/bin/activate
pip install -r script_requirements.txt
deactivate
cd ..
```
Since all of its parameters are hardcoded, to run the script simply activate its environment an run it (it can take quite some time for it to finishes its execution, for such, it's recommended to run it in background, redirect its output and dissociate it from the terminal, as the example):
```bash
cd scripts
source env/bin/activate
python wu_scrap.py &> wu_city.log & disown -a
deactivate
cd ..
```

## Jupyter Notebook

### Environment setup
The environmet, although alot more complex, can be setup the same way of the scrapping script environment (it can even be the same environment for both).
To configure it, one may use the following commands:
```bash
virtualenv -p python3 env
source env/bin/activate
pip install -r requirements.txt
deactivate
``` 

### Notebook Run
The notebook can be simply run by running the following commands:
```bash
cd notebooks
jupyter notebook
```
Then you may run the notebooks from the recently open browser window.
