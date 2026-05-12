"""Small wrapper that runs the extraction tools on a directory.

This module is a thin orchestration layer used by the CLI. It locates
`.txt` files, extracts QnA pairs and writes a JSON file to
`save_location`.
"""

from ai_tools.data_extractor.tools import extract_funcs as ef


def run_extraction(directory_path, save_location='.'):
    """Run the extraction pipeline for `directory_path`.

    Args:
        directory_path: directory to scan for `.txt` QnA files.
        save_location: destination path for the produced JSON file.
    """

    txt_files = ef.search_txt_files(directory_path)

    # print discovered files for visibility during runs
    print('Found the following text files:')
    for file in txt_files:
        print(file.name)

    # extract question/answer pairs from the detected files
    pair_list = ef.extract_qna_pairs(txt_files)

    # create a JSON file from the extracted pairs
    ef.create_json(pair_list=pair_list, save_loc=save_location)

    print(f'Successfully saved data to {save_location}')