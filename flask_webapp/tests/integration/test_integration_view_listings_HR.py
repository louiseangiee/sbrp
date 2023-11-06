import json
import unittest
from app import app
from bs4 import BeautifulSoup

class TestAllListingsHR(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

        # Replace the following with your session data
        self.staff_id = 160008  # staff ID for Sally Loh HR Singapore
        self.role = 4  # HR
        self.staff_fname = "Sally"
        self.staff_lname = "Loh"
        self.staff_name = self.staff_fname + " " + self.staff_lname
        self.dept = "HR"
        self.country = "Singapore"
        self.email = "Sally.Loh@allinone.com.sg"

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

    def tearDown(self):
        # Clean up session data (log out if necessary)
        with self.client:
            # You may need to define a /logout route
            self.client.get('/logout')

    def test_all_listings_HR_with_filters(self):
        # Test with filters
        response = self.client.post('/all_listings_HR/1', data={
            'status': 'Open',
            'recency': 'Past month',
            'country': 'Singapore',
            'department': 'Engineering',
        })

        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.data, 'html.parser')

        # Assert elements within the rendered HTML template
        listing_divs = soup.find_all('div', class_='listing')
        self.assertEqual(len(listing_divs), 1)  # Should have only one listing

        # Example of assertions for specific elements within a listing
        role_name = listing_divs[0].find('h5', class_='card-title').text
        date_open = listing_divs[0].find('div', class_='date-open').text
        date_close = listing_divs[0].find('div', class_='date-close').text
        status = listing_divs[0].find('div', class_='status').text

        self.assertEqual(role_name, 'Junior Engineer')
        self.assertEqual(date_open, '05/11/2023')
        self.assertEqual(date_close, '10/11/2024')
        self.assertEqual(status, 'Open')
        # Add more assertions based on the structure of your HTML template

    def test_all_listings_HR_without_filters(self):
        # Test without filters
        response = self.client.post('/all_listings_HR/1', data={
        })

        self.assertEqual(response.status_code, 200)
        print(response.data)
        # soup = BeautifulSoup(response.data, 'html.parser')

        # Assert elements within the rendered HTML template when no filters are applied

        # Example of assertions for specific elements
        # num_results = soup.find('span', class_='num-results').text
        # staff_name = soup.find('span', class_='staff-name').text

        # Add more assertions based on the structure of your HTML template

if __name__ == '__main__':
    unittest.main()
