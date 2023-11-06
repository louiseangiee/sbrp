import unittest
from app import app, db  # Import your Flask app and db
from db_config.models import *  # Import your Role_Listing model
import json

from decouple import config


class TestCreateRole(unittest.TestCase):
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

        self.manager1 = Staff(
            180012,
            "Ji",
            "Han",
            "Consultancy",
            "Singapore",
            "Ji.Han@allinone.com.sg",
            3,
        )

        self.role1 = Role(
            "Consultant",
            "The Consultant is responsible for providing Sales technical expertise to the sales team and clients during the sales process. He/She delivers presentations and technical demonstrations of the organisation's products to prospective clients. He translates the client's business requirements into technical specifications and requirements, and provides technical inputs for proposals, tenders, bids and any relevant documents. He uses prescribed guidelines or policies to analyse and solve problems. He works in a fast-paced and dynamic environment, and travels frequently to clients' premises for technical sales pitches and meetings. He is familiar with client relationship management and sales tools. He possesses deep product and technical knowledge, and is knowledgeable of the trends, developments and challenges of the industry domain. The Sakes Consultant displays effective listening skills and is inquisitive in nature. He possesses deep technical and domain knowledge, pays attention to detail, and has strong analytical and problem-solving capabilities. He has a service-oriented personality and is a team player who works towards developing solutions collaboratively.",
        )

        self.existing_listing1 = Role_Listing(
            country="Singapore",
            dept="Consultancy",
            num_opening=4,
            date_open="2023-11-4 00:00:00",
            date_close="2023-11-18 00:00:00",
            role_name="Consultant",
            reporting_mng=180012,
        )


    def tearDown(self):
        with app.app_context():
            db.session.query(Role_Listing).delete() 
            db.session.query(Staff).delete() 
            db.session.query(Role).delete() 

            db.session.commit()

    def test_create_role(self):
        # Create a test Role_Listing
        with app.app_context():
            db.session.add(self.manager1)
            db.session.add(self.role1)
            db.session.commit()
        

        with self.client.session_transaction() as sess:
            sess["Staff_ID"] = 16008
            sess["Role"] = 4

        new_data = {"title": "Consultant",
                    "department": "Consultancy",
                    "country": "Singapore",
                    "startDate": "2023-11-08",
                    "endDate": "2023-11-15",
                    "manager": 180012,
                    "vacancy": 4}
        
        response = self.client.post("/create/check_listing_exist", json=new_data)

        self.assertEqual(
            response.status_code, 201
        ) 

    def test_create_overlap_existing(self):
        # Create a test Role_Listing
            with app.app_context():
                db.session.add(self.role1)
                db.session.add(self.manager1)
                db.session.add(self.existing_listing1)
                db.session.commit()
            

            with self.client.session_transaction() as sess:
                sess["Staff_ID"] = 16008
                sess["Role"] = 4

            new_data = {"title": "Consultant",
                        "department": "Consultancy",
                        "country": "Singapore",
                        "startDate": "2023-11-08",
                        "endDate": "2023-11-15",
                        "manager": 180012,
                        "vacancy": 2}
            
            response = self.client.post("/create/check_listing_exist", json=new_data)

            self.assertEqual(
                response.status_code, 400
            )  



if __name__ == "__main__":
    unittest.main()
