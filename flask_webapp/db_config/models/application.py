from app import db
from sqlalchemy import ForeignKey

class Application(db.Model):

    __tablename__ = 'application'

    application_id = db.Column(db.Integer, primary_key= True, autoincrement=True)
    status = db.Column(db.String(20), nullable = False)
    applied_date = db.Column(db.DateTime, nullable=False)

    # Foreign attributes
    listing_id = db.Column(db.Integer, ForeignKey('role_listing.listing_id'))
    staff_id = db.Column(db.Integer, ForeignKey('staff.staff_id'))

    def __init__(self, status, applied_date, listing_id, staff_id):
       self.status = status
       self.applied_date = applied_date
       self.listing_id = listing_id
       self.staff_id = staff_id
    
    def json(self):
        return {
            "application_id": self.application_id,
            "status" : self.status,
            "applied_date": self.applied_date,
            "listing_id":self.listing_id,
            "staff_id": self.staff_id
        }