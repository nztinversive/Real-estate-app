import os
import joblib
import pandas as pd
from app import create_app
from app.models import PropertyData, MarketTrend
from app import db
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

def train_and_save_model():
    app = create_app()
    with app.app_context():
        # Fetch data from the database
        properties = PropertyData.query.all()
        trends = MarketTrend.query.all()

        if not properties or not trends:
            print("Insufficient data to train the model.")
            return

        # Convert to DataFrame
        properties_df = pd.DataFrame([{
            'purchase_price': prop.purchase_price,
            'rental_income': prop.rental_income,
            'operating_expenses': prop.operating_expenses,
            'vacancy_rate': prop.vacancy_rate,
            'purchase_date': prop.purchase_date
        } for prop in properties])

        trends_df = pd.DataFrame([{
            'date': trend.date,
            'median_home_price': trend.median_home_price,
            'rental_rate': trend.rental_rate,
            'unemployment_rate': trend.unemployment_rate
        } for trend in trends])

        # Merge properties with the latest market trend at the time of purchase
        trends_df = trends_df.sort_values('date')
        properties_df['purchase_date'] = pd.to_datetime(properties_df['purchase_date'])
        trends_df['date'] = pd.to_datetime(trends_df['date'])

        merged_df = pd.merge_asof(
            properties_df.sort_values('purchase_date'),
            trends_df.sort_values('date'),
            left_on='purchase_date',
            right_on='date',
            direction='backward'
        )

        # Feature Engineering
        merged_df['loan_amount'] = merged_df['purchase_price'] - merged_df['operating_expenses']  # Example
        merged_df['annual_rental_income'] = merged_df['rental_income'] * 12 * (1 - merged_df['vacancy_rate'])
        merged_df['annual_operating_expenses'] = merged_df['operating_expenses'] * 12
        merged_df['net_operating_income'] = merged_df['annual_rental_income'] - merged_df['annual_operating_expenses']

        # Define features and target
        features = merged_df[['purchase_price', 'rental_income', 'operating_expenses', 'vacancy_rate',
                              'median_home_price', 'rental_rate', 'unemployment_rate']]
        target = merged_df['net_operating_income']

        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

        # Initialize and train the model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        # Evaluate the model
        predictions = model.predict(X_test)
        mse = mean_squared_error(y_test, predictions)
        print(f"Model Mean Squared Error: {mse}")

        # Save the trained model
        model_path = os.path.join(app.instance_path, 'models')
        os.makedirs(model_path, exist_ok=True)
        joblib.dump(model, os.path.join(model_path, 'cash_flow_model.pkl'))
        print("Model trained and saved successfully.")

if __name__ == "__main__":
    train_and_save_model()