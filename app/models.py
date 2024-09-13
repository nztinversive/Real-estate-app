from .extensions import db
from datetime import datetime

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(200), nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    rental_income = db.Column(db.Float, nullable=False)
    expenses = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Remove the backref from here
    incomes = db.relationship('Income', back_populates='property')
    property_expenses = db.relationship('Expense', back_populates='property')

    def __repr__(self):
        return f'<Property {self.address}>'

class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    income_type = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)

    property = db.relationship('Property', back_populates='incomes')

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    expense_type = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)

    property = db.relationship('Property', back_populates='property_expenses')

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    file_path = db.Column(db.String(255), nullable=False)
    extracted_text = db.Column(db.Text)
    tags = db.Column(db.String(255))

    property = db.relationship('Property', backref=db.backref('documents', lazy=True))

class Deal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    total_amount = db.Column(db.Float, nullable=False)
    raised_amount = db.Column(db.Float, default=0)
    status = db.Column(db.String(50), default='Open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Deal {self.name}>'

class Investor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(50), default='Co-Investor')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Investor {self.name}>'

class Investment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deal_id = db.Column(db.Integer, db.ForeignKey('deal.id'), nullable=False)
    investor_id = db.Column(db.Integer, db.ForeignKey('investor.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    deal = db.relationship('Deal', backref=db.backref('investments', lazy=True))
    investor = db.relationship('Investor', backref=db.backref('investments', lazy=True))

class Distribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deal_id = db.Column(db.Integer, db.ForeignKey('deal.id'), nullable=False)
    investor_id = db.Column(db.Integer, db.ForeignKey('investor.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    deal = db.relationship('Deal', backref=db.backref('distributions', lazy=True))
    investor = db.relationship('Investor', backref=db.backref('distributions', lazy=True))

class PropertyDescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    image_paths = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)