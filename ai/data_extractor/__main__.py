"""
extracts QnA stuff from shri's files.

Usage: python main.py <any directory file path> <data save location> 
Usage E.g: (windows cmd) python main.py 
Output: Data.json
"""

import argparse
import os
from ai.data_extractor.run_extractor import run_extraction

def main():
    
    parser = argparse.ArgumentParser(description="Extracts data from .txt files in QnA format.")
    parser.add_argument('-d', '--directory', required=True, help='The directory path to extract data from')
    parser.add_argument('-l', '--location', default=os.getcwd(), required=False, help='The destination file path to save the JSON')
    
    args = parser.parse_args()
    
    run_extraction(args.directory, args.location)
    
if __name__ == "__main__":
    main()

