#!/bin/bash
# Job settings
JOB_NAME="flukaagent_job5"
export FLUKAPATH="/mnt/c/Users/zavier.ndum/OneDrive - Texas A&M University/Research_ZDFDJ/AIML_Workshop/FWT_TEPC/FLUKAAGENT_Sims/Results"
cd "/mnt/c/Users/zavier.ndum/OneDrive - Texas A&M University/Research_ZDFDJ/AIML_Workshop/FWT_TEPC/FLUKAAGENT_Sims/Results"
# Fluka Simulation for input file
/usr/local/fluka/bin/rfluka -M 1 fwt_tepc_05.inp
