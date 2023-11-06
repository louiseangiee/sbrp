from app import db

class Role(db.Model):

    __tablename__ = 'role'

    role_name = db.Column(db.String(20), primary_key=True)
    role_desc = db.Column(db.String(100000), nullable=False)
    
    role_listings = db.relationship('Role_Listing', backref='role')
    role_skills = db.relationship('Role_Skill', backref='role')

    def __init__(self, role_name, role_desc):
        self.role_name = role_name
        self.role_desc = role_desc

    def json(self):
        return {
            'role_name': self.role_name,
            'role_desc': self.role_desc,
            'role_listings': [listing.json() for listing in self.role_listings],
            'role_skills': [skill.json() for skill in self.role_skills]
        }