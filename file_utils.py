import csv
import rispy

def open_csv(source_file):
    reader = csv.DictReader(source_file)
    return reader
    
def open_ris(source_file):
    reader = rispy.load(source_file)
    return reader
    
def create_results_file(reader, resultsfile):
    writer = None
    # Create a header row for the results file.
    fieldnames = ['Line number', 'Error', 'Transaction', 'Transaction number']
    writer = csv.DictWriter(resultsfile, fieldnames=fieldnames)
    writer.writeheader()
    return writer