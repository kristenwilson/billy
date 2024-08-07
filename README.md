# Billy - Bulk ILL, Y'all!
## Description
A Python script that creates ILLiad interlibrary loan (ILL) transactions from a file of citation data.

## Prerequisites
### Install required libraries
```python
python -m pip install -r requirements.txt
```
### ILLiad API
To connect to the ILLiad API, ask your ILLiad administrator to create an API key for this project. You will also need the base URL for your ILLiad system. It will look like `https://your.illiad.edu/ILLiadWebPlatform`.
### Config
Use `config.py.template` to create `config.py`. Fill in the values for your ILLiad API base URL and key.

## Usage
```python
python bulk_ill.py you@university.edu file.csv -p 'Pickup Location'
```
Use `-t` to run the script in test mode. This will output a list of transactions and errors to review before submitting.

Valid pickup locations include:
* 'Hill'
* 'Hunt'
* 'Design'
* 'Natural Resources'
* 'Veterinary Medicine'
* 'Textiles'
* 'METRC'
* 'Distance/Extension'

## RIS files
RIS is a format for citation data used by many major databases and library applications. Place any RIS files you want to process in the 'data_files' folder. Properly formatted RIS files should be processed without any additional intervention.

## CSV files
Place any CSV files you want to process in the 'data_files' folder. (This folder also contains a CSV template and test file.) 

The file you use with this script must be a plaintext .csv file. It can include a combination of request formats. Each row must contain the required fields (*) as defined by the value in the 'Item Type' field. 

This file format matches the default output from Zotero. If you are using a different citation manager, you may need to do some pre-processing to get your citation data into the correct format.

### Book request fields
* Item Type = 'book' *
* Title *
* Author *
* Publication Year*
* Publisher
* ISBN

### Journal article request fields
* Item Type='journalArticle' *
* Title *
* Publication Title *
* Author *
* Publication Year *
* Volume
* Issue
* Pages
* DOI
* ISSN

### Book chapter request fields
* Item Type='bookSection' *
* Title *
* Publication Title *
* Author *
* Publication Year *
* Pages
* ISBN

