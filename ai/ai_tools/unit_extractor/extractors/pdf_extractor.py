"""PDF extractor producing one `TextData` per page.

This extractor uses `pypdf.PdfReader` to read pages and stores the
page number in the produced `TextData.metadata` dictionary. Only
docstrings and comments were added.
"""

from .base import ExtractorBase
from domain import TextData
from pypdf import PdfReader


class PdfExtractor(ExtractorBase):
    """Extract text from each page of a PDF as a separate `TextData`."""

    def _extract(self, path=None) -> list:

        pdf = PdfReader(path)

        page_docs = []
        for i, page in enumerate(pdf.pages, start=1):

            text = self._get_text(page)

            data = TextData(path=path, text=f'CONTENT: {text}\n')
            # annotate page number for downstream consumers
            data.metadata['page_num'] = f'{i}'

            page_docs.append(data)

        return page_docs

    def _get_text(self, page) -> str:
        """Extract textual content from a PDF page object."""
        return page.extract_text()


if __name__ == "__main__":
    test_path = r"C:\All University Materials\Project\ICT304-project\ai\ai_tools\data_extractor\data\raw\ICT283_contents\Topic10\Content\coding standards and rules\JSF-AV-C++rules.pdf"

    import time

    print('starting...')

    start = time.time()
    for i in PdfExtractor().extract(test_path):
        print(i.text)
    end = time.time()

    print(f'finished: {(end - start):.2f}')
