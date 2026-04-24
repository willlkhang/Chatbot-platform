from domain import TextData
from pathlib import Path


def txt_serializer( data : list[TextData], save_path : str | Path = Path().cwd() / 'content.txt'):
    
    lines = [f"{td.id} : {td.text}" for td in data]
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    ...