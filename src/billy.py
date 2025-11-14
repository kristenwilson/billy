#!/usr/bin/env python3
"""
billy.py - Main entry point for the Bulk ILL (Billy) application.

This module orchestrates the complete workflow: parsing command-line arguments, validating
input files, checking user credentials, processing citations, and creating ILLiad transactions.

The script supports multiple modes:
- Normal mode: submit transactions to ILLiad API.
- Test mode (-t): validate and output results without submitting.
- Developer mode (--dev): console logging, deterministic output filenames, no submissions.

Exit codes indicate failure categories for scripting/CI integration:
- 0: Success - no per-entry errors.
- 1: Unexpected/unhandled error.
- 2: User account problems - not found, not cleared.
- 3: File/validation errors.
- 4: API/external system errors.
- 5: Per-entry processing errors recorded.
- 6: Configuration errors.

Author: Kristen Wilson, NC State Libraries, kmblake@ncsu.edu
Editor: Aditi Singh, NC State Libraries, asingh39@ncsu.edu
"""

import argparse
import os
import sys
import csv
import datetime
import logging

from rispy_mapping import map_rispy
from transaction_templates import map_citation_type
from file_utils import validate_file, read_csv
from api import check_user, submit_transaction
from transaction import create_transaction, validate_transaction
from logging_utils import setup_logging
from typing import List, Tuple, Optional
from config import settings
from exceptions import (
    BillyError,
    TransactionSubmissionError,
    APIError,
    APIAuthenticationError,
    UserNotFoundError,
    UserNotClearedError,
    BillyFileNotFoundError,
    InvalidFileError,
    EmptyFileError,
    ValidationError,
    ConfigError,
)



logger = logging.getLogger(__name__)


def get_args() -> Tuple[str, str, str, bool, bool]:
    """
    Parse and validate command-line arguments.

    This function sets up argument parsing with required and optional parameters.
    Mutually exclusive flags (-t/--test and --dev) ensure the script runs in only
    one mode at a time.

    Returns:
        Tuple (email, filename, pickup, test_mode, dev_mode).
        - email: User email address for the request.
        - filename: Input file name (CSV or RIS).
        - pickup: Pickup location (or empty string if not provided).
        - test_mode: True if -t/--test flag is set.
        - dev_mode: True if --dev flag is set.

    Raises:
        SystemExit: On argument parse error or mutually exclusive flag conflict.
    """
    
    parser = argparse.ArgumentParser(
        description='Create interlibrary loan transactions in ILLiad for articles in a CSV or RIS file.'
    )
    parser.add_argument(
        'email', 
        help='The email address of the person who will receive the requested materials. ' \
        'This person must already have a user account in ILLiad.'
    )
    parser.add_argument(
        'filename', 
        help='The name of the file to be read. Must be a .csv or .ris file.'
    )
    parser.add_argument(
        '-p', '--pickup', 
        help='The library where the requested materials will be picked up.' \
        ' This is only needed if you are requesting physical materials.',
        choices=settings.pickup_locations,
        default=''
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-t', 
        '--test', 
        action='store_true',
        help='Run the script in test mode to output a report showing ' \
        'which transactions will be created and which will produce errors.'
    )
    group.add_argument(
        '--dev', 
        action='store_true',
        help='Developer mode: console logging only, deterministic filename, no submissions.'
    )
    args = parser.parse_args()    
    
    return args.email, args.filename, args.pickup, args.test, args.dev


