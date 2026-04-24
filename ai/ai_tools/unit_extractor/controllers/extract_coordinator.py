from pathlib import Path
from extractors import ExtractorBase
from domain import TextData

class UnitExtractor():
    
    def __init__(self, **extractors):
        
        self.extractors = extractors
    
    def run(self, path : str | Path = None, skip_list : list = None):
        
        root = Path(path)
        stack = []
        text_data_list = []
        
        for path in root.iterdir():
            stack.append(path)
            
        while stack:
            current = stack.pop()
            
            if isinstance(current, TextData):
                text_data_list.append(current)
                continue
                
            cur_as_path = Path(current)
            
            if cur_as_path.is_dir():
                for path in cur_as_path.iterdir():
                    stack.append(path)
            else:
                ext = cur_as_path.suffix.lower()
                extractor : ExtractorBase = self.extractors.get(ext, None)
                
                
                if extractor:
                    print(cur_as_path)
                    print(f"processing {ext}...")
                    for txt_data in extractor.extract(cur_as_path):
                        stack.append(txt_data)
                    
        return text_data_list