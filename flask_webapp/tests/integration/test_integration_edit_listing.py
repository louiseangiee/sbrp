import json
import unittest
from app import app

class TestEditListing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        app.config['TESTING'] = True
        cls.listing_id = 15
        cls.original_listing_data = None

    def setUp(self):
        self.session_headers = {"Content-Type": "application/json"}
        with self.client.session_transaction() as sess:
            sess['Staff_ID'] = 160008  # staff ID for Sally Loh HR Singapore
            sess['Role'] = 4  # HR role
            sess['Staff_Fname'] = "Sally"
            sess['Staff_Lname'] = "Loh"
            sess['Staff_Name'] = "Sally Loh"
            sess['Dept'] = "HR"
            sess['Country'] = "Singapore"
            sess['Email'] = "Sally.Loh@allinone.com.sg"

        # Fetch and store the current state of the listing
        response = self.client.get('/get_listing_by_id/' + str(self.listing_id))
        print('Response data:', response.data)  # This will print the response data to help debug
        if response.status_code == 200:
            fetched_data = response.get_json()['data']
            # Map the fetched data to the test data structure
            TestEditListing.original_listing_data = {
                "listing_id": fetched_data['listing_id'],
                "title": fetched_data['role_name'],
                "department": fetched_data['dept'],
                "country": fetched_data['country'],
                "vacancy": fetched_data['num_opening'],
                "manager": fetched_data['reporting_mng'],
                "startDate": fetched_data['date_open'].split("T")[0],  # Assuming the date is in ISO format with 'T' separator
                "endDate": fetched_data['date_close'].split("T")[0],
            }
        else:
            self.fail(f"Setup failed: Unable to fetch original listing data. Status code: {response.status_code}, Response: {response.data}")
    def tearDown(self):
        # Restore the original listing data if it was changed
        if TestEditListing.original_listing_data is not None:
            response = self.client.put(
                '/update/check_listing_exist/' + str(self.listing_id),
                data=json.dumps(TestEditListing.original_listing_data),
                headers=self.session_headers
            )
            self.assertEqual(response.status_code, 201, "Failed to restore the listing to its original state")
            TestEditListing.original_listing_data = None

        # Additional cleanup can be performed here if necessary

    def test_edit_listing(self):
        # Define the updated test data for the listing
        updated_test_data = {
            "listing_id": self.listing_id,
            "title": "Senior Engineer",
            "department": "Engineering",
            "country": "Singapore",
            "vacancy": 1,
            "manager": 150866,
            "startDate": "2024-08-01",
            "endDate": "2024-12-31",
        }

        # Perform the update
        response = self.client.put(
            '/update/check_listing_exist/' + str(updated_test_data['listing_id']),
            data=json.dumps(updated_test_data),
            headers=self.session_headers
        )
        self.assertEqual(response.status_code, 201)

        # You can add more assertions here to check the content of the response

    def test_edit_listing_invalid_id(self):
        # Attempt to edit a listing that does not exist
        invalid_test_data = {
            "listing_id": 999,  # Assuming 999 is an ID that does not exist
            "title": "Senior Engineer",
            "department": "Engineering",
            "country": "Singapore",
            "vacancy": 1,
            "manager": 150866,
            "startDate": "2024-08-01",
            "endDate": "2024-12-31",
        }

        # Perform the update
        response = self.client.put(
            '/update/check_listing_exist/' + str(invalid_test_data['listing_id']),
            data=json.dumps(invalid_test_data),
            headers=self.session_headers
        )
        self.assertEqual(response.status_code, 404)  # Assuming 404 is returned for non-existent records

        # Additional assertions for the invalid case can be added here

if __name__ == '__main__':
    unittest.main()
