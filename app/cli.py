import click
from . import db
from .models import PropertyData, MarketTrend
from datetime import date

@click.command("populate_sample_data")
def populate_sample_data():
    """Populate the database with sample PropertyData and MarketTrend."""
    # Sample Property Data
    if not PropertyData.query.first():
        sample_properties = [
            PropertyData(
                address="123 Maple Street",
                purchase_price=250000,
                rental_income=2000,
                operating_expenses=800,
                vacancy_rate=0.05,
                purchase_date=date(2022, 1, 15)
            ),
            PropertyData(
                address="456 Oak Avenue",
                purchase_price=350000,
                rental_income=2500,
                operating_expenses=900,
                vacancy_rate=0.04,
                purchase_date=date(2021, 6, 10)
            ),
            # Add more sample properties as needed
        ]
        db.session.add_all(sample_properties)
        db.session.commit()
        click.echo("Sample PropertyData added.")
    else:
        click.echo("PropertyData already exists. Skipping...")

    # Sample Market Trends
    if not MarketTrend.query.first():
        sample_trends = [
            MarketTrend(
                date=date(2023, 1, 1),
                median_home_price=300000,
                rental_rate=2.5,
                unemployment_rate=5.0
            ),
            MarketTrend(
                date=date(2023, 6, 1),
                median_home_price=310000,
                rental_rate=2.6,
                unemployment_rate=4.8
            ),
            # Add more sample trends as needed
        ]
        db.session.add_all(sample_trends)
        db.session.commit()
        click.echo("Sample MarketTrend data added.")
    else:
        click.echo("MarketTrend data already exists. Skipping...")

    click.echo("Sample data populated successfully.")