#!/bin/bash
#SBATCH --job-name=createdb
#SBATCH --output=logs/%x_%A_%a.out
#SBATCH --error=logs/%x_%A_%a.err
#SBATCH --array=0-4
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=04:00:00

# Set Singularity run command (important!)
RUN="singularity exec -B /farmshare/user_data/ymoon1,/farmshare/home/classes/bios/270 /farmshare/home/classes/bios/270/envs/bioinformatics_latest.sif"

DATABASE="bacteria.db"

$RUN python insert_gff_table.py --database_path $DATABASE
$RUN python insert_protein_cluster_table.py --database_path $DATABASE
$RUN python insert_metadata_table.py --database_path $DATABASE
