#!/bin/bash
#export EPICS_CA_ADDR_LIST=127.0.0.1:5068
#export EPICS_CA_AUTO_ADDR_LIST=NO
conda init bash
which python
python ~/gitsrc/e3-rs_nrp/opi/IOC.py
