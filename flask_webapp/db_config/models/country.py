from app import db

class Country(db.Model):

    __tablename__ = 'country'

    country = db.Column(db.String(50), primary_key= True)
    country_name = db.Column(db.String(255), nullable=False)


    def __init__(self, country, country_name):
        self.country = country
        self.country_name = country_name

    def json(self):
        return {
            'country': self.country,
            'country_name': self.country_name
        }





