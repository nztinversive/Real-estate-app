from . import db
from datetime import datetime, date  # {{ edit_1 }} Import 'date'

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    extracted_text = db.Column(db.Text)
    tags = db.Column(db.String(255))
    version = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f'<Document {self.filename}>'

# Add PropertyData model
class PropertyData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    rental_income = db.Column(db.Float, nullable=False)
    operating_expenses = db.Column(db.Float, nullable=False)
    vacancy_rate = db.Column(db.Float, nullable=True)
    purchase_date = db.Column(db.Date, nullable=False, default=date.today)  # {{ edit_2 }}
    square_footage = db.Column(db.Integer, nullable=False)
    num_bedrooms = db.Column(db.Integer, nullable=False)
    num_bathrooms = db.Column(db.Float, nullable=False)
    year_built = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    estimated_rent = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<PropertyData {self.property_name}>'

# Add MarketTrend model
class MarketTrend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    median_home_price = db.Column(db.Float, nullable=False)
    rental_rate = db.Column(db.Float, nullable=False)
    unemployment_rate = db.Column(db.Float, nullable=True)
    # Add more fields as needed

# Add AnalyzedDeal model
class AnalyzedDeal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    purchase_price = db.Column(db.Float, nullable=False)
    down_payment = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    monthly_rental_income = db.Column(db.Float, nullable=False)
    monthly_operating_expenses = db.Column(db.Float, nullable=False)
    vacancy_rate = db.Column(db.Float, nullable=False)
    roi = db.Column(db.Float, nullable=False)
    cap_rate = db.Column(db.Float, nullable=False)
    cash_on_cash_return = db.Column(db.Float, nullable=False)
    annual_cash_flow = db.Column(db.Float, nullable=False)
    predicted_cash_flow = db.Column(db.Float, nullable=False)
    analysis_date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'purchase_price': self.purchase_price,
            'down_payment': self.down_payment,
            'interest_rate': self.interest_rate,
            'monthly_rental_income': self.monthly_rental_income,
            'monthly_operating_expenses': self.monthly_operating_expenses,
            'vacancy_rate': self.vacancy_rate,
            'roi': self.roi,
            'cap_rate': self.cap_rate,
            'cash_on_cash_return': self.cash_on_cash_return,
            'annual_cash_flow': self.annual_cash_flow,
            'predicted_cash_flow': self.predicted_cash_flow,
            'analysis_date': self.analysis_date.isoformat()
        }