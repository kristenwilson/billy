#!/usr/bin/env python3
# bulk_ill.py
# Purpose: Input citations from a .csv file and create interlibrary loan transactions in ILLiad for each citation.
# Author: Kristen Wilson, NC State Libraries

import os.path
import sys
import argparse
import csv
from config import api_key, api_base
from transaction_templates import get_transaction_templates
from api_functions import check_user, submit_transaction

def get_args():
    
    # Identify required inputs via command line arguments
    parser = argparse.ArgumentParser(description='Create interlibrary loan transactions in ILLiad for articles in a csv file.')
    parser.add_argument('email', 
                        help='The email address of the person who will receive the requested materials. This person must already have a user account in ILLiad.')
    parser.add_argument('filename', 
                        help='The name of the file to be read. Must be a .csv file.')
    parser.add_argument('-p', '--pickup', 
                        help='The library where the requested materials will be picked up. This is only needed if you are requesting physical materials.',
                        choices=['Hill', 'Hunt', 'Design', 'Natural Resources', 'Veterinary Medicine', 'Textiles', 'METRC', 'Distance/Extension'])
    args = parser.parse_args()
    
    # Assign command line arguments to variables
    filename = args.filename
    email = args.email
    if args.pickup:
        pickup = args.pickup
    else:
        pickup = ''
    
    return email, filename, pickup

def check_file(filename):

    # Check that the file exists in the data_files directory and store the filepath. 
    script_dir = os.path.join(os.path.dirname(__file__), 'data_files')
    filepath = os.path.join(script_dir, filename)

    if not os.path.isfile(filepath):
        print('Error: The file ' + filepath + ' does not exist.\n')
        sys.exit()

    else:
        return filepath

def process_transaction_csv(email, filename, filepath, pickup):
    
    # Open the file as a CSV reader object.
    print('Reading file ' + filename + '...\n')
    
    with open(filepath, 'r') as csvfile:
        reader = csv.DictReader(csvfile)

        print('Creating transactions...\n')

        # Create and submit a transaction for each row in the reader object.
        for i, row in enumerate(reader, start=1):

            transaction_type = str.lower(row['Type'])
            transaction_templates = get_transaction_templates(email, pickup, row)

            # If the Type column contains a valid value, create a transaction using the appropriate template.
            # If the CSV file contains a value for a column, use that value. If not, use the default value from the template.
            if transaction_type in transaction_templates:
                transaction = {k: row.get(v, v) for k, v in transaction_templates[transaction_type].items()}
                submit_transaction(transaction, api_base, api_key)

            # If the Type column contains an invalid value, print an error message and move to the next row.
            else:
                print(f'Error on line {i}: The Type column must contain either "article" or "book".')
                continue

    print('\nProcessing complete.')
        
def main():
    email, filename, pickup = get_args()
    filepath = check_file(filename)
    check_user(email, api_base, api_key)
    process_transaction_csv(email, filename, filepath, pickup)

if __name__ == '__main__':
    main()