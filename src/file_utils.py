import os
import csv
from exceptions import BillyError

def validate_file(filename: str, messages: list) -> tuple:
    """
    Validates the input file and determines its type (CSV or RIS).
    Returns the absolute filepath, filetype, and messages.
    Raises BillyError on failure.
    """
    # Construct the filepath of the user's file.
    data_files_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data_files'))
    filepath = os.path.join(data_files_dir, filename)

    # If the file doesn't exist, raise an error.
    if not os.path.isfile(filepath):
        error_message = f'Error: The file {filepath} does not exist.\n'
        raise BillyError(error_message)

    # Verify that the file is either a RIS or CSV file.
    filetype = None
    with open(filepath, 'r', encoding='utf-8') as file:
        first_line = file.readline().strip()
        
        # Skip blank lines at the beginning of the file.
        while not first_line:
            first_line = file.readline().strip()
            # Check if the file is empty
            if not first_line:
                if file.tell() == 0:
                    error_message = 'Error: The file is empty.'
                    raise BillyError(error_message)
        
        # If the first line of the file is a RIS 'type' tag, the file is treated as an RIS file.
        if 'TY  -' in first_line:
            filetype = 'ris'
            messages.append('RIS file confirmed.')
        
        # If there is a comma in the first line, the file is treated as a CSV file.
        elif ',' in first_line:
            try:
                with open(filepath, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    
                    # Check that the file contains an 'Item Type' column and if not, exit the script.
                    if 'Item Type' not in reader.fieldnames:
                        error_message = 'Error: The file must contain a column called "Item Type".\n'
                        raise BillyError(error_message)
                    else:
                        filetype = 'csv'
                        messages.append('\nCSV file confirmed.')
            # If the file is not a valid CSV file, exit the script.
            except csv.Error:
                error_message = f'Error: The file {filepath} is not a valid CSV file.\n'
                raise BillyError(error_message)
        
        # If the file is not a valid RIS or CSV file, exit the script.
        else:
            error_message = f'Error: The file {filename} is not a valid file type. The file must be a CSV or RIS file.\n'
            raise BillyError(error_message)
    return filepath, filetype, messages

def read_csv(filepath: str):
    """
    Generator that yields each row from a CSV file as a dict.
    """
    with open(filepath, 'r', encoding='utf-8') as source_file:
        reader = csv.DictReader(source_file)
        for row in reader:
            yield row