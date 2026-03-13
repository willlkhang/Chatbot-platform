"""
extracts QnA stuff from shri's files.

Usage: python main.py <any directory file path> (Eg. python main.py "./QnA Files)
Output: Data.json
"""

import sys
from src import extract_funcs as ef

def main():
    
    if len(sys.argv) < 3:
        print('Enter a file path to a directory.')
        return
    
    directory_path = sys.argv[1]
    
    txt_files = ef.search_txt_files(directory_path)
    
    print('Found the following text files:')
    for file in txt_files:
        print(file.name)
    
    pair_list = ef.extract_qna_pairs(txt_files)
    
    ef.create_json(pair_list)
    
    print('Created data.json')
    
if __name__ == "__main__":
    main()

