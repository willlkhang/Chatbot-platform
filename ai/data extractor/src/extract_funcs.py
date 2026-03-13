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
        
        if item.is_file and re.search(r'\.txt', item.name):
            files.append(item)
        elif item.is_dir():
            search_txt_files(str(item), files)
            
    return files




def extract_qna_pairs(txt_file_paths : list[Path]):
    
    """
    Returns all QnA pairs findable from the list of txt files.
    
    The pairs are returned as a list of {Q: (Question), A: (Answer)}.
    """
    
    text = []
    
    for txt_file in txt_file_paths:
        
        # shri's files use weird apostrophes that we cant easily, so we ignore errors
        with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:
            
            raw_text = f.read()

            # split by the Q and A tag
            split_text = re.split(r'(\n[AaQq].?\n)', raw_text)
           
            create_qna_pairs(split_text, text)
    
    return text



def create_qna_pairs(split_txt_list : list, pair_storage : list):
    
    """
    Creates QnA pairs from raw txt files which have been split and appends them to a pair storage list.
    
    Data is returneda as {Q: (Question), A: (Answer)} pairs.
    
    Expects split_txt_list to be a list of strings returned from using re.split(r'(AaQq).?') on raw text.
    
    I am assuming that that QnA are in sequence always.
    """
    
    # removes beginning text which has no QnA pairing
    while split_txt_list and re.search(r'([AaQq].?)', split_txt_list[0].strip()) is None:
        split_txt_list = split_txt_list[1::]
    
    # slice 4 since we're expecting split_txt_files to have a pattern of [Q, (question_str), A, (answer_str)]
    while len(split_txt_list) >= 4:
        
        # getting [Q, (question_str), A, (answer_str)]
        pair = split_txt_list[:4:]
        
        A = pair[1].strip()
        Q = pair[3].strip()
        
        # getting rid of really tiny QnA (and corrupted text)
        if len(A) > 5 and len(Q) > 5:
            pair_storage.append({'Question' : A, 'Answer' : Q})

        # shortening the list to get the next pair
        split_txt_list = split_txt_list[4::]
        


def create_json(pair_list, mode='w'):
    
    """
    Creates a json file from a list
    """
    with open('data.json', mode) as file:
        json.dump(pair_list, file, indent=4)
        
        
        

