from abc import abstractmethod

class BasePreprocessor():
    
    @abstractmethod
    def preprocess(text : str) -> str:
        """process a prompt or query"""
        ...