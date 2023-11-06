from app import db
from sqlalchemy import ForeignKey


class Staff_Skill(db.Model):

    __tablename__ = 'staff_skill'

    # Foreign key relationship to access_control table
    staff_id = db.Column(db.Integer, ForeignKey('staff.staff_id'), primary_key = True,)
    skill_name = db.Column(db.Text(length='long'), ForeignKey('skill.skill_name'),primary_key = True)


    def __init__(self, staff_id, skill_name):
        self.staff_id = staff_id
        self.skill_name = skill_name

    def json(self):
        return {
            'staff_id': self.staff_id,
            'skill_name': self.skill_name
        }