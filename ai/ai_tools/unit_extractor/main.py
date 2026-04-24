from controllers import UnitExtractor
from controllers import Serializer

from extractors import TextExtractor
from extractors import DocxExtractor
from extractors import PdfExtractor
from extractors import PptExtractor
from extractors import PptxExtractor
from extractors import ZipExtractor
from extractors import XlsxExtractor
from extractors import XlsExtractor

EXTRACTORS  = {
    ".txt" : TextExtractor(), 
    ".h" : TextExtractor(),
    ".hpp" : TextExtractor(),
    ".cpp" : TextExtractor(),
    #".csv" : TextExtractor(),
    ".c" : TextExtractor(),
    ".docx" : DocxExtractor(),
    ".pdf" : PdfExtractor(),
    ".ppt" : PptExtractor(),
    ".pptx" : PptxExtractor(),
    ".zip" : ZipExtractor(), # this does not produce TextData, only more work for the pipeline
    #".xls" : XlsExtractor(),
    #".xlsx" : XlsxExtractor()
}

from serializers import txt_serializer
from serializers import json_serializer
from pathlib import Path

ROOT_CWD = Path.cwd()


SERIALIZERS = {
        'txt' : txt_serializer,
        'json' : json_serializer
    }

def user_input():
    
    path = None
    
    TASKS = [
    #(ROOT_CWD / 'content.txt', txt_serializer),
    ]
    
    while True:
        
        # path to extract from
        data_path = input("input extraction directory path (or Q to finish):")
        save_name = None
        serializer = None
        
        if data_path.lower() == 'q': break
        
        while not serializer:
            
            # serializer choose
            key = input(f"choose serialization {SERIALIZERS.keys()}: ")
            serializer = SERIALIZERS.get(key, None)
            
            if serializer:
                # save file name choose
                save_name = str(input(f"save name as (will be saved in local directory): ")) + "." + key
                save_name = Path().cwd() / save_name
                break
        
        TASKS.append((data_path, save_name, serializer))
        
    return TASKS

def confirm(TASKS : list[tuple]):
    
    for i, (data_path, save_name, serializer) in enumerate(TASKS):
        
        print("=" * 40)
        print(f'TASK {i + 1}: ')
        print(f'PATH: {data_path} ')
        print(f'SAVE NAME: {save_name}')
        print(f'SERIALIZER: {serializer} ')
        print("=" * 40)
    
    user_input = None
    
    while True:
        user_input = str(input("Start extraction? (Y or N): ")).lower()
        if user_input not in ['y', 'n']:
            print('invalid.')
        else:
            return user_input
    
        
        
def run(TASKS : list[tuple]):

    for data_path, save_name, serializer in TASKS:
        
        OPTIONS = [(save_name, serializer)] # this was an older design, hence the strange set up
        results = UnitExtractor(**EXTRACTORS).run(data_path)
        Serializer(*OPTIONS).run(data=results)
    

if __name__ == "__main__":
    
    TASKS = user_input()
    CONFIRMATION = confirm(TASKS)
    
    if CONFIRMATION == 'n':
        print('exiting...')
    else:
        print('beginning extraction.')
        run(TASKS)
    
    