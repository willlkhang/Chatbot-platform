import pandas as pd
from pathlib import Path
from .base import ExtractorBase
from domain import TextData

"""
CLAUDE CODE
"""
class XlsxExtractor(ExtractorBase):
    """Extracts modern Excel files (.xlsx, .xlsm)."""
    
    def _extract(self, path=None) -> list:
        path = Path(path)
        # sheet_name=None returns {sheet_name: DataFrame} for all sheets
        sheets = pd.read_excel(path, sheet_name=None)
        
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