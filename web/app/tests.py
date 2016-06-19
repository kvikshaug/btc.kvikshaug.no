import os
import unittest

# Before local imports, set test configuration
os.environ['CONFIGURATION'] = 'test'

from app import app
import database

class TestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        database.create_tables()

    def tearDown(self):
        database.drop_tables()

    def test_get_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
