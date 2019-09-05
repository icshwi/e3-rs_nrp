require rs_nrp,master

epicsEnvSet("TOP", "$(E3_CMD_TOP)/..")

epicsEnvSet("ASYN_PORT_PREFIX", "RS_NRP") # RS_NRP

epicsEnvSet("secsub", "SRFLab-010")

epicsEnvSet("STREAM_PROTOCOL_PATH", "${rs_nrp_DB}")

epicsEnvSet("EPICS_CAS_SERVER_PORT", "5068")
epicsEnvSet("EPICS_CA_MAX_ARRAY_BYTES", "65536")

epicsEnvSet("IP", "172.30.155.12") #PM01
epicsEnvSet("disdevidx", "RFS-PM-01")
iocshLoad("$(rs_nrp_DIR)/rs_nrp.iocsh", "secsub=$(secsub), disdevidx=$(disdevidx), IP=$(IP), ASYN_PORT=$(ASYN_PORT_PREFIX)_1")

epicsEnvSet("IP", "172.30.155.13") #PM02
epicsEnvSet("disdevidx", "RFS-PM-02")
iocshLoad("$(rs_nrp_DIR)/rs_nrp_calibration.iocsh", "secsub=$(secsub), disdevidx=$(disdevidx), IP=$(IP), ASYN_PORT=$(ASYN_PORT_PREFIX)_2")

epicsEnvSet("IP", "172.30.155.14") #PM03
epicsEnvSet("disdevidx", "RFS-PM-03")
iocshLoad("$(rs_nrp_DIR)/rs_nrp_calibration.iocsh", "secsub=$(secsub), disdevidx=$(disdevidx), IP=$(IP), ASYN_PORT=$(ASYN_PORT_PREFIX)_3")

iocInit

dbl > "$(TOP)/PVs.list"
