"""Utility functions used by the data extractor.

Includes helpers to locate `.txt` files, extract Q/A pairs from files
using a simple heuristic, and write the results to JSON. Existing
implementation is preserved; only documentation/comments were added.
"""

from pathlib import Path
import re
import json


def search_txt_files(dir_path: str, files=None):
    """Recursively collect `.txt` files under `dir_path`.

    Returns a list of `Path` objects. The `files` argument is used for
    recursion to accumulate results.
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

def extract_qna_pairs(txt_file_paths: list[Path]):

    """Extract question/answer pairs from the given list of text files.

    The function reads each file (ignoring decoding errors), splits the
    text using a simple regex-based heuristic and delegates block
    processing to `create_qna_pairs`.
    """

    qna_pairs = []

    for txt_file in txt_file_paths:

        # some source files contain non-standard characters; ignore errors
        with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:

            raw_text = f.read()

            # split by the lines that start with Q/q or A/a
            split_text = re.split(r'(\n[AaQq].?\n)', raw_text)

            # drop any leading fragments until we hit a Q/A marker
            while split_text and re.search(r'^([AaQq].?)$', split_text[0].strip()) is None:
                split_text.pop(0)

            qna_pairs = qna_pairs + create_qna_pairs(split_text)

    return qna_pairs



def create_qna_pairs(split_txt_list: list):

    """Convert a split text list into a sequence of Q/A dictionaries.

    The function scans the list in windows expecting the pattern:
    [Q_marker, question, A_marker, answer]. If the pattern is not found
    the window advances by two to attempt realignment.
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
            # realign assumption: skip two elements when pattern not found
            i += 2

    return pair_storage
        


def create_json(pair_list, save_loc=Path.cwd(), mode='w'):
    """Write `pair_list` to a JSON file named `data.json` in `save_loc`.

    `save_loc` may be a directory path or string; the function appends
    `/data.json` to the provided location.
    """

    save_loc = str(save_loc) + '/data.json'

    with open(save_loc, mode) as file:
        json.dump(pair_list, file, indent=4)
        
        
        

