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
from illiad_api_utils import check_user, submit_transaction

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
    parser.add_argument('-t', '--test', action='store_true',
                        help='Run the script in test mode to output a report showing which transactions will be created and which will produce errors.')
    args = parser.parse_args()
    
    # Assign command line arguments to variables
    filename = args.filename
    email = args.email
    
    if args.pickup:
        pickup = args.pickup
    else:
        pickup = ''

    if args.test:
        test_mode = True
    
    return email, filename, pickup, test_mode

def check_file(filename):

    script_dir = os.path.join(os.path.dirname(__file__), 'data_files')
    filepath = os.path.join(script_dir, filename)

    # Check that the file exists.
    if not os.path.isfile(filepath):
        print('Error: The file ' + filepath + ' does not exist.\n')
        sys.exit()

    # Check that the file is a .csv file.
    elif not filepath.endswith('.csv'):
        print('Error: The file ' + filepath + ' is not a .csv file.\n')
        sys.exit()

    # Check that the file contains a Type column.
    with open(filepath, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        if 'Type' not in reader.fieldnames:
            print('Error: The file must contain a column called "Type".\n')
            sys.exit()

        else:
            return filepath

def validate_row(row, i):
    
    # Check that the row contains data in all required fields according to the transaction type.
    if row['Type'].lower() == 'article':
        required_fields = ['Journal title', 'Article title', 'Author', 'Year']
    if row['Type'].lower() == 'book':
        required_fields = ['Book title', 'Author', 'Publication date']
    missing_fields = [field for field in required_fields if field not in row or not row[field]]

    if missing_fields:
        print(f'Error on line {i}: The following required fields are missing from the row: {", ".join(missing_fields)}.\n')
        return False
    
    else:
        return True
    
def create_transaction(transaction_type, email, pickup, row, i):
    
    # Create a transaction using the appropriate template.
    transaction_templates = get_transaction_templates(email, pickup, row)
    if transaction_type in transaction_templates:

        # If the Type column contains a valid value, create a transaction using the appropriate template.
        # If the CSV file contains a value for a column, use that value. If not, use the default value from the template.
        transaction = {k: row.get(v, v) for k, v in transaction_templates[transaction_type].items()}
        return transaction

    # If the Type column contains an invalid value, print an error message and move to the next row.
    else:
        print(f'Error on line {i}: The Type column must contain either "article" or "book".')

def validate_transaction(transaction, i):
               
        # Check that the transaction contains all required fields.
        if transaction['RequestType'] == 'Article':
            required_fields = ['ExternalUserId', 'RequestType', 'ProcessType', 'PhotoJournalTitle', 'PhotoArticleTitle', 'PhotoArticleAuthor', 'PhotoJournalYear']
        if transaction['RequestType'] == 'Loan':
            required_fields = ['ExternalUserId', 'ItemInfo4', 'RequestType', 'ProcessType', 'LoanTitle', 'LoanAuthor', 'LoanDate']
        missing_fields = [field for field in required_fields if field not in transaction or not transaction[field]]
        
        if missing_fields:
            print(f'Error on line {i}: The following required fields are missing from the transaction: {", ".join(missing_fields)}.\n')
            return False
    
        else:
            return True

def process_transaction_csv(email, filename, filepath, pickup, test_mode):
    
    # Open the file as a CSV reader object.
    print('Reading file ' + filename + '...\n')
    
    with open(filepath, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        
        print('Creating transactions...\n')
        
        # Create and submit a transaction for each row in the reader object.
        for i, row in enumerate(reader, start=1):

            if not validate_row(row, i):
                continue

            transaction_type = str.lower(row['Type'])
            transaction = create_transaction(transaction_type, email, pickup, row, i)

            if not transaction or not validate_transaction(transaction, i):
                continue

            if test_mode:
                print(f'Transaction {i}: ', end='')
                print(transaction)
                print('\n')

            else:        
                submit_transaction(transaction, api_base, api_key, i)

    print('\nProcessing complete.')
        
def main():
    email, filename, pickup, test_mode = get_args()
    filepath = check_file(filename)
    check_user(email, api_base, api_key)
    process_transaction_csv(email, filename, filepath, pickup, test_mode)

if __name__ == '__main__':
    main()