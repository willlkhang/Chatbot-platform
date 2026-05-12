"""Extractor for legacy Microsoft Word `.doc` files.

This extractor uses COM automation (Windows-only) to convert a `.doc`
file to `.docx` and then delegates to `DocxExtractor`. Small comments
and docstrings have been added; functionality is unchanged.
"""

import os
from pathlib import Path
import win32com.client

from .base import ExtractorBase
from .docx_extractor import DocxExtractor


class DocExtractor(ExtractorBase):
    """Handle legacy `.doc` files by converting to `.docx` first."""

    def _doc_to_docx(self, path: str) -> str:
        """Convert `path` (.doc) to a temporary .docx file and return its path.

        Note: uses Windows COM automation and therefore only works on
        Windows hosts with Microsoft Word installed.
        """
        src = os.path.abspath(path)
        dst = os.path.join(os.path.dirname(src), Path(src).stem + ".docx")

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
        """Convert `.doc` to `.docx` and delegate extraction to `DocxExtractor`."""
        if docx_extractor is None:
            docx_extractor = DocxExtractor()
        elif isinstance(docx_extractor, type):
            docx_extractor = docx_extractor()

        converted_path = self._doc_to_docx(path)

        try:
            docs = docx_extractor.extract(converted_path)
            # Rewrite path to the original .doc so metadata reflects source
            for doc in docs:
                doc.path = path
            return docs
        finally:
            try:
                os.remove(converted_path)
            except OSError:
                pass