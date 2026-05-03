from abc import abstractmethod

class BaseTopicClassifier():
    
    @abstractmethod
    def classify(text : str) -> str:
        """classify a text into a certain topic"""
        ...
       
    @abstractmethod 
    def get_topics() -> list[tuple]:
        """return the topics this model knows"""
        ...