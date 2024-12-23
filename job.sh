#!/bin/bash
#BSUB -J DTU_courses
#BSUB -o DTU_courses_%J.out
#BSUB -e DTU_courses_%J.err
#BSUB -R "rusage[mem=4GB]"
#BSUB -W 24:00
#BSUB -n 1

# Echo start time
echo "Job started at: $(date)"

# Activate existing virtual environment
source ~/RAG/myenv/bin/activate

# Navigate to the correct directory
cd ~/RAG

# Run the script
python scrap/get_all_courses_text.py

# Echo end time
echo "Job finished at: $(date)"
