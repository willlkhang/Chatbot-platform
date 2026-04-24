from .base import ExtractorBase
from domain import TextData
from pypdf import PdfReader

#i think I knnow what for them to do
# is let them to build model to take keywords from this fat file like NLP task we may do words bag and take top frequent words

class PdfExtractor(ExtractorBase):
    """
    Extracts pdf files
    """
    def _extract(self, path=None) -> list:
        
        pdf = PdfReader(path)
        
        page_docs = []
        for i, page in enumerate(pdf.pages, start=1):
            
            text = self._get_text(page)

            data = TextData(path=path, text=f'CONTENT: {text}\n')
            data.metadata['page_num'] = f'{i}'
            
            page_docs.append(data)
            
        return page_docs
    
    def _get_text(self, page) -> str:
        """Retrieves all text from page"""
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
