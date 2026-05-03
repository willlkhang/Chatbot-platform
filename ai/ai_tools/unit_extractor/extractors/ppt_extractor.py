import os
import tempfile
from pathlib import Path
import win32com.client  # from the 'pywin32' package

from .base import ExtractorBase
from .pptx_extractor import PptxExtractor

"""
Claude's code


LOTS OF OLD PPT FILES NEEDS TO BE CONVERTED PPTX
"""
class PptExtractor(ExtractorBase):
    
    """
    Extracts .ppt files by first converting them to .pptx using PowerPoint,
    then delegating to PptxExtractor.
    """
    
    def _ppt_to_pptx(self, path: str) -> str:
        """
        Converts a .ppt file to .pptx by driving a real PowerPoint instance
        via COM automation. Returns the path to the new .pptx file
        (saved in the system temp folder).
        """
        # COM needs absolute paths — relative paths silently fail
        src = os.path.abspath(path)
        dst = os.path.join(os.path.dirname(src), Path(src).stem + ".pptx")

        powerpoint = win32com.client.Dispatch("PowerPoint.Application")
        try:
            # Some Office versions refuse to hide the window, so wrap it
            try:
                powerpoint.Visible = False
            except Exception:
                pass

            deck = powerpoint.Presentations.Open(src, WithWindow=False)
            deck.SaveAs(dst, 24)  # 24 = ppSaveAsOpenXMLPresentation (.pptx)
            deck.Close()
        finally:
            powerpoint.Quit()

        return dst

    def _extract(self, path=None, pptx_extractor=None) -> list:
        # Default to a fresh PptxExtractor if none provided
        if pptx_extractor is None:
            pptx_extractor = PptxExtractor()
        # Allow passing the class OR an instance
        elif isinstance(pptx_extractor, type):
            pptx_extractor = pptx_extractor()

        converted_path = self._ppt_to_pptx(path)

        try:
            slide_docs = pptx_extractor.extract(converted_path)
            # Rewrite the path in each TextData to the original .ppt,
            # otherwise it'll point at a temp file that's about to be deleted
            for doc in slide_docs:
                doc.path = path
            return slide_docs
        finally:
            # Clean up the temp .pptx
            try:
                os.remove(converted_path)
            except OSError:
                pass


if __name__ == "__main__":
    test_path = r"C:\All University Materials\Project\ICT304-project\ai\ai_tools\data_extractor\data\raw\ICT283_contents\Topic11\Content\Lec-31.ppt"

    for i in PptExtractor().extract(test_path):
        print(i.metadata)