import os
import sys
import csv

def validate_file(filename):

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

def validate_row(row):
    
    # Check that the row contains a valid value in the Type column.
    if row['Type'].lower() not in ['article', 'book']:
        error = f'The Type column must contain either "article" or "book".'
        #print(error)
        return error
    
    # Check that the row contains data in all required fields according to the transaction type.
    if row['Type'].lower() == 'article':
        required_fields = ['Journal title', 'Article title', 'Author', 'Year']
    if row['Type'].lower() == 'book':
        required_fields = ['Book title', 'Author', 'Publication date']
    missing_fields = [field for field in required_fields if field not in row or not row[field]]

    if missing_fields:
        error = f'The following required fields are missing from the row: {", ".join(missing_fields)}.'
        #print(error)
        return error
    
def validate_transaction(transaction):
            
    # Check that the transaction contains all required fields.
    if transaction['RequestType'] == 'Article':
        required_fields = ['ExternalUserId', 'RequestType', 'ProcessType', 'PhotoJournalTitle', 'PhotoArticleTitle', 'PhotoArticleAuthor', 'PhotoJournalYear']
    if transaction['RequestType'] == 'Loan':
        required_fields = ['ExternalUserId', 'ItemInfo4', 'RequestType', 'ProcessType', 'LoanTitle', 'LoanAuthor', 'LoanDate']
    missing_fields = [field for field in required_fields if field not in transaction or not transaction[field]]
    
    if 'ItemInfo4' in missing_fields:
        missing_fields.remove('ItemInfo4')
        missing_fields.append('Pickup Location')
    
    if missing_fields:
        error = f'The following required fields are missing from the transaction: {", ".join(missing_fields)}.'
        #print(error)
        return error