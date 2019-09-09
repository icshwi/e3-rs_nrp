# get the instance parameters
iocshLoad(config)

require rs_nrp,master

epicsEnvSet("TOP", "$(E3_CMD_TOP)/..")
#### The second option ####
#epicsEnvSet("IP", "${Arg_IP}")
#epicsEnvSet("secsub", "${Arg_secsub}")
#epicsEnvSet("disdevidx", "${Arg_disdevidx}")
###########################

epicsEnvSet("ASYN_PORT", "RS_NRP")

epicsEnvSet("EPICS_CA_MAX_ARRAY_BYTES", "131072")

iocshLoad("$(rs_nrp_DIR)/rs_nrp.iocsh", "secsub=$(secsub), disdevidx=$(disdevidx), IP=$(IP), ASYN_PORT=$(ASYN_PORT)")

iocInit

dbl > "$(TOP)/${disdevidx}-PVs.list"

#epicsEnvShow
