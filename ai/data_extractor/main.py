"""
extracts QnA stuff from shri's files.

Usage: python main.py <any directory file path> <data save location> 
Usage E.g: (windows cmd) python main.py 
Output: Data.json
"""

import argparse
from src import extract_funcs as ef

def main():
    
    parser = argparse.ArgumentParser(description="Extracts data from .txt files in QnA format.")
    
    parser.add_argument('-d', '--directory', required=True, help='The directory path to extract data from')
    parser.add_argument('-l', '--location', default='data.json', required=False, help='The destination file path to save the JSON')
    
    args = parser.parse_args()
    
    directory_path = args.directory
    save_location = args.location
    
    txt_files = ef.search_txt_files(directory_path)
    
    print('Found the following text files:')
    for file in txt_files:
        print(file.name)
        
    pair_list = ef.extract_qna_pairs(txt_files)
    
    ef.create_json(pair_list=pair_list, save_loc=save_location)
    
    print(f'Successfully saved data to {save_location}')
    
if __name__ == "__main__":
    main()

