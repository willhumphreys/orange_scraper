import unittest
from scrape import my_handler

def fun(x):
    return x + 1

class ScraperTest(unittest.TestCase):

    def testScraper(self):
        event = {"forge_api_key" : "1234", "data_url" : "http://hello.there.com", "db_table" : "SentimentTest" }
        self.assertEqual(fun(3), 4)
        self.assertEqual(my_handler(event,None))