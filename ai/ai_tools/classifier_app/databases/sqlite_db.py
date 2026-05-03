import sqlite3
from pathlib import Path
from .base_db import BaseDB

class SQLiteDB(BaseDB):
    
    def __init__(self):
        
        self.db_path = data_path = Path(__file__).parent / 'data' / 'resources.db'
        
        connection = sqlite3.connect(data_path)
        cursor = connection.cursor()
        
        cursor.execute("""
                                CREATE TABLE IF NOT EXISTS resources (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    topic TEXT NOT NULL,
                                    resource TEXT
                                    )
                            """)
        
        connection.commit()
        
    def add_resources(self, topic : str, resource : str):
        
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute("""
                        INSERT INTO resources (topic, resource)
                        VALUES(?, ?)
                        """, (topic, resource))
            
        connection.commit()
        connection.close()
            
    
    def get_resources(self, topic : str):
        
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        
        cursor.execute(f"""
                        SELECT * FROM resources WHERE topic = ?
                        """, (topic,))
        
        rows = cursor.fetchall()
        
        return [resources for _, _, resources in rows]