import unittest
from app import app, db  # Import your Flask app and db
from db_config.models import *  # Import your Role_Listing model
import json

from decouple import config


class TestEditListing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = config('TEST_DATABASE_URL')
        cls.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(cls.app)

    def setUp(self):
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()


        self.app = app.test_client()

        self.role = Role(
            "Finance Manager",
            "The Finance Manager is the lead finance business partner for the organisation and has responsibilities covering all aspects of financial management, performance management, financial accounting, budgeting, corporate reporting etc. He/she has sound technical as well as management skills and be able to lead a team consisting of finance professionals with varied, in-depth or niche technical knowledge and abilities; consolidating their work and ensuring its quality and accuracy, especially for reporting purposes. The Finance Manager is expected to provide sound financial advice and counsel on working capital, financing or the financial position of the organisation by synthesising internal and external data and studying the economic environment. He often has a key role in implementing best practices in order to identify and manage all financial and business risks and to meet the organisation's desired business and fiscal goals. He is expected to have a firm grasp of economic and business trends and to implement work improvement projects that are geared towards quality, compliance and efficiency in finance.",
        )
        self.manager1 = Staff(
            171029,
            "Somchai",
            "Kong",
            "Finance",
            "Singapore",
            "Somchai.Kong@allinone.com.sg",
            3,
        )
        self.manager2 = Staff(
            171014,
            "Kumari",
            "Pillai",
            "Finance",
            "Singapore",
            "Kumari.Pillai@allinone.com.sg",
            3,
        )
        self.listing = Role_Listing(
            "Singapore",
            "Finance",
            4,
            "2023-10-30 00:00:00",
            "2023-11-15 00:00:00",
            "Finance Manager",
            171029,
        )

    def tearDown(self):
        with app.app_context():
            db.session.query(Role_Listing).delete() 
            db.session.query(Staff).delete() 
            db.session.query(Role).delete() 

            db.session.commit()

    def test_update_check_listing(self):

        # Create a test Role_Listing
        with app.app_context():
            db.session.add(self.role)
            db.session.add(self.manager1)
            db.session.add(self.manager2)
            db.session.add(self.listing)
            db.session.commit()

        new_data = {
            "title": "Finance Manager",
            "department": "Finance",
            "country": "Singapore",
            "startDate": "2023-10-28",
            "endDate": "2023-11-30",
            "manager": 171014,
            "vacancy": 7,
        }

        response = self.app.put("/update/check_listing_exist/0", json=new_data)
        print(response)
        print(response.data)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 201)


if __name__ == "__main__":
    unittest.main()
