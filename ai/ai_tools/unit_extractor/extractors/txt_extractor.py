from .base import ExtractorBase
from domain import TextData
from pathlib import Path

class TextExtractor(ExtractorBase):
    
    def _extract_apply(self, path = None):
        """
        works on most code files.
        """
        try:
            return Path(path).read_text(encoding='utf-8')
        except:
            return Path(path).read_text(encoding='cp1252')
        
    def _extract(self, path : str | Path = None) -> list[TextData]:
        """extracts the text from a pdf"""
        path = Path(path)
        content = self._extract_apply(path)
        
        return [TextData(path=path,
                         text=content)]

if __name__ == "__main__":
    ...