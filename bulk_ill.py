#!/usr/bin/env python3
# bulk_ill.py
# Description: This script processes citations from a .csv or .ris file and creates interlibrary loan transactions in ILLiad for each citation.
# Author: Kristen Wilson, NC State Libraries, kmblake@ncsu.edu

# Built-in modules
from args import get_args

# Custom modules
from illiad_api_utils import check_user
from validation_utils import validate_file, validate_file_type
from transaction_utils import process_transaction

# Configuration
from config import api_key, api_base
     
def main():
    # Get command line arguments
    email, filename, pickup, test_mode = get_args()
    
    # Validate that the file exists and store the full filepath.
    filepath = validate_file(filename)
    
    # Validate the filetype and user account.
    filetype = validate_file_type(filename, filepath)
    check_user(email, api_base, api_key)
    
    # Process the file
    process_transaction(filetype, email, filename, filepath, pickup, test_mode)


if __name__ == '__main__':
    main()