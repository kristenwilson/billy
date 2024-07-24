#!/usr/bin/env python3
# validation_utils.py
# Description: Utilities to validate citation files and transactions; for use by bulk_ill.py.
# Author: Kristen Wilson, NC State Libraries, kmblake@ncsu.edu

# Built-in modules
import os
import sys
import csv

# Validate that the file exits in the data_files directory and return the full filepath.
def validate_file(filename):

    script_dir = os.path.join(os.path.dirname(__file__), 'data_files')
    filepath = os.path.join(script_dir, filename)

    if not os.path.isfile(filepath):
        print('Error: The file ' + filepath + ' does not exist.\n')
        sys.exit()

    else:
        return filepath

# Identify the file type (.csv or .ris) and verify that it contains an "Item Type" field for each citation.
def validate_file_type(filename, filepath):

    filetype = None    
    
    with open(filepath, 'r', encoding='utf-8') as file:
        first_line = file.readline().strip()
        
        # Skip blank lines at the beginning of the file.
        while not first_line:
            first_line = file.readline().strip()
        
        # If the first line of the file is a RIS 'type' tag, the file treated as an RIS file.
        if first_line.__contains__('TY  -'):
            filetype = 'ris'
            print('\nRIS file confirmed.')
            return filetype
        
        # If there is a comma in the first line, the file treated as a CSV file.
        # Note that this is a simple check and may not work for all CSV files.
        elif ',' in first_line:        
            try:
                with open(filepath, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    
                    # Check that the file contains an 'Item Type' column.
                    if 'Item Type' not in reader.fieldnames:
                        print('Error: The file must contain a column called "Item Type".\n')
                        sys.exit()

                    filetype = 'csv'
                    print('\nCSV file confirmed.')
                    return filetype
            
            # If the file is not a valid CSV file, exit the program.
            except csv.Error:
                print('Error: The file ' + filepath + ' is not a valid CSV file.\n')
                sys.exit()
            
        # If the file is not a valid RIS or CSV file, exit the program.
        else:
            print('Error: The file ' + filename + ' is not a valid file type. The file must be a CSV or RIS file.\n')
            sys.exit()

# Validate the transaction that will be sent to ILLiad to ensure it contains all required data and return an error if it does not.    
def validate_transaction(transaction):
            
    # Check that the transaction contains all required fields.
    if transaction['RequestType'] == 'Article':
        required_fields = ['ExternalUserId', 'RequestType', 'ProcessType']
    if transaction['RequestType'] == 'Loan':
        required_fields = ['ExternalUserId', 'ItemInfo4', 'RequestType', 'ProcessType']
    missing_fields = [field for field in required_fields if field not in transaction or not transaction[field]]
    
    # Replaces 'ItemInfo4' with 'Pickup Location' in the error message for user clarity.
    if 'ItemInfo4' in missing_fields:
        missing_fields.remove('ItemInfo4')
        missing_fields.append('Pickup Location')
    
    # Return an error if the transaction is missing any required fields.
    if missing_fields:
        error = f'The following required fields are missing from the transaction: {", ".join(missing_fields)}.'
        return error