from pathlib import Path
import re 
import json

def search_txt_files(dir_path : str, files=None):
    
    """
    Searches a directory path and returns a list of txt file paths
    from the directory.
    """
    
    # creates an initial list to store the found txt files
    if files is None:
        files = list()
    
    # turns string path into a Path object
    current_dir = Path(dir_path)
    
    if not current_dir.is_dir():
        return files
    
    # recursively searches for text files from starting directory
    for item in current_dir.iterdir():
        
        if item.is_file() and re.search(r'\.txt', item.name):
            files.append(item)
        elif item.is_dir():
            search_txt_files(str(item), files)
            
    return files

def extract_qna_pairs(txt_file_paths : list[Path]):
    
    """
    Returns all QnA pairs findable from the list of txt files.
    
    The pairs are returned as a list of {Q: (Question), A: (Answer)}.
    """
    
    qna_pairs = []
    
    for txt_file in txt_file_paths:
        
        # shri's files use weird apostrophes that we cant easily, so we ignore errors
        with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:
            
            raw_text = f.read()

            # split by the Q and A tag
            split_text = re.split(r'(\n[AaQq].?\n)', raw_text)
            
            while split_text and re.search(r'^([AaQq].?)$', split_text[0].strip()) is None:
                split_text.pop(0) 
            
            qna_pairs = qna_pairs + create_qna_pairs(split_text)
    
    return qna_pairs



def create_qna_pairs(split_txt_list : list):
    
    """
    Creates QnA pairs from list of text in pattern (Q, question, A, answer).
    
    Data is returned as {Q: (Question), A: (Answer)} pairs.
    
    NOTE: gemini created this logic, I just wrote it to be cleaner.
    
    How it works:
    
    1. Checks list via index in blocks of 4.
    2. For each block, checks if position 1 is 'Q' and position 2 is 'A'
    3. If both are true, this is a valid block, it gets collected as a QnA pair.
    4. If not, we assume there's an issue with the list and move two steps forward
       to try realign again.
    
    """
    
    pair_storage = []
    
    i = 0
    while i < len(split_txt_list) - 3:
        
        Q = split_txt_list[i].strip()
        A = split_txt_list[i + 2].strip()
            
        is_Q = re.search(r"^([Qq].?)$", Q) is not None
        is_A = re.search(r"^([Aa].?)$", A) is not None
        
        if is_Q and is_A:
            
            question = split_txt_list[i + 1].strip()
            answer = split_txt_list[i + 3].strip()
            
            pair_storage.append({'Q': question, 'A': answer})
            
            i += 4
        else:
            i += 2
        
    return pair_storage
        


def create_json(pair_list, save_loc= Path.cwd() , mode='w'):
    
    """
    Creates a json file from a list
    """
    save_loc = str(save_loc) +  '/data.json'
    
    with open(save_loc, mode) as file:
        json.dump(pair_list, file, indent=4)
        
        
        

