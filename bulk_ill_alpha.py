# Path: bulk_ill_alpha.py
# Purpose: Input citation from a .csv file and create interlibrary loan transactions in ILLiad for each citation.
# Author: Kristen Wilson, NC State Libraries

import os.path
import sys
import argparse
import csv

# Identify the file to be read via a command line argument
parser = argparse.ArgumentParser(description='Input citation from a .csv file and create interlibrary loan transactions in ILLiad for each citation.')
parser.add_argument('filename', help='The name of the file to be read. Must be a .csv file.')
args = parser.parse_args()

# Check that the file exists
script_dir = os.path.join(os.path.dirname(__file__), "data_files")
filename = os.path.join(script_dir, args.filename)

if not os.path.isfile(filename):
    print("Error: The file " + filename + " does not exist.")
    sys.exit()
else:
    print("Reading file " + args.filename + "...")
    