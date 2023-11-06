from app import db

class Department(db.Model):

    __tablename__ = 'department'

    department = db.Column(db.String(50), primary_key= True)


    def __init__(self,department):
       self.department = department
   
    def json(self):
        return self.department