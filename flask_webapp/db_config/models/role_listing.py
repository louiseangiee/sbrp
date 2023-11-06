from app import db
from sqlalchemy import ForeignKey


class Role_Listing(db.Model):

    __tablename__ = 'role_listing'

    listing_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    country= db.Column(db.String(50),nullable=False)
    dept= db.Column(db.String(50),nullable=False)
    num_opening= db.Column(db.Integer,nullable=False)
    date_open= db.Column(db.DateTime,nullable=False)
    date_close= db.Column(db.DateTime,nullable=False)

    # Foreign key relationship to role table
    role_name = db.Column(db.String(20), ForeignKey('role.role_name'), nullable=False, autoincrement=True)
    reporting_mng = db.Column(db.Integer, ForeignKey('staff.staff_id'), nullable=False)
    applications = db.relationship('Application', backref='role_listing')

    def __init__(self, country, dept, num_opening, date_open, date_close, role_name, reporting_mng):
        self.country = country
        self.dept = dept
        self.num_opening = num_opening
        self.date_open = date_open
        self.date_close = date_close
        self.role_name = role_name
        self.reporting_mng = reporting_mng

    def json(self):
        return {
            'listing_id': self.listing_id,
            'country': self.country,
            'dept': self.dept,
            'num_opening': self.num_opening,
            'date_open': self.date_open.isoformat(),  # Convert to ISO format for JSON
            'date_close': self.date_close.isoformat(),  # Convert to ISO format for JSON
            'role_name': self.role_name,
            'reporting_mng': self.reporting_mng,
            'applications': [app.json() for app in self.applications]
        }