def process_transaction(
    filetype: str,
    email: str,
    filename: str,
    filepath: str,
    pickup: str,
    test_mode: bool,
    dev_mode: bool,
    messages: List[str],
) -> None:
    """
    Process citations from a file and create ILLiad transactions.

    This function is the core processing loop. For each citation entry, it:
    1. Maps the citation type to a standardized transaction type.
    2. Creates a transaction payload from the entry.
    3. Validates the transaction (required fields).
    4. Either submits the transaction (normal mode) or records it (test/dev mode).

    All results (success or error) are written to a results CSV file for review.
    Per-entry errors do not abort processing; the loop continues to the next entry.

    Args:
        filetype: Either 'csv' or 'ris' (determines parsing method).
        email: User email (included in all transactions).
        filename: Original input filename (used in results filename).
        filepath: Full path to the input file.
        pickup: Pickup location (required for some request types).
        test_mode: If True, write results but do not submit.
        dev_mode: If True, use console logging, deterministic filename, no submissions.
        messages: List to append human-readable status/error messages.

    Raises:
        Does not raise; all errors are caught, recorded in results, and messages are appended.
    """
    # Compute effective test/dev mode (either flag disables submission)
    testing = test_mode or dev_mode

    # Log which mode the script is running in
    if dev_mode:
        messages.append('Running in developer test mode (console logging). Transactions will not be submitted.')
    elif test_mode:
        messages.append('Running in test mode. Transactions will be included in the results file but not submitted.')

    # Determine output directory (based on mode) exists.
    if dev_mode:
        results_root = settings.test_results_dir
    else:
        results_root = settings.results_dir

    if not os.path.exists(results_root):
        os.makedirs(results_root)
    
    # Construct the filepath for the results file: deterministic for dev mode, timestamped for test/normal mode.
    base_filename = os.path.splitext(filename)[0]
    if dev_mode:
        results_filename = f'{base_filename}_actual.csv'
    else:
        # Get the current date and time to the nearest second for use in filename
        now = datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
        results_filename = f'{base_filename}_{now}_results.csv'
    results_filepath = os.path.join(results_root, results_filename)

    messages.append(f'Results saved to {results_filepath}')

    # Create a new file for the results.
    with open(results_filepath, 'w', encoding='utf-8', newline='') as resultsfile:
        writer = None
        # Create a header row for the results file.
        fieldnames = [
            'Entry number', 
            'Title', 
            'Author', 
            'Error', 
            'Transaction', 
            'Transaction number'
        ]
        writer = csv.DictWriter(resultsfile, fieldnames=fieldnames)
        writer.writeheader()

        # Initialize the result dictionary.
        result = {
            'Entry number': None, 
            'Title': None, 
            'Author': None, 
            'Error': None, 
            'Transaction': None, 
            'Transaction number': None
        }

        # Store the citations from the file in a list.
        # RIS citations will be mapped to standardized keys via map_rispy
        if filetype == 'ris':
            citations = map_rispy(filepath)
        elif filetype == 'csv':
            citations = list(read_csv(filepath))
       
        # Process a transaction for each entry.
        for i, entry in enumerate(citations, start=1):
        
            # Get the citation type from the source file.
            if filetype == 'ris':
                citation_type = entry['type_of_reference']
            elif filetype == 'csv':
                citation_type = str.lower(entry['Item Type'])
            
            # Map the transaction type from the input file to the standardized values.
            # map_citation_type returns None if type is unrecognized.
            transaction_type, illiad_request_type, illiad_doc_type = map_citation_type(citation_type)

            # Create the transaction based on the transaction type.
            result['Transaction'], result['Error'], result['Title'], result['Author'] = create_transaction(filetype, transaction_type, illiad_request_type, illiad_doc_type, email, pickup, entry)

            # Log transaction for diagnostics
            logger.info("Transaction: %s", result['Transaction'])

            # Validate the transaction.
            if not result['Error']:
                result['Error'] = validate_transaction(result['Transaction'])
    
            # If there are any errors, write them to the results file.
            # Transaction will not be submitted if there are errors.
            if result['Error']:
                logger.info("Errors: %s", result['Error'])
                writer.writerow(result)
                messages.append(f'Entry {i}: ' + result['Error'])
                continue
            
            # No errors: proceed to submission or test recording.
            result["Error"] = "No errors"

            # If in dev/test mode, only append the transaction results to the results file without submitting.
            if testing:
                result['Transaction number'] = 'n/a'
                writer.writerow(result)
                messages.append(f'Entry {i}: Created the following transaction data: ' + str(result['Transaction']))
                logger.info(f"Transaction submitted: {result['Transaction number']}")

            # If in normal mode, attempt to submit the transaction and append the transaction results to the results file.
            if not testing:        
                try:
                    result['Transaction number'], result['Error'] = submit_transaction(result['Transaction'], settings.api_base, settings.api_key, i)
                except TransactionSubmissionError as e:
                    # Per-entry submission failure: record error and continue.
                    logger.error("Submission failed for entry %s: %s", i, e)
                    result['Transaction number'] = None
                    result['Error'] = str(e)
                
                writer.writerow(result)
                if result['Transaction number']:
                    messages.append(f'Entry {i}: Created transaction number {result["Transaction number"]}')
                else:
                    messages.append(f'Entry {i}: {result["Error"]}')        

