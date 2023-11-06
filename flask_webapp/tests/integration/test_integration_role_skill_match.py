import json
import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import app, get_all_open_role_listings, get_skills_required # Import your Flask app and db
from db_config.db import db
from db_config.models import *  # Import your Role_Listing model
from test_config import TestConfig  # Import your TestConfig
from decouple import config
import math


class TestViewRoleSkillMatch(unittest.TestCase):
     def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

        # Establish the application context
        self.app_context = app.app_context()
        self.request_context = app.test_request_context()
        self.app_context.push()

        # Replace the following with your session data
        self.staff_id = 140002 
        self.role = 2  
        self.staff_fname = "Susan"
        self.staff_lname = "Goh"
        self.staff_name = self.staff_fname + " " + self.staff_lname
        self.dept = "Sales"
        self.country = "Singapore"
        self.email = "Susan.Goh@allinone.com.sg"

        with self.client:
            with self.client.session_transaction() as sess:
                sess['Staff_ID'] = self.staff_id
                sess['Role'] = self.role
                sess['Staff_Fname'] = self.staff_fname
                sess['Staff_Lname'] = self.staff_lname
                sess['Staff_Name'] = self.staff_name
                sess['Dept'] = self.dept
                sess['Country'] = self.country
                sess['Email'] = self.email

     def test_test(self):
        with app.test_request_context('/skills'):
            with self.client:
                #Getting staff's paired skills
                staff_skills_json = self.client.get('/skills').get_json()
                staff_skills_dict = staff_skills_json.get('data', {})
                skill_names = staff_skills_dict.get('skill_names', [])
                descriptions = staff_skills_dict.get('descriptions', [])
                # staff_skills_set = set(staff_skills_json.get('data', []))
                paired_skills = list(zip(skill_names, descriptions))
                print(paired_skills)
        
                #Assuming no search parameter
                role_search = ""
                recency = "Any time"
                country = "Country"
                department = "Department"
                required_skills = []

                #Expected unmatched skills
                '''
                unmatched_skills_results = [["Accounting Standards", "Audit Compliance", "Audit Frameworks", "Business Acumen", "Collaboration", "Communication", "Data Analytics", "Finance Business Partnering", "Financial Management", "Financial Planning", "Financial Reporting", "Financial Statements Analysis", "Project Management", "Regulatory Compliance", "Regulatory Risk Assessment", "Stakeholder Management", "Tax Implications"], 
                                            ["Audit Compliance", "Communication", "Data Analytics", "Finance Business Partnering", "Financial Management", "Financial Planning", "Financial Reporting", "Regulatory Strategy", "Stakeholder Management", "Tax Implications"],
                                            ["Audit Compliance", "Communication", "Data Analytics", "Finance Business Partnering", "Financial Management", "Financial Planning", "Financial Reporting", "Regulatory Strategy", "Stakeholder Management", "Tax Implications"],
                                            ["Automated Equipment and Control Configuration", "Collaboration", "Communication", "Problem Solving"]
                                            ]
                                            '''
                
                matched_skills_results = [[],
                                          ["Accounting and Tax Systems", "Professional and Business Ethics"],
                                          ["Accounting and Tax Systems", "Professional and Business Ethics"]]
                expected_skill_match_scores = [0, 11, 17]
                expected_feedbacks = ["You are not recommended for this role","You are not recommended for this role", "You are not recommended for this role" ]



                #Setting Offset and limit
                offset = 0
                limit = 5
                search_params = {"role_search": role_search, "recency": recency, "country": country, "department": department, "required_skills": required_skills}
                listings_json = get_all_open_role_listings(search_params, offset=offset, limit=5)
                listings_dict = listings_json[0].get_json()

                print(listings_dict)
                data = listings_dict['data']
                for listing in data:
                    listing_index = data.index(listing)
                    skills_required_json = get_skills_required(listing['role_name'])

                    skills_required_dict = json.loads(skills_required_json.data)
                    skills_required_list = skills_required_dict['data']['skills_required']
                    #matched_skills = set(skills_required_list) & set(paired_skills)
                    staff_skills_list = staff_skills_dict['skill_names']

                    matched_skills = list(set(staff_skills_list) & set(skills_required_list))
                    matched_skills.sort()

                    unmatched_skills = list(set(skills_required_list) - set(matched_skills))
                    unmatched_skills.sort()

                    expected_matched_skills = matched_skills_results[listing_index]
                    expected_matched_skills.sort()

                    self.assertListEqual(matched_skills, expected_matched_skills)

                    skill_match_score = math.ceil((len(matched_skills) / (len(unmatched_skills) + len(matched_skills)) ) * 100)
                    print(skill_match_score)
                    expected_skill_match_score = expected_skill_match_scores[listing_index]
                    self.assertEqual(skill_match_score, expected_skill_match_score)


                    if skill_match_score < 20:
                        feedback = "You are not recommended for this role"
                    elif skill_match_score >= 40:
                        feedback = "You are recommended for this role"
                    else:
                        feedback = "You are highly recommended for this role"

                    expected_feedback = expected_feedbacks[listing_index]
                    self.assertEqual(feedback, expected_feedback)



                    '''
                    unmatched_skills = set(skills_required_list) - matched_skills
                    print("matched skills")
                    matched_skills = list(matched_skills)
                    matched_skills.sort()
                    print("unmatched skills")
                    unmatched_skills = list(unmatched_skills)
                    unmatched_skills.sort()
                    print(unmatched_skills)
                    

                    expected_unmatched_skills = unmatched_skills_results[listing_index]
                    expected_unmatched_skills.sort()

                    self.assertListEqual(unmatched_skills, expected_unmatched_skills)
                    '''

                

                '''
                    data = listings_dict['data']
                    for listing in data:
                        print(listing)
                        listing_index = data.index(listing)
                        skills_required_json = get_skills_required(listing['role_name'])
                        print(skills_required_json)
                
                        skills_required_dict = json.loads(skills_required_json.data)
                        skills_required_list = skills_required_dict['data']['skills_required']
                        matched_skills = set(skills_required_list) & set(paired_skills)
                        unmatched_skills = set(skills_required_list) - matched_skills
                        print("matched skills")
                        matched_skills = list(matched_skills)
                        matched_skills.sort()
                        print("unmatched skills")
                        unmatched_skills = list(unmatched_skills)
                        unmatched_skills.sort()
                        print(unmatched_skills)
                        

                        expected_unmatched_skills = unmatched_skills_results[listing_index]
                        expected_unmatched_skills.sort()

                        self.assertListEqual(unmatched_skills, expected_unmatched_skills)
                        '''

            

            



if __name__ == '__main__':
    unittest.main()

