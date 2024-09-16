import os
import joblib
from flask import current_app
import pandas as pd

def predict(input_features):
    """
    Predicts the cash flow based on input features using a trained ML model.
    
    Args:
        input_features (list): A list of input features for prediction.
        
    Returns:
        float: The predicted cash flow.
    """
    model_path = os.path.join(current_app.instance_path, 'models', 'cash_flow_model.pkl')
    
    if not os.path.exists(model_path):
        raise FileNotFoundError("Trained model not found. Please train the model using train_model.py.")
    
    model = joblib.load(model_path)
    input_df = pd.DataFrame([input_features], columns=[
        'purchase_price', 'rental_income', 'operating_expenses', 'vacancy_rate',
        'median_home_price', 'rental_rate', 'unemployment_rate'
    ])
    prediction = model.predict(input_df)
    return prediction[0]