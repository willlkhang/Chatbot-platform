"""
extracts QnA stuff from shri's files.

Usage: python main.py <any directory file path> (Eg. python main.py "./QnA Files)
Output: Data.json
"""

import sys
import txt_extract_tools as txtools

def main():
    
    if len(sys.argv) < 3:
        print('Enter a file path to a directory.')
        return
    
    directory_path = sys.argv[1]
    
    txt_files = txtools.search_txt_files(directory_path)
    
    print('Found the following text files:')
    for file in txt_files:
        print(file.name)
    
    pair_list = txtools.extract_qna_pairs(txt_files)
    
    txtools.create_json(pair_list)
    
    print('Created data.json')
    
if __name__ == "__main__":
    main()

