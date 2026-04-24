import pandas as pd
from pathlib import Path
from .base import ExtractorBase
from domain import TextData

"""
CLAUDE CODE
"""
class XlsExtractor(ExtractorBase):
    """Extracts legacy Excel files (.xls, Office 97-2003 binary format)."""
    
    def _extract(self, path=None) -> list:
        path = Path(path)
        # Explicit engine='xlrd' — xlrd 2.0+ is the xls-only reader
        sheets = pd.read_excel(path, sheet_name=None, engine='xlrd')
        
        docs = []
        for sheet_name, df in sheets.items():
            if df.empty:
                continue
            
            text = df.to_string(index=False)
            data = TextData(path=path, text=text)
            data.metadata['sheet_name'] = sheet_name
            data.metadata['row_count'] = len(df)
            docs.append(data)
        
        return docs


if __name__ == "__main__":
    ...