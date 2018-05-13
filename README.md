# UAS Tracking Framework
[![Build Status](https://travis-ci.org/UAS-Bachelor/uas-tracking.svg?branch=master)](https://travis-ci.org/UAS-Bachelor/uas-tracking)
[![Coverage Status](https://coveralls.io/repos/github/UAS-Bachelor/uas-tracking/badge.svg?branch=master)](https://coveralls.io/github/UAS-Bachelor/uas-tracking?branch=master)

Bachelor project concerning UAV tracking and visualization,  by Niels Heltner and Lars Christensen at SDU, MMMI, spring 2018.


## Installation and running
Requires Python 3 and pip3.
1. Download or clone the project
2. Execute the following command `pip install -r requirements.txt` to install the required Python packages
   * If on Unix, the command might have to be run as `sudo pip3`
   * If on Unix and there's an error during installation of `mysqlclient`, install the package `python-mysqldb`
   * If on Windows, the command might have to be run in an elevated command prompt
3. Execute the `run.py` script to run the server. This will launch all microservices
   * If on Unix, the command might need to be executed as `sudo python3 run.py`
   * If the nofly_information module fails on MacOS, directly run `/Applications/Python\ 3.6/Install\ Certificates.command`
   * If `libf77blas.so.3` is missing on Linux, install the package `libatlas-base-dev`
   * If `liblapack.so.3` is missing on Linux, install the package `liblapack3`


## Documentation
An API overview and detailed API description can be found [here](https://docs.google.com/document/d/1sgmST3H5-IDegrrKFVCr_vQVqwL7w1Tg-pdPdTY59es/edit?usp=sharing).


## Testing
Tests are automatically run by the Travis CI build server on every push to the git repository, but tests can also be run manually by executing the command `pytest` or `python -m pytest` in the project root.