from pathlib import Path


class TextData:
    
    def __init__(self, 
                 path: str | Path, 
                 text: str = None):
        
        path = Path(path)
        
        # Find the project root by walking up until we hit a known anchor folder.
        # Adjust 'raw' to whatever top-level folder makes sense as your anchor.
        try:
            anchor_index = path.parts.index('raw')
            rel_path = Path(*path.parts[anchor_index + 1:])
        except ValueError:
            # Anchor not in path (e.g., temp file from .ppt conversion)
            rel_path = Path(path.name)
        
        rel_str = rel_path.as_posix()
        
        self.id = rel_str
        self.text = text
        self.metadata = {
            "filename": path.name,
            "extension": path.suffix.lstrip('.').lower(),
            "topic": str(rel_path.parent.name),
            "path": rel_str,
        }