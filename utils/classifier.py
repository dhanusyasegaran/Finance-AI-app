import joblib
import os

class ExpenseClassifier:
    def __init__(self):
        model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'expense_model.pkl')
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
        else:
            self.model = None

    def predict(self, description):
        if self.model:
            return self.model.predict([description])[0]
        return "Others"

classifier = ExpenseClassifier()
