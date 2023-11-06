from app import db
from sqlalchemy import ForeignKey


class Role_Skill(db.Model):

    __tablename__ = 'role_skill'

    # Foreign key relationship to access_control table
    role_name = db.Column(db.String(20), ForeignKey('role.role_name'), primary_key = True, nullable=False)
    skill_name = db.Column(db.String(50), ForeignKey('skill.skill_name'),primary_key = True, nullable=False)


    def __init__(self, role_name, skill_name):
        self.role_name = role_name
        self.skill_name = skill_name
    
    def json(self):
        return {"role_name":self.role_name, "skill_name": self.skill_name}