def main(
    email: Optional[str] = None,
    filename: Optional[str] = None,
    pickup: Optional[str] = None,
    test_mode: Optional[bool] = None,
    dev_mode: Optional[bool] = None,
) -> None:
    """
    Main entry point: orchestrate the entire workflow.

    This function parses arguments, initializes logging, validates inputs, and coordinates
    the processing pipeline. It handles exceptions at the top level, mapping them to
    user-facing messages and exit codes.

    Args:
        email: User email (optional; parsed from CLI if None).
        filename: Input filename (optional; parsed from CLI if None).
        pickup: Pickup location (optional; parsed from CLI if None).
        test_mode: Test flag (optional; parsed from CLI if None).
        dev_mode: Developer flag (optional; parsed from CLI if None).

    Exit codes:
        0: Success (no per-entry errors).
        1: Unexpected/unhandled error.
        2: User account problems (not found, not cleared).
        3: File/validation errors.
        4: API/external system errors.
        5: Per-entry processing errors recorded.
        6: Configuration errors.
    """
    
    messages: List[str] = []
    
    # Get command line arguments
    if email is None or filename is None or pickup is None or test_mode is None or dev_mode is None:
        email, filename, pickup, test_mode, dev_mode = get_args()
    
    # Initialize logging (console-only for dev mode, file for others)
    log_file_path = os.path.join(os.path.dirname(__file__), "billy.log")
    if dev_mode:
        setup_logging(log_file=log_file_path, console_only=True, secrets=[settings.api_key])
    else:
        setup_logging(log_file=log_file_path, console=False, secrets=[settings.api_key])
        
    logger.info('Processing initiated')
    logger.info(f'Arguments: email={email}, filename={filename}, pickup={pickup}, test_mode={test_mode}, dev_mode={dev_mode}')
      

    try:
        # Validate the file and get file type.
        filepath, filetype, messages = validate_file(filename, messages)

        # Check that the user exists and is cleared to request materials
        messages = check_user(email, settings.api_base, settings.api_key, messages)
        
        # Process citations and create transactions.
        process_transaction(filetype, email, filename, filepath, pickup, test_mode, dev_mode, messages)
    
    # User-related errors: account doesn't exist or isn't cleared
    except (UserNotFoundError, UserNotClearedError) as e:
        messages.append(str(e))
        logger.error(str(e))
        for message in messages:
            print(message)
        sys.exit(2)
    
    # File/validation errors: missing file, bad format, validation failed
    except (BillyFileNotFoundError, InvalidFileError, EmptyFileError, ValidationError) as e:
        messages.append(str(e))
        logger.error(str(e))
        for message in messages:
            print(message)
        sys.exit(3)

    # API/external system errors: auth failure, connection, server, submission
    except (APIAuthenticationError, APIError, TransactionSubmissionError) as e:
        messages.append(str(e))
        # log traceback for diagnosis but show a concise user message
        logger.exception("API error (see log for details)")
        for message in messages:
            print(message)
        sys.exit(4)
    
    # Configuration errors: missing/invalid config values
    except ConfigError as e:
        messages.append(str(e))
        logger.error(str(e))
        for message in messages:
            print(message)
        sys.exit(6)

     # Generic Billy error (fallback for unmapped BillyError subclasses)
    except BillyError as e:
        messages.append(str(e))
        logger.error(str(e))
        for message in messages:
            print(message)
        sys.exit(3)

    # Unexpected errors
    except Exception as e:
        messages.append(f'Unexpected error: {str(e)}')
        logger.exception('Unexpected error')
        for message in messages:
            print(message)
        sys.exit(1)

    # Print collected messages to user
    if not dev_mode:
        for message in messages:
            print(message)
    else:
        logger.info(f"Developer test mode: {len(messages)} messages printed to cmd (not billy.log).")

    # Exit with non-zero code if any per-entry errors were recorded.
    if any('Error' in (message or '') for message in messages):
        sys.exit(5)

if __name__ == '__main__':
    main()