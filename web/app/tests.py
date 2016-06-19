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

if __name__ == '__main__':
    unittest.main()
