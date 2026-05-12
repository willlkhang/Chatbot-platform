"""LinearSVC classifier wrapper used by the FastAPI app.

This module wraps a scikit-learn pipeline saved as a joblib file and
exposes a minimal `LinearSVC` class implementing the project's
classification interface. Comments and docstrings were added; no logic
was changed.
"""

from .base_classifier import BaseTopicClassifier
from pathlib import Path
import joblib


model_path = Path(__file__).parent / 'models' / 'LinearSVC.joblib'


class LinearSVC(BaseTopicClassifier):
    """Wrapper around a persisted LinearSVC scikit-learn pipeline.

    The model is loaded from the `models/LinearSVC.joblib` file and used
    to compute a prediction and decision score. If the top score does not
    exceed `threshold`, the classifier returns `'OTHER'`.
    """

    def __init__(self, threshold=0):
        # load trained pipeline from package resources
        self.model = joblib.load(model_path)
        # map integer class indices to label names
        self.class_names = {i: name for i, name in enumerate(self.model.named_steps['model'].classes_)}
        self.threshold = threshold

    def classify(self, text: str):
        """Return the predicted topic label for `text`.

        If the classifier's top confidence score does not exceed
        `self.threshold`, return `'OTHER'` to indicate low confidence.
        """

        scores = self.model.decision_function([text])
        pred = self.model.predict([text])
        max_score = scores.max(axis=1)

        if max_score > self.threshold:
            return pred[0]
        else:
            return 'OTHER'

    def get_topics(self):
        # expose label names
        return self.class_names.values()


