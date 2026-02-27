import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
import joblib
import os

# Sample labeled dataset
data = {
    'description': [
        'Starbucks Coffee', 'Uber Ride', 'Monthly Rent', 'Amazon Shopping', 
        'Netflix Subscription', 'Electricity Bill', 'Grocery Store', 'Delta Airlines',
        'Walmart Grocery', 'Gas Station', 'Gym Membership', 'Dining Out',
        'ZARA Clothing', 'Spotify', 'Mobile Bill', 'Train Ticket'
    ],
    'category': [
        'Food', 'Travel', 'Rent', 'Shopping', 
        'Entertainment', 'Bills', 'Food', 'Travel',
        'Food', 'Travel', 'Entertainment', 'Food',
        'Shopping', 'Entertainment', 'Bills', 'Travel'
    ]
}

def train_expense_classifier():
    df = pd.DataFrame(data)
    
    # Feature Extraction & Classifier Pipeline
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english')),
        ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    
    # Train
    pipeline.fit(df['description'], df['category'])
    
    # Save Model
    model_path = os.path.join(os.path.dirname(__file__), 'expense_model.pkl')
    joblib.dump(pipeline, model_path)
    print(f"Model saved to {model_path}")

if __name__ == '__main__':
    train_expense_classifier()
