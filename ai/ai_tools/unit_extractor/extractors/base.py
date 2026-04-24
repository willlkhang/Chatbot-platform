from abc import ABC, abstractmethod
from pathlib import Path
from domain import TextData

class ExtractorBase(ABC):
    
    def __init__(self, *cleaners, **kwargs):
        self.kwargs = kwargs
        self.cleaners = cleaners
        
    
    def extract(self, path=None) -> list:
        results = self._extract(path)
        
        items = []
        for item in results:
            if isinstance(item, TextData):
                items.append(self._apply_cleaners(item))
            else:
                items.append(item)
                
        return items
            
    
    @abstractmethod
    def _extract(self, path = None) -> list:
        """extract stuff from a path"""
        ...
        
    def _apply_cleaners(self, text_data : TextData):
        cleaned_text_data = text_data
        for cleaner in self.cleaners:
            cleaned_text_data = cleaner(cleaned_text_data)
        return cleaned_text_data
        
if __name__ == "__main__":
    print('testing')
    
    
