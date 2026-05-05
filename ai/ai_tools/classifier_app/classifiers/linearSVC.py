from .base_classifier import BaseTopicClassifier
from pathlib import Path
import joblib

model_path = Path(__file__).parent / 'models' / 'LinearSVC.joblib'

class LinearSVC(BaseTopicClassifier):
    
    def __init__(self, threshold = 0):
        
        self.model = joblib.load(model_path)
        self.class_names = {i: name for i, name in enumerate(self.model.named_steps['model'].classes_)}
        self.threshold = threshold
        
    def classify(self, text : str):
        
        scores = self.model.decision_function([text])
        pred = self.model.predict([text])
        max_score = scores.max(axis=1)
        
        if max_score > self.threshold:
            return pred[0]
        else:
            return 'OTHER'
        
    def get_topics(self):
        
        return self.class_names.values()
        
        
        