#!/usr/bin/env python3
"""
rispy_mapping.py - RIS file parsing and field mapping utilities.

This module provides utilities for parsing RIS (Research Information Systems) bibliographic
files using the rispy library. It handles the mapping of RIS tags to standardized field names
used by transaction_templates.py.

RIS is a widely-used citation format supported by major databases (ProQuest, JSTOR, Summon, etc.)
and reference managers (Zotero, Mendeley, EndNote). Different sources may use variant RIS tags
for the same field (e.g., 'AU' vs 'A1' for authors, 'DOI' vs 'DO' for DOI). This module
normalizes these variants to a consistent set of keys.

Notes:
- The rispy library must be installed (pip install rispy).
- Field mapping is case-sensitive and must match RIS tag conventions exactly.
- Authors are stored as a list; callers should join them for display (e.g., ', '.join(authors)).

Prerequisites:
- rispy library installed (see requirements.txt).

Author: Kristen Wilson, NC State Libraries, kmblake@ncsu.edu
Editor: Aditi Singh, NC State Libraries, asingh39@ncsu.edu
"""

from copy import deepcopy
from typing import List, Dict, Any
import logging

try:
    import rispy
except ImportError as e:
    raise ImportError('The rispy library is required for this script. Please install it with "pip install rispy".') from e

logger = logging.getLogger(__name__)

def map_rispy(filepath: str) -> List[Dict[str, Any]]:
    """
    Parse a RIS file and return entries with standardized field names.

    This function reads a RIS file and maps RIS tags to standardized field names
    used by transaction_templates.py. It handles common variant tags (e.g., 'AU' vs 'A1'
    for authors) by normalizing them to a single canonical name.

    The mapping includes:
    - Authors: 'AU', 'A1' -> 'authors' (list of strings)
    - DOI: 'DOI', 'DO' -> 'doi'
    - Primary title: 'T1', 'TI' -> 'primary_title' (article/chapter title, or book title)
    - Secondary title: 'T2', 'JF' -> 'secondary_title' (journal or book container)
    - Year: 'PY', 'Y1' -> 'year'
    - Plus standard rispy mappings (volume, issue, pages, publisher, etc.)

    Args:
        filepath: Path to the RIS file to parse.

    Returns:
        List of dicts, one per RIS entry. Each dict contains standardized field names
        (e.g., 'primary_title', 'authors', 'year') as keys.

    Raises:
        FileNotFoundError: If the RIS file does not exist.
        rispy.RISParserError: If the RIS file is malformed or cannot be parsed.
        IOError: If the file cannot be read (e.g., permissions issue).

     Notes:
        - Authors are returned as a list (rispy default behavior).
        - Empty or missing fields will not appear in the returned dicts.
        - Case sensitivity: RIS tags are uppercase (e.g., 'TY', 'AU', 'T1').
    """
    # Start with rispy's default tag-to-key mapping, then extend it with our custom mappings
    mapping = deepcopy(rispy.TAG_KEY_MAPPING)
    
    # Author mappings
    mapping["AU"] = "authors" # This is the default mapping for authors, but it is included here for clarity.
    mapping["A1"] = "authors" # The 'A1' field is often used interchangably with 'AU'.
    
    # DOI mappings
    mapping["DOI"] = "doi" # This is the default mapping for DOIs, but it is included here for clarity.
    mapping["DO"] = "doi" # The 'DO' field is often used interchangably with 'DOI'.

    # Primary title mappings
    # Primary title fields are typically used as the title of the article or chapter in those types of citations.
    # For book citations, the primary title is the title of the book.
    mapping["T1"] = "primary_title" # This is the default mapping for primary titles, but it is included here for clarity.
    mapping["TI"] = "primary_title" # The 'TI' field is often used when there is only one title.

    # Secondary title mappings
    # Secondary title fields are typically used as the journal or book title when the citation is for an article or chapter, respectively.
    mapping["T2"] = "secondary_title" # This is the default mapping for secondary titles, but it is included here for clarity.
    mapping["JF"] = "secondary_title" # The 'JF' field is used by Summon secondary titles.
    
    # Year mappings
    mapping["PY"] = "year" # This is the default mapping for years, but it is included here for clarity.
    mapping["Y1"] = "year" # The 'Y1' field is often used interchangably with 'PY'.
    
    # Open and parse the RIS file using the customized mapping.
    try:
        with open(filepath, "r", encoding="utf-8") as bibliography_file:
            entries = rispy.load(bibliography_file, mapping=mapping)
        return entries
    except FileNotFoundError:
        logger.error("RIS file not found: %s", filepath)
        raise
    except rispy.RISParserError as e:
        logger.error("Failed to parse RIS file %s: %s", filepath, str(e))
        raise
    except IOError as e:
        logger.error("I/O error reading RIS file %s: %s", filepath, str(e))
        raise