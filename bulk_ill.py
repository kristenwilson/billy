#!/usr/bin/env python3
# bulk_ill.py
# Purpose: Input citations from a .csv file and create interlibrary loan transactions in ILLiad for each citation.
# Author: Kristen Wilson, NC State Libraries

from config import api_key, api_base
from args import get_args
from illiad_api_utils import check_user
from validation_utils import validate_file
from transaction_utils import process_transaction_csv, process_transaction_csv
     
def main():
    email, filename, pickup, test_mode = get_args()
    filepath = validate_file(filename)
    check_user(email, api_base, api_key)
    process_transaction_csv(email, filename, filepath, pickup, test_mode)

if __name__ == '__main__':
    main()