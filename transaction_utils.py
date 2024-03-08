import csv
from config import api_key, api_base
from transaction_templates import get_transaction_templates
from illiad_api_utils import check_user, submit_transaction
from validation_utils import validate_file, validate_row, validate_transaction

def create_transaction(transaction_type, email, pickup, row):
    
    # Create a transaction using the appropriate template.
    transaction_templates = get_transaction_templates(email, pickup, row)
    if transaction_type in transaction_templates:

        # If the Type column contains a valid value, create a transaction using the appropriate template.
        # If the CSV file contains a value for a column, use that value. If not, use the default value from the template.
        transaction = {k: row.get(v, v) for k, v in transaction_templates[transaction_type].items()}
        return transaction, None

    # If the Type column contains an invalid value, print an error message and move to the next row.
    else:
        error = f'The Type column must contain either "article" or "book".'
        #print(error)
        return None, error

def process_transaction_csv(email, filename, filepath, pickup, test_mode):
    
    if test_mode:
        print('Running in test mode. Transactions will be included in the results file but not submitted.\n')
    
    print('Processing transactions...\n')

    # Open the file as a CSV reader object.    
    with open(filepath, 'r') as csvfile:
        reader = csv.DictReader(csvfile)

        # Create a new file for the results.
        with open('results.csv', 'w', newline='') as resultsfile:
            writer = None

            # Create a header row for the results file.
            fieldnames = reader.fieldnames + ['Error', 'Transaction', 'Transaction number']
            writer = csv.DictWriter(resultsfile, fieldnames=fieldnames)
            writer.writeheader()
        
            # Create and process a transaction for each row in the reader object.
            for i, row in enumerate(reader, start=1):

                result = {'Error': None, 'Transaction': None, 'Transaction number': None}

                # Validate the row.    
                result = {'Error': validate_row(row)}
                
                # If there are no errors in the row, create a transaction.
                if not result['Error']:
                    transaction_type = str.lower(row['Type'])
                    result['Transaction'], result['Error'] = create_transaction(transaction_type, email, pickup, row)

                # Validate the transaction.
                if not result['Error']:
                    result['Error'] = validate_transaction(result['Transaction'])
                
                # If there are any errors, append them to the original row and write to the results file.
                # Row will not be submitted if there are errors.
                if result['Error']:
                    row.update(result)
                    writer.writerow(row)
                    print(f'Row {i}: ' + result['Error'] + '\n')
                    continue
                
                # If in test mode, append the transaction to the original row and write to the results file.
                if test_mode:
                    row.update(result)
                    writer.writerow(row)
                    print(f'Row {i}: Created the following transaction data: ' + str(result['Transaction']) + '\n')

                # If not in test mode, submit the transaction and append the results to the original row.
                if not test_mode:        
                    result['Transaction number'], result['Error'] = submit_transaction(result['Transaction'], api_base, api_key, i)
                    row.update(result)
                    writer.writerow(row)
                    print(f'Row {i}: Created transaction number {result["Transaction number"]}' + '\n')

    print('\nProcessing complete.')
    print('Results have been saved to results.csv.\n')