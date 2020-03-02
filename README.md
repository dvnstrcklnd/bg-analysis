# BG Analysis
A set of Jupyter notebooks for analyzing Dexcom and Tidepool data

## Installation
This code is designed to be run in a Docker container. You will need  
[Docker](https://www.docker.com/get-started) if you don't have it already.

To install:
```bash
git pull https://github.com/dvnstrcklnd/bg-analysis.git
cd bg-analysis
docker-compose build
docker-compose up
```
This will start the Jupyter server. To access the notebooks, 
copy one of the links that are provided in the terminal. Everything is in the `work` directory,
which is also available from the local filesystem.

## Dexcom
Dexcom analysis is provided by `class DexcomExplorer`. A new instance of this class will automatically 
read all `*.csv` files in the top level of `work`, assuming that they are 
[exported from Clarity](https://www.dexcom.com/faq/can-i-export-raw-data). It will 
concatenate all of the `.csv` files it finds into a single Pandas `DataFrame`, and remove duplicates. 
This class provides methods for plotting summary data over time.

## Tidepool
`class TidepoolExplorer` reads in data 
[exported from Tidepool](https://support.tidepool.org/hc/en-us/articles/360019872811-Export-your-data), 
but doesn't do much else at this time. 
