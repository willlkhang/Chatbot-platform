from domain import TextData
from pathlib import Path
import json

def json_serializer( data : list[TextData], save_path : str | Path = Path().cwd() / 'content.json'):
    
    with open(save_path, 'w', encoding='utf-8') as f:
        
        for text_data in data:
            text_data_dict = {
                "filename" : str(text_data.filename),
                "folder_name" : str(text_data.file_folder),
                "text" : str(text_data.text),
                "metadata" : {key : str(metadata) for key, metadata in text_data.metadata.items()}
            }
            
            f.write(json.dumps(text_data_dict, ensure_ascii=False) + '\n')
    


if __name__ == "__main__":
    
    ...