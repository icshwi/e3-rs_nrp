#!/bin/bash

#read -p "IOC IP address?" IP

# takes IOC parameters from Client
# 1 - IP address
# 2 - IOC name

# -->1. generate config file
echo "epicsEnvSet(\"IP\", \"$1\")" > config
echo "epicsEnvSet(\"secsub\", \"$2\")" >> config
echo "epicsEnvSet(\"disdevidx\", \"$3\")" >> config
#### The second option ####
#echo "Arg_IP=$1" >config
#echo "Arg_secsub=$2" >>config
#echo "Arg_disdevidx=$3" >>config
###########################

# -->2. enter into the E3 environment
#source ./config
#export Arg_IP
#export Arg_secsub
#export Arg_disdevidx

#echo "IP address is:" $Arg_IP
#echo "IOC name is:" $Arg_secsub:$Arg_disdevidx

###########################
source ~/gitsrc/e3-3.15.5/tools/setenv

# -->3. start up the ioc 
iocsh.bash ~/gitsrc/e3-rs_nrp/cmds/rs_nrp.cmd


