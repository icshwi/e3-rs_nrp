require rs_nrp,master

epicsEnvSet("TOP", "$(E3_CMD_TOP)/..")
epicsEnvSet("IP", "172.30.155.12")
epicsEnvSet("secsub", "SRFLab-010")
epicsEnvSet("disdevidx", "RFS-PM-01")

epicsEnvSet("ASYN_PORT", "RS_NRP")

epicsEnvSet("EPICS_CAS_SERVER_PORT", "5068")
epicsEnvSet("EPICS_CA_MAX_ARRAY_BYTES", "65536")

iocshLoad("$(rs_nrp_DIR)/rs_nrp.iocsh", "secsub=$(secsub), disdevidx=$(disdevidx), IP=$(IP), ASYN_PORT=$(ASYN_PORT)")

iocInit

dbl > "$(TOP)/PVs.list"
