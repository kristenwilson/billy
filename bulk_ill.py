#!/usr/bin/env python3
# bulk_ill.py
# Description: This script processes citations from a .csv or .ris file and creates interlibrary loan transactions in ILLiad for each citation.
# Author: Kristen Wilson, NC State Libraries, kmblake@ncsu.edu

# Built-in modules
from args import get_args

# Custom modules
from illiad_api_utils import check_user
from validation_utils import validate_file, validate_file_type
from transaction_utils import process_transaction_csv, process_transaction_ris

# Configuration
from config import api_key, api_base
     
def main():
    # Get command line arguments
    email, filename, pickup, test_mode = get_args()
    
    # Validate that the file exists and store the full filepath.
    filepath = validate_file(filename)
    
    # Identify the file type and verify that it contains a "type" field for each citation.
    filetype = validate_file_type(filename, filepath)
    check_user(email, api_base, api_key)
    
    # Process the file based on its type.
    if filetype == 'ris':
        process_transaction_ris(email, filename, filepath, pickup, test_mode)
    elif filetype == 'csv':
      process_transaction_csv(email, filename, filepath, pickup, test_mode)


if __name__ == '__main__':
    main()