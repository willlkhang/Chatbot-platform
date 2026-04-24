from ai.ai_tools.unit_extractor.controllers import UnitExtractor
from ai.ai_tools.unit_extractor.extractors import TextExtractor


EXTRACTORS  ={
    ".txt" : TextExtractor(), 
    ".h" : TextExtractor()
}

if __name__ == "__main__":
    
    test_path = r"C:\All University Materials\Project\ICT304-project\ai\ai_tools\data_extractor\data\raw\ICT283_contents"
    results = UnitExtractor(**EXTRACTORS).get_data(test_path)
    