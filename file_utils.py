#!/usr/bin/env python3
# file_utils.py
# Description: Utilities to help with managing files, for use with the bulk_ill.py script.
# Author: Kristen Wilson, NC State University Libraries, kmblake@ncsu.edu

import csv
from rispy_utils import map_rispy

# Open a CSV file as a reader object.
def open_csv(source_file):
    reader = csv.DictReader(source_file)
    return reader

#  Open a RIS file as a reader object.    
def open_ris(source_file):
    reader = csv.DictReader(source_file)
    return reader
    
# Create a results file and write the header row.    
def create_results_file(reader, resultsfile):
    writer = None
    # Create a header row for the results file.
    fieldnames = ['Line number', 'Error', 'Transaction', 'Transaction number']
    writer = csv.DictWriter(resultsfile, fieldnames=fieldnames)
    writer.writeheader()
    return writer