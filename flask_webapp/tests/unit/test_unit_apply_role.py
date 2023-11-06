import unittest
from app import app, db  # Import your Flask app and db
from db_config.models import *  # Import your Role_Listing model
import json

from decouple import config


class TestApplyRole(unittest.TestCase):
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

        self.role1 = Role(
            "Finance Manager",
            "The Finance Manager is the lead finance business partner for the organisation and has responsibilities covering all aspects of financial management, performance management, financial accounting, budgeting, corporate reporting etc. He/she has sound technical as well as management skills and be able to lead a team consisting of finance professionals with varied, in-depth or niche technical knowledge and abilities; consolidating their work and ensuring its quality and accuracy, especially for reporting purposes. The Finance Manager is expected to provide sound financial advice and counsel on working capital, financing or the financial position of the organisation by synthesising internal and external data and studying the economic environment. He often has a key role in implementing best practices in order to identify and manage all financial and business risks and to meet the organisation's desired business and fiscal goals. He is expected to have a firm grasp of economic and business trends and to implement work improvement projects that are geared towards quality, compliance and efficiency in finance.",
        )

        self.role2 = Role(
            "Account Manager",
            "The Account Manager acts as a key point of contact between an organisation and its clients. He/She possesses thorough product knowledge and oversees product and/or service sales. He works with customers to identify their wants and prepares reports by collecting, analysing, and summarising sales information. He contacts existing customers to discuss and give recommendations on how specific products or services can meet their needs. He maintains customer relationships to strategically place new products and drive sales for long-term growth. He works in a fast-paced and dynamic environment, and travels frequently to clients' premises for meetings. He is familiar with client relationship management and sales tools. He is knowledgeable of the organisation's products and services, as well as trends, developments and challenges of the industry domain. The Sales Account Manager is a resourceful, people-focused and persistent individual, who takes rejection as a personal challenge to succeed when given opportunity. He appreciates the value of long lasting relationships and prioritises efforts to build trust with existing and potential customers. He exhibits good listening skills and is able to establish rapport with customers and team members alike easily.",
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
        self.staff = Staff(
            140002,
            "Susan",
            "Goh",
            "Finance",
            "Singapore",
            "Susan.Goh@allinone.com.sg",
            3,
        )
        self.listing = Role_Listing(
            country="Singapore",
            dept="Finance",
            num_opening=4,
            date_open="2023-10-30 00:00:00",
            date_close="2023-11-30 00:00:00",
            role_name="Finance Manager",
            reporting_mng=171029,
        )
        self.closed_listing = Role_Listing(
            country="Singapore",
            dept="Finance",
            num_opening=4,
            date_open="2023-10-30 00:00:00",
            date_close="2023-10-31 00:00:00", 
            role_name="Account Manager",
            reporting_mng=171029,
        )
        self.existing_application = Application(
            listing_id=0,
            staff_id=140002,
            status="Pending",
            applied_date="2023-11-01 00:00:00"
        )
                

    def tearDown(self):
        with app.app_context():
            db.session.query(Application).delete()  # Delete any related Application records
            db.session.query(Role_Listing).delete() 
            db.session.query(Staff).delete() 
            db.session.query(Role).delete() 

            db.session.commit()

    def test_apply_role(self):
        # Create a test Role_Listing
        with app.app_context():
            db.session.add(self.role1)
            db.session.add(self.manager1)
            db.session.add(self.staff)
            db.session.add(self.listing)
            db.session.commit()
        

        with self.client.session_transaction() as sess:
            sess["Staff_ID"] = 140002
            sess["Role"] = 2

        new_data = {"listing_id": 0}

        response = self.client.post("/apply_role/0")
        print(response)
        data = json.loads(response.data)

        self.assertEqual(
            response.status_code, 201
        )  # Check if the response status code is 201 (Created)

        # You can add more assertions to check the response data or database state if needed

    def test_apply_existing_role(self):
        # Create a test Role_Listing
        with app.app_context():
            db.session.add(self.role1)
            db.session.add(self.manager1)
            db.session.add(self.staff)
            db.session.add(self.listing)
            db.session.add(self.existing_application)
    
            db.session.commit()
        

        with self.client.session_transaction() as sess:
            sess["Staff_ID"] = 140002
            sess["Role"] = 2

        new_data = {"listing_id": 0}

        response = self.client.post("/apply_role/0")
        print(response)
        data = json.loads(response.data)

        self.assertEqual(
            response.status_code, 400
        )  # Check if the response status code is 201 (Created)

    def test_apply_closed_role(self):
        # Create a test Role_Listing
        with app.app_context():
            db.session.add(self.role2)
            db.session.add(self.manager1)
            db.session.add(self.staff)
            db.session.add(self.closed_listing)
    
            db.session.commit()
        

        with self.client.session_transaction() as sess:
            sess["Staff_ID"] = 140002
            sess["Role"] = 2

        new_data = {"listing_id": 0}

        response = self.client.post("/apply_role/0")
        print(response)
        data = json.loads(response.data)

        self.assertEqual(
            response.status_code, 411
        )  # Check if the response status code is 201 (Created)

if __name__ == "__main__":
    unittest.main()
