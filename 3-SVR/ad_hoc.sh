#!/bin/bash
#PBS -N Test
#PBS -q normal
#PBS -l Walltime=24:00:00
#PBS -l select=4:ncpus=24:mem=96GB
#PBS -P 13001265

module load /home/users/astar/imre/chenxy14/apps/anaconda3/bin/python3.7
python3 /scratch/users/astar/imre/chenxy14/Micromagnetics/sk-ML/Optimisation/OptimiseSVR.py
