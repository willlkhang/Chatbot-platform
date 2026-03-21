from ai.data_extractor.tools import extract_funcs as ef

"""
for internal development use
"""

def run_extraction(directory_path, save_location='.'):
    
    txt_files = ef.search_txt_files(directory_path)
    
    print('Found the following text files:')
    for file in txt_files:
        print(file.name)
        
    pair_list = ef.extract_qna_pairs(txt_files)
    
    ef.create_json(pair_list=pair_list, save_loc=save_location)
    
    print(f'Successfully saved data to {save_location}')