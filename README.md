# UAS Tracking Framework
[![Build Status](https://travis-ci.org/UAS-Bachelor/uas-tracking.svg?branch=master)](https://travis-ci.org/UAS-Bachelor/uas-tracking)
[![Coverage Status](https://coveralls.io/repos/github/UAS-Bachelor/uas-tracking/badge.svg?branch=master)](https://coveralls.io/github/UAS-Bachelor/uas-tracking?branch=master)

Bachelor project concerning UAV tracking and visualization,  by Niels Heltner and Lars Christensen at SDU, MMMI, spring 2018.


## Installation and running
Requires Python 3.6 and pip.
1. Download or clone the project
2. Execute the following command `pip install -r requirements.txt` to install the required Python packages
3. Execute the `run.py` script to run the server. This will launch all microservices
   * If on Unix, the command might need to be executed as `sudo python3 run.py`
   * If the nofly_information module fails on MacOS, directly run `/Applications/Python\ 3.6/Install\ Certificates.command`


## Documentation
An API overview and detailed API description can be found [here](https://docs.google.com/document/d/1sgmST3H5-IDegrrKFVCr_vQVqwL7w1Tg-pdPdTY59es/edit?usp=sharing).
