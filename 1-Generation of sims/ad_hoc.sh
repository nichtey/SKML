#!/bin/bash
#PBS -N name_9e0272da291d4e4eb295ad03f35f132e
#PBS -q gpu
#PBS -l Walltime=walltime_0bcf006c78d449989c7444ea9d5ea3f2
#PBS -l select=1:ncpus=24:mem=24GB
#PBS -P project_564e4c15d2ca463696fff4f3b7020dd2

module load mumax
mumax3 mx3_file_6cd0eb031acf4b36982d877fe8c142ce
