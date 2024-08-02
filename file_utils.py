#!/usr/bin/env python3
# file_utils.py
# Description: Utilities to help with managing files, for use with the bulk_ill.py script.
# Author: Kristen Wilson, NC State University Libraries, kmblake@ncsu.edu

import csv
import datetime
import os
from rispy_utils import map_rispy

# Open a CSV file as a reader object.
def open_csv(source_file):
    reader = csv.DictReader(source_file)
    return reader

#  Open a RIS file as a reader object.    
def open_ris(source_file):
    reader = csv.DictReader(source_file)
    return reader
    
# Get the current date and time to the nearnest second for use in filenames.
def get_date_time():
    now = datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
    return now

# Ensure the "results" folder exists
def check_for_results_folder():
    if not os.path.exists('results'):
        os.makedirs('results')

def construct_results_filepath(filename, now):
    results_filename = f'{filename}_{now}.csv'
    results_filepath = os.path.join('results', results_filename)
    print(f'Results will be saved to {results_filepath}\n')
    return results_filepath

# Create a results file and write the header row.    
def create_results_file(reader, resultsfile):
    writer = None
    # Create a header row for the results file.
    fieldnames = ['Line number', 'Error', 'Transaction', 'Transaction number']
    writer = csv.DictWriter(resultsfile, fieldnames=fieldnames)
    writer.writeheader()
    return writer