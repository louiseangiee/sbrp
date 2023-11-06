from app import db
from sqlalchemy import ForeignKey

class Staff(db.Model):

    __tablename__ = 'staff'

    staff_id = db.Column(db.Integer, primary_key=True)
    staff_fname= db.Column(db.String(50),nullable=False)
    staff_lname= db.Column(db.String(50),nullable=False)
    dept= db.Column(db.String(50), nullable=False)
    country= db.Column(db.String(50), nullable=False)
    email= db.Column(db.String(50), nullable=False)

    # Foreign key relationship to access_control table
    role = db.Column(db.Integer, ForeignKey('access_control.access_id'), nullable=False)


    role_listings = db.relationship('Role_Listing', backref='staff')
    staff_skills = db.relationship('Staff_Skill', backref='staff')
    applications = db.relationship('Application', backref='staff')
    
    def __init__(self, staff_id, staff_fname, staff_lname, dept, country, email, role):
        self.staff_id = staff_id
        self.staff_fname = staff_fname
        self.staff_lname = staff_lname
        self.dept = dept
        self.country = country
        self.email = email
        self.role = role
    
    def json(self): 
        return {
            'staff_id': self.staff_id,
            'staff_fname': self.staff_fname,
            'staff_lname': self.staff_lname,
            'dept': self.dept,
            'country': self.country,
            'email': self.email,
            'role': self.role,
            'role_listings': [listing.json() for listing in self.role_listings],
            'staff_skills': [skill.json() for skill in self.staff_skills],
            'applications': [app.json() for app in self.applications]
        }