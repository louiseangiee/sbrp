from app import db

class Access_Control(db.Model):

    __tablename__ = 'access_control'

    access_id = db.Column(db.Integer,primary_key=True)
    access_control_name = db.Column(db.String(20), nullable=False)

    staffs = db.relationship('Staff', backref='access_control')

    
    def __init__(self, access_control_name):
        self.access_control_name = access_control_name

    def json(self):
        return {
            'access_id': self.access_id,
            'access_control_name': self.access_control_name,
            'staffs': [staff.json() for staff in self.staffs]
        }