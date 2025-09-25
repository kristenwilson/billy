import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access your variables
api_base = os.getenv("API_BASE")
api_key = os.getenv("API_KEY")

if not api_base:
    raise ValueError("API_BASE not found. Please set it in your .env file.")
if not api_key:
    raise ValueError("API_KEY not found. Please set it in your .env file.")

pickup_locations_str = os.getenv("PICKUP_LOCATIONS", "")
pickup_locations = [loc.strip() for loc in pickup_locations_str.split(",") if loc.strip()]
if not pickup_locations:
    raise ValueError("PICKUP_LOCATIONS not found. Please set it in your .env file.")


DATA_FILES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data_files'))
RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data_files', 'results'))
TEST_RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'test', 'data', 'actual'))