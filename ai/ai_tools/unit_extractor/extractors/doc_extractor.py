import os
import tempfile
from pathlib import Path
import win32com.client

from .base import ExtractorBase
from .docx_extractor import DocxExtractor

"""
CLAUDE CODE
"""

class DocExtractor(ExtractorBase):
    """
    Extracts .doc files by first converting them to .docx using Word,
    then delegating to DocxExtractor.
    """

    def _doc_to_docx(self, path: str) -> str:
        """
        Converts a .doc file to .docx by driving a real Word instance
        via COM automation. Returns the path to the new .docx file
        (saved in the system temp folder).
        """
        src = os.path.abspath(path)
        dst = os.path.join(tempfile.gettempdir(), Path(src).stem + ".docx")

        word = win32com.client.Dispatch("Word.Application")
        try:
            try:
                word.Visible = False
            except Exception:
                pass

            doc = word.Documents.Open(src, ReadOnly=True)
            # 16 = wdFormatXMLDocument (.docx, Word 2007+ format)
            doc.SaveAs(dst, FileFormat=16)
            doc.Close(SaveChanges=False)
        finally:
            word.Quit()

        return dst

    def _extract(self, path=None, docx_extractor=None) -> list:
        if docx_extractor is None:
            docx_extractor = DocxExtractor()
        elif isinstance(docx_extractor, type):
            docx_extractor = docx_extractor()

        converted_path = self._doc_to_docx(path)

        try:
            docs = docx_extractor.extract(converted_path)
            # Rewrite path to the original .doc
            for doc in docs:
                doc.path = path
            return docs
        finally:
            try:
                os.remove(converted_path)
            except OSError:
                pass