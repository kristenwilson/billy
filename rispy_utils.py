#!/usr/bin/env python3
# rispy_utils.py
# Description: Utilities to help with parsing RIS files using the rispy library, for use with the bulk_ill.py script.
# Author: Kristen Wilson, NC State University Libraries, kmblake@ncsu.edu

from copy import deepcopy
try:
    import rispy
except ImportError:
    print('The rispy library is required for this script. Please install it with "pip install rispy".')
    exit()

# Maps RIS tags to the key names used by the transaction_templates.py script.
def map_rispy(filepath):
    mapping = deepcopy(rispy.TAG_KEY_MAPPING)
    
    # Author mappings
    mapping["AU"] = "authors" # This is the default mapping for authors, but it is included here for clarity.
    mapping["A1"] = "authors" # The 'A1' field is often used interchangably with 'AU'.

    # Secondary title mappings
    # Secondary title fields are typically used as the journal or book title when the citation is for an article or chapter, respectively.
    mapping["T2"] = "secondary_title" # This is the default mapping for secondary titles, but it is included here for clarity.
    mapping["JF"] = "secondary_title" # The 'JF' field is used by Summon secondary titles.
    
    # Primary title mappings
    # Primary title fields are typically used as the title of the article or chapter in those types of citations.
    # For book citations, the primary title is the title of the book.
    mapping["T1"] = "primary_title" # This is the default mapping for primary titles, but it is included here for clarity.
    mapping["TI"] = "primary_title" # The 'TI' field is often used when there is only one title.

    # Year mappings
    mapping["PY"] = "year" # This is the default mapping for years, but it is included here for clarity.
    mapping["Y1"] = "year" # The 'Y1' field is often used interchangably with 'PY'.
    
    with open(filepath, 'r') as bibliography_file:
        entries = rispy.load(bibliography_file, mapping=mapping)
    return entries