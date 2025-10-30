import os
import csv
from config import DATA_FILES_DIR
import logging
from exceptions import BillyFileNotFoundError, InvalidFileError, EmptyFileError

logger = logging.getLogger(__name__)
REQUIRED_CSV_COLUMNS = {"Item Type"}


def validate_file(filename: str, messages: list) -> tuple:
    """
    Validates the input file and determines its type (CSV or RIS).
    Returns the absolute filepath, filetype, and messages.
    Raises exceptions on failure.
    """
    # Construct the filepath of the user's file.
    filepath = os.path.join(DATA_FILES_DIR, filename)

    # If the file doesn't exist, raise an error.
    if not os.path.isfile(filepath):
        logger.error("File not found: %s", filepath)
        raise BillyFileNotFoundError(f"The file {filepath} does not exist.")

    # Verify that the file is either a RIS or CSV file.
    filetype = None
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            first_line = file.readline().strip()
            
            # Skip blank lines at the beginning of the file.
            while not first_line:
                first_line = file.readline().strip()
                # Check if the file is empty
                if not first_line:
                    if file.tell() == 0:
                        logger.error("Empty file: %s", filepath)
                        raise EmptyFileError(f"The file {filepath} is empty.")
            
            
            # If the first line of the file is a RIS 'type' tag, the file is treated as an RIS file.
            if 'TY  -' in first_line:
                filetype = 'ris'
                messages.append('RIS file confirmed.')
            
            # If there is a comma in the first line, the file is treated as a CSV file.
            elif ',' in first_line:
                try:
                    file.seek(0)
                    reader = csv.DictReader(file)

                    # Check that the file contains required columns and if not, exit the script.
                    missing = REQUIRED_CSV_COLUMNS - set(reader.fieldnames or [])
                    if missing:
                        logger.error("Missing %s column in CSV: %s", {', '.join(sorted(missing))}, filepath)
                        raise InvalidFileError(f"CSV is missing required columns: {', '.join(sorted(missing))}")
                    
                    filetype = 'csv'
                    messages.append('CSV file confirmed.')
                # If the file is not a valid CSV file, exit the script.
                except csv.Error as e:
                    logger.error("CSV parsing error: %s - %s", filepath, str(e))
                    raise InvalidFileError(f"The file {filepath} is not a valid CSV file: {str(e)}")
            
            # If the file is not a valid RIS or CSV file, exit the script.
            else:
                logger.error("Invalid file type: %s", filepath)
                raise InvalidFileError(f"The file {filename} is not a valid file type. Must be CSV or RIS.")
    except (OSError, IOError) as e:
        logger.error("I/O error reading file: %s - %s", filepath, str(e))
        raise BillyFileNotFoundError(f"Error reading file {filepath}: {str(e)}")
    return filepath, filetype, messages

def read_csv(filepath: str):
    """
    Generator that yields each row from a CSV file as a dict.
    """
    with open(filepath, 'r', encoding='utf-8') as source_file:
        reader = csv.DictReader(source_file)
        for row in reader:
            yield row