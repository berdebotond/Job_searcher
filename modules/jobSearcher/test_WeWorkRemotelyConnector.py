import unittest
from unittest.mock import patch, Mock, call
import neo4j
import requests
from bs4 import BeautifulSoup
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

from modules.jobSearcher.WeWorkRemotelyConnector import WeWorkRemotelyConnector
from modules.logger.logger import logger
from modules.models.models import Job, Company
from modules.config.config import config, WeWorkRemotelyConfig


class MyTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.driver = GraphDatabase.driver(config.DATABASE_URL, auth=(config.DATABASE_USER, config.DATABASE_PASS))


    @patch('requests.get')
    def test_check_status_code(self, mock_get):
        # Set up the mock object
        mock_get.return_value.status_code = 200
        connector = requests.get(WeWorkRemotelyConfig.BASE_URL)

        # This should not raise an exception
        WeWorkRemotelyConnector.check_status_code(200, WeWorkRemotelyConfig.BASE_URL)

        with self.assertRaises(ConnectionError):
            # This should raise a ConnectionError
            WeWorkRemotelyConnector.check_status_code(400, WeWorkRemotelyConfig.BASE_URL)

    def test_find_categories_urls_with_empty_page_source(self):
        connector = WeWorkRemotelyConnector(None, None)
        connector.page_source = ""
        categories_urls = connector.find_categories_urls()
        self.assertListEqual([], categories_urls)

    def test_find_categories_urls_with_page_source_that_does_not_contain_any_categories(self):
        connector = WeWorkRemotelyConnector("", "")
        connector.page_source = """
        <div class="spacer js-gps-track" data-gps-track="linkedquestion.click({ source_post_id: 15453283, 
        target_question_id: 2784519, position: 3 })">
		<a href="https://stackoverflow.com/q/2784519?lq=1" title="Question score 
		(upvotes - downvotes)"><div class="answer-votes answered-accepted default">6</div></a>
		<a href="https://stackoverflow.com/questions/2784519/how-do-i-unit-test-the-methods
		-in-a-method-object?noredirect=1&amp;lq=1" class="question-hyperlink">How do I unit test the 
		methods in amethod object?</a></div>
        """
        categories_urls = connector.find_categories_urls()
        self.assertListEqual([], categories_urls)

    def test_find_categories_urls_with_page_source_that_contains_one_category(self):
        connector = WeWorkRemotelyConnector("", "")
        categories_urls = connector.find_categories_urls()
        logger.info(f'Categories: {categories_urls}')
        self.assertIn("/categories/remote-full-stack-programming-jobs", categories_urls)
        self.assertIn("/categories/remote-back-end-programming-jobs", categories_urls)

    def test_check_status_code_with_200_status_code(self):
        status_code = 200
        url = "https://www.google.com"
        WeWorkRemotelyConnector.check_status_code(status_code, url)
        self.assertLogs(level="INFO")

    def test_check_status_code_with_400_status_code(self):
        status_code = 400
        url = "https://www.google.com"
        with self.assertRaises(ConnectionError):
            WeWorkRemotelyConnector.check_status_code(status_code, url)
        self.assertLogs(level="ERROR")

    def test_check_status_code_with_500_status_code(self):
        status_code = 500
        url = "https://www.google.com"
        with self.assertRaises(ConnectionError):
            WeWorkRemotelyConnector.check_status_code(status_code, url)
        self.assertLogs(level="ERROR")

    """
    def test_get_jobs_with_empty_categories(self):
        connector = WeWorkRemotelyConnector("", "")
        jobs = connector.get_jobs(limitation=70)
        connector.jobs_to_csv()
        self.assertGreater(len(jobs), 1)
        self.assertEqual(Job, type(jobs[0]))
        connector.jobs_to_csv()
        connector.save_to_db()
    """

    def check_neo4j(self):

        try:
            with self.driver.session() as session:
                session.run("RETURN 1")
            return True
        except Exception as e:
            logger.debug(f"Neo4j is not running: {e}")
            return False

    def test_upload_to_neo4j(self):

        """
        Integration test for uploading to neo4j, neo4j has to run,
        if it's running the test pass with warnings
        """
        # Need neo4j running if nto running skip test
        if self.check_neo4j() is False:
            logger.warn("Neo4j is not running, skipping test")
            return

        neo4j_obj = WeWorkRemotelyConnector("", "")  # Initialize as required
        neo4j_obj.companies = [
            Company(id="1", name="Company1", location="Location1", website="www.company1.com", size="100",
                    established="2000", years_remote="10"),
            Company(id="2", name="Company2", location="Location2", website="www.company2.com", size="200",
                    established="2001", years_remote="11"),
            Company(id="3", name="Company3", location="Location3", website="www.company3.com", size="300",
                    established="2002", years_remote="12"),
        ]

        # Create some mock jobs
        neo4j_obj.jobs = [
            Job(id="2", name="Job3", description="Description1", url="www.job1.com", additional_info="Additional Info1",
                company="Company3"),
            Job(id="2", name="Job2", description="Description2", url="www.job2.com", additional_info="Additional Info2",
                company="Company3"),
            Job(id="3", name="Job4", description="Description3", url="www.job3.com", additional_info="Additional Info3",
                company="Company3"),
        ]

        neo4j_obj.upload_to_neo4j()

        # Check if the companies were uploaded
        with self.driver.session() as session:
            result = session.run("MATCH (c:Company) RETURN c")
            self.assertEqual(len(neo4j_obj.companies), len(result.data()))


if __name__ == '__main__':
    unittest.main()
