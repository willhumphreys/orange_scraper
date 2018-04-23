import unittest
import os
from scrape import my_handler

class ScraperTest(unittest.TestCase):

    def testScraper(self):
        forge_api_key = os.environ.get("forge_api_key", "Not Set")
        data_url = os.environ.get("data_url", "Not Set")
        db_table = os.environ.get('db_table', "Not Set")

        print(forge_api_key)
        print(data_url)
        print(db_table)

        event = {"forge_api_key" : forge_api_key, "data_url" : data_url, "db_table" : db_table }
        self.assertEqual(my_handler(event,None), {'persisted_items': 'a small tree'})