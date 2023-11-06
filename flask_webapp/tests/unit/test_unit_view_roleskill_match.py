import unittest
from app import app, db  # Import your Flask app and db
from db_config.models import *  # Import your Role_Listing model
import json

from decouple import config


class TestRoleSkillMatch(unittest.TestCase):
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

        self.staff_skills_data = [
        {
            "staff_id": 140002,
            "skill_name": "Accounting and Tax Systems",
        },
        {
            "staff_id": 140002,
            "skill_name": "Business Environment Analysis",
        },
        {
            "staff_id": 140002,
            "skill_name": "Customer Relationship Management",
        },
        {
            "staff_id": 140002,
            "skill_name": "Professional and Business Ethics",
        },
        ]

        self.skills_data = [
        {
            "skill_name": "Accounting and Tax Systems",
            "skill_desc": "Implement accounting or tax software systems in the organisation"
        },
        {
            "skill_name": "Accounting Standards",
            "skill_desc": "Apply financial reporting framework prescribed by the relevant governing body to ensure all transactions meet regulatory requirements"
        },
        {
            "skill_name": "Audit Compliance",
            "skill_desc": "Ensure compliance with corporate policies and guidelines"
        },
        {
            "skill_name": "Audit Frameworks",
            "skill_desc": "Develop quality assurance frameworks to meet regulatory requirements",
        },
        {
            "skill_name": "Business Acumen",
            "skill_desc": "Assess the impact of changes in the business organisation, environment, and industry",
        },
        {
            "skill_name": "Collaboration",
            "skill_desc": "Manage relationships and work collaboratively and effectively with others to achieve goals",
        },
        {
            "skill_name": "Communication",
            "skill_desc": "Convey and exchange thoughts, ideas and information effectively through various mediums and approaches",
        },
        {
            "skill_name": "Data Analytics",
            "skill_desc": "Assess the impact of changes in the business organisation, environment, and industry",
        },
        {
            "skill_name": "Finance Business Partnering",
            "skill_desc": "Assess the impact of changes in the business organisation, environment, and industry",
        },
        {
            "skill_name": "Financial Management",
            "skill_desc": "Assess the impact of changes in the business organisation, environment, and industry",
        },
        {
            "skill_name": "Financial Planning",
            "skill_desc": "Assess the impact of changes in the business organisation, environment, and industry",
        },
        {
            "skill_name": "Financial Reporting",
            "skill_desc": "Assess the impact of changes in the business organisation, environment, and industry",
        },
        {
            "skill_name": "Financial Statements Analysis",
            "skill_desc": "Assess the impact of changes in the business organisation, environment, and industry",
        },
        {
            "skill_name": "Professional and Business Ethics",
            "skill_desc": "Assess the impact of changes in the business organisation, environment, and industry",
        },
        {
            "skill_name": "Project Management",
            "skill_desc": "Assess the impact of changes in the business organisation, environment, and industry",
        },
        {
            "skill_name": "Regulatory Compliance",
            "skill_desc": "Assess the impact of changes in the business organisation, environment, and industry",
        },
        {
            "skill_name": "Regulatory Risk Assessment",
            "skill_desc": "Assess the impact of changes in the business organisation, environment, and industry",
        },
        {
            "skill_name": "Stakeholder Management",
            "skill_desc": "Assess the impact of changes in the business organisation, environment, and industry",
        },
        {
            "skill_name": "Tax Implications",
            "skill_desc": "Assess the impact of changes in the business organisation, environment, and industry",
        },
        {
            "skill_name": "Business Environment Analysis",
            "skill_desc": "Assess the impact of changes in the business organisation, environment, and industry",
        },
        {
            "skill_name": "Customer Relationship Management",
            "skill_desc": "Assess the impact of changes in the business organisation, environment, and industry",
        },

        

        ]

        self.manager = Staff(
            staff_id=171029,
            staff_fname="Somchai",
            staff_lname="Kong",
            dept="Finance",
            country="Singapore",
            email="Somchai.Kong@allinone.com.sg",
            role="3",
        )

        self.role = Role(
            "Finance Manager",
            "The Finance Manager is the lead finance business partner for the organisation and has responsibilities covering all aspects of financial management, performance management, financial accounting, budgeting, corporate reporting etc. He/she has sound technical as well as management skills and be able to lead a team consisting of finance professionals with varied, in-depth or niche technical knowledge and abilities; consolidating their work and ensuring its quality and accuracy, especially for reporting purposes. The Finance Manager is expected to provide sound financial advice and counsel on working capital, financing or the financial position of the organisation by synthesising internal and external data and studying the economic environment. He often has a key role in implementing best practices in order to identify and manage all financial and business risks and to meet the organisation's desired business and fiscal goals. He is expected to have a firm grasp of economic and business trends and to implement work improvement projects that are geared towards quality, compliance and efficiency in finance.",
        )

        self.role_skills = []
        skills = ['Accounting and Tax Systems', 'Accounting Standards', 'Audit Compliance', 'Audit Frameworks', 'Business Acumen', 'Collaboration', 'Communication', 'Data Analytics', 'Finance Business Partnering', 'Financial Management', 'Financial Planning', 'Financial Reporting', 'Financial Statements Analysis', 'Professional and Business Ethics', 'Project Management', 'Regulatory Compliance', 'Regulatory Risk Assessment', 'Stakeholder Management', 'Tax Implications']

        for skill in skills:
            role_skill = Role_Skill(
                role_name='Finance Manager',
                skill_name=skill
            )
            self.role_skills.append(role_skill)


        self.role_listing = Role_Listing(
            role_name='Finance Manager',
            country='Singapore',
            dept='Finance',
            num_opening=2,
            date_open='2023-10-10 00:00:00',
            date_close='2023-11-30 00:00:00',
            reporting_mng=171029,
        )
        
        self.staff = Staff(
            staff_id=140002,
            staff_fname="Susan",
            staff_lname="Goh",
            dept="Finance",
            country="Singapore",
            email="Susan.Goh@allinone.com.sg",
            role=2,
        )

    def tearDown(self):
        with self.app_context:
            try:
                db.session.query(Role_Listing).delete()
                db.session.query(Role_Skill).delete()
                db.session.query(Staff_Skill).delete()
                db.session.query(Staff).delete()
                db.session.query(Skill).delete()
                db.session.query(Role).delete()
                db.session.commit()
            except Exception as e:
                print(f"An error occurred during the cleanup: {e}")
                db.session.rollback()
                raise

    def test_match_skills(self):
        with self.app_context:
            for skill_data in self.skills_data:
                skill = Skill(**skill_data)
                db.session.add(skill)

            db.session.add(self.manager)
            db.session.add(self.role)
            db.session.add(self.role_listing)
            db.session.add(self.staff)
            for role_skill in self.role_skills:
                db.session.add(role_skill)
            for staff_skill_data in self.staff_skills_data:
                staff_skill = Staff_Skill(**staff_skill_data)
                db.session.add(staff_skill)
            db.session.commit()
            print(f"Role Listing ID: {self.role_listing.listing_id}")

            with self.client as c:
            # Set up session data within the context of the test client
                with c.session_transaction() as sess:
                    sess['Staff_ID'] = 140002 

                response = c.get(f'/match_skills/0')
                print(response.data)
                data = response.get_json()
                self.assertEqual(response.status_code, 200)

                self.assertIn("response_data", data)
                self.assertIn("message", data)
                self.assertIn("code", data)

                response_data = data["response_data"]
                self.assertIn("listing_id", response_data)
                self.assertIn("role_name", response_data)
                self.assertIn("staff_id", response_data)
                self.assertIn("matched_skills", response_data)
                self.assertIn("lacking_skills", response_data)

                print("Staff Skills:")
                for staff_skill in self.staff.staff_skills:
                    print(f"Skill Name: {staff_skill.skill_name}")

                print("\nRole Skills:")
                for role_skill in self.role_skills:
                    print(f"Skill Name: {role_skill.skill_name}")

                expected_message = "You have matching skills with this role!"
                actual_message = data["message"]
                self.assertEqual(actual_message, expected_message)

                if not response_data["matched_skills"]:
                    self.assertEqual(data["message"], "You have no matching skills with this role!")
                else:
                    self.assertEqual(data["message"], "You have matching skills with this role!")

    def test_get_skills(self):
        with self.app_context:
            for skill_data in self.skills_data:
                skill = Skill(**skill_data)
                db.session.add(skill)
            db.session.commit()

            db.session.add(self.staff)

            for staff_skill_data in self.staff_skills_data:
                staff_skill = Staff_Skill(**staff_skill_data)
                db.session.add(staff_skill)
            db.session.commit()
        
        with self.client:
            with app.test_request_context():
                with app.test_client() as c:
                    with c.session_transaction() as sess:
                        sess['Staff_ID'] = 140002

                    response = c.get('/skills')

                    self.assertEqual(response.status_code, 200)

                    data = json.loads(response.data)
                    self.assertIn('code', data)
                    self.assertIn('data', data)
                    self.assertIn('skill_names', data['data'])
                    self.assertIn('descriptions', data['data'])

if __name__ == '__main__':
    unittest.main()