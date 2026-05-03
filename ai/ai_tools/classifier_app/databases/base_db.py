from abc import abstractmethod

class BaseDB():
    
    @abstractmethod
    def get_resources(self, topic: str) -> list:
        """get resources from a db"""
        ...
        
    @abstractmethod 
    def add_resources(self, topic: str, resource : str):
        """add resources in a database"""
        ...