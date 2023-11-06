from app import db

class Skill(db.Model):

    __tablename__ = 'skill'

    skill_name = db.Column(db.String(50),primary_key=True, nullable=False)
    skill_desc = db.Column(db.Text(length='long'), nullable=False)

    role_skills = db.relationship('Role_Skill', backref='skill')
    staff_skills = db.relationship('Staff_Skill', backref='skill')

    
    def __init__(self, skill_name, skill_desc):
        self.skill_name = skill_name
        self.skill_desc = skill_desc

    
    def json(self):
        return {
            'skill_name': self.skill_name,
            'skill_desc': self.skill_desc,
            'role_skills': [role_skill.json() for role_skill in self.role_skills],
            'staff_skills': [staff_skill.json() for staff_skill in self.staff_skills]
        }
    
