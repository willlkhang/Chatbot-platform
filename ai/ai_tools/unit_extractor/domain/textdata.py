from pathlib import Path


class TextData:
    
    def __init__(self, 
                 path: str | Path, 
                 text: str = None):
        
        path = Path(path)
        
        
        self.filename = path.name
        self.file_folder = path.parent.name
        self.text = text
        self.metadata = {
            "extension": path.suffix.lstrip('.').lower(),
            "full_path" : path.as_posix() # comment out for privacy purposes
        }