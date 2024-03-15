from config import api_key, api_base
from transaction_templates import get_transaction_templates_csv, get_transaction_templates_ris
from illiad_api_utils import submit_transaction
from validation_utils import validate_row, validate_transaction
from file_utils import open_csv, open_ris, create_results_file

def create_transaction_csv(transaction_type, email, pickup, row):
    
    # Create a transaction using the appropriate template.
    transaction_templates = get_transaction_templates_csv(email, pickup, row)
    if transaction_type in transaction_templates:

        # If the Type column contains a valid value, create a transaction using the appropriate template.
        # If the CSV file contains a value for a column, use that value. If not, it will be set to ''.
        transaction = {k: row.get(v, v) for k, v in transaction_templates[transaction_type].items()}
        return transaction, None

    # If the Type column contains an invalid value, print an error message and move to the next row.
    else:
        error = f'The Type field must contain either "article" or "book".'
        #print(error)
        return None, error

def process_transaction_csv(email, filename, filepath, pickup, test_mode):
    
    if test_mode:
        print('Running in test mode. Transactions will be included in the results file but not submitted.\n')
    
    print('Processing transactions...\n')

    # Open the file as a CSV reader object.    
    with open(filepath, 'r') as source_file:
        reader = open_csv(source_file)

        # Create a new file for the results.
        with open('results.csv', 'w', newline='') as resultsfile:
            writer = create_results_file(reader, resultsfile)
            
            # Create and process a transaction for each row in the reader object.
            for i, row in enumerate(reader, start=1):

                result = {'Line number': i, 'Error': None, 'Transaction': None, 'Transaction number': None}

                # Validate the row.    
                result['Error'] = validate_row(row)
                
                # If there are no errors in the row, create a transaction.
                if not result['Error']:
                    transaction_type = str.lower(row['Type'])
                    result['Transaction'], result['Error'] = create_transaction_csv(transaction_type, email, pickup, row)

                # Validate the transaction.
                if not result['Error']:
                    result['Error'] = validate_transaction(result['Transaction'])
                
                # If there are any errors, write them to the results file.
                # Transaction will not be submitted if there are errors.
                if result['Error']:
                    writer.writerow(result)
                    print(f'Row {i}: ' + result['Error'] + '\n')
                    continue
                
                # If in test mode, write to the results file.
                if test_mode:
                    writer.writerow(result)
                    print(f'Row {i}: Created the following transaction data: ' + str(result['Transaction']) + '\n')

                # If not in test mode, submit the transaction and append the results file.
                if not test_mode:        
                    result['Transaction number'], result['Error'] = submit_transaction(result['Transaction'], api_base, api_key, i)
                    writer.writerow(result)
                    print(f'Row {i}: Created transaction number {result["Transaction number"]}' + '\n')

    print('\nProcessing complete.')
    print('Results have been saved to results.csv.\n')

def create_transaction_ris(transaction_type, email, pickup, entry):
    
    # Create a transaction using the appropriate template.
    transaction_templates = get_transaction_templates_ris(email, pickup, entry)
    if transaction_type in transaction_templates:

        # If the Type column contains a valid value, create a transaction using the appropriate template.
        # If the CSV file contains a value for a column, use that value. If not, it will be set to ''.
        transaction = {k: entry.get(v, v) for k, v in transaction_templates[transaction_type].items()}
        return transaction, None

    # If the Type column contains an invalid value, print an error message and move to the next row.
    else:
        error = f'The Type field must contain one of the following values: {", ".join(transaction_templates.keys())}'
        #print(error)
        return None, error

def process_transaction_ris(email, filename, filepath, pickup, test_mode):
    
    if test_mode:
        print('Running in test mode. Transactions will be included in the results file but not submitted.\n')
    
    print('Processing transactions...\n')

    # Open the file as a RIS reader object.    
    with open(filepath, 'r') as source_file:
        reader = open_ris(source_file)

        # Create a new file for the results.
        with open('results.csv', 'w', newline='') as resultsfile:
            writer = create_results_file(reader, resultsfile)
            
            # Create and process a transaction for each row in the reader object.
            for i, entry in enumerate(reader, start=1):

                result = {'Line number': i, 'Error': None, 'Transaction': None, 'Transaction number': None}

                # TODO: Create a function to validate the row.
                # Validate the row.    
                
                # If there are no errors in the row, create a transaction.
                #if not result['Error']:
                transaction_type = entry['type_of_reference']
                result['Transaction'], result['Error'] = create_transaction_ris(transaction_type, email, pickup, entry)

                # Validate the transaction.
                if not result['Error']:
                    result['Error'] = validate_transaction(result['Transaction'])
                
                # If there are any errors, write them to the results file.
                # Transaction will not be submitted if there are errors.
                if result['Error']:
                    writer.writerow(result)
                    print(f'Row {i}: ' + result['Error'] + '\n')
                    continue
                
                # If in test mode, write to the results file.
                if test_mode:
                    writer.writerow(result)
                    print(f'Row {i}: Created the following transaction data: ' + str(result['Transaction']) + '\n')

                # If not in test mode, submit the transaction and append to the results file.
                if not test_mode:        
                    result['Transaction number'], result['Error'] = submit_transaction(result['Transaction'], api_base, api_key, i)
                    writer.writerow(result)
                    print(f'Row {i}: Created transaction number {result["Transaction number"]}' + '\n')