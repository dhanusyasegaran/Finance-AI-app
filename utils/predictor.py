import numpy as np
from sklearn.linear_model import LinearRegression

def predict_next_month_expense(monthly_data):
    """
    Expects a list of monthly total expenses [m1, m2, m3...]
    """
    if len(monthly_data) < 2:
        return np.mean(monthly_data) if monthly_data else 0
    
    X = np.array(range(len(monthly_data))).reshape(-1, 1)
    y = np.array(monthly_data)
    
    model = LinearRegression()
    model.fit(X, y)
    
    next_month = np.array([[len(monthly_data)]])
    prediction = model.predict(next_month)[0]
    
    return max(0, prediction)
