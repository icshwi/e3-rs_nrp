require rs_nrp,master

epicsEnvSet("TOP", "$(E3_CMD_TOP)/..")
epicsEnvSet("IP", "172.30.155.13")
epicsEnvSet("secsub", "SRFLab-010")
epicsEnvSet("disdevidx", "RFS-PM-01")

iocshLoad("$(rs_nrp_DIR)/rs_nrp.iocsh", "secsub=$(secsub), disdevidx=$(disdevidx), IP=$(IP)")

iocInit

