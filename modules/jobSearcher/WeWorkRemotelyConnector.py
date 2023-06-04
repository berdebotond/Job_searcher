# Import required libraries
import requests
import csv
import uuid
from bs4 import BeautifulSoup
import re
import traceback

# Import user-defined modules
from modules.jobSearcher.jobSearchers import JobSearchers
from modules.config.config import WeWorkRemotelyConfig
from modules.logger.logger import logger
from modules.models.models import Job, Company


# Define a class for connecting and retrieving job data from WeWorkRemotely
class WeWorkRemotelyConnector(JobSearchers):

    def __init__(self, keywords, category):
        super().__init__(keywords, category)

        # Get the HTML content from the WeWorkRemotely URL
        page_source = requests.get(WeWorkRemotelyConfig.BASE_URL)
        # Check the status of the request
        self.check_status_code(page_source.status_code, WeWorkRemotelyConfig.BASE_URL)

        # Store the HTML content
        self.page_source = page_source.text
        logger.info(f"Connected to {WeWorkRemotelyConfig.BASE_URL} with status code {page_source.status_code}")

        # Extract the category URLs from the page source
        self.categories = self.find_categories_urls()


    # Method to extract category URLs
    def find_categories_urls(self) -> list[str]:
        matches = re.findall(WeWorkRemotelyConfig.REGEX_FOR_CATEGORIES, self.page_source)
        logger.debug(f'Categories: {matches}')
        return matches

    # Method to get jobs from the categories
    def get_jobs(self, limitation: int = None, keywords: list[str] = None) -> list:
        for category in self.categories:
            category_page = requests.get(WeWorkRemotelyConfig.BASE_URL + category)
            self.check_status_code(category_page.status_code, WeWorkRemotelyConfig.BASE_URL + category)
            self.__find_jobs(category_page.text, limitation=limitation, keywords=keywords)

        return self.jobs

    # Method to check the status code of a web request
    @staticmethod
    def check_status_code(status_code, url):
        if status_code > 399:
            logger.error(f"Error connecting to {url} with status code {status_code}")
            raise ConnectionError(f"Error connecting to {url} with status code {status_code}")
        logger.info(f"Connected to {url} with status code {status_code}")

    # Private method to find job URLs from the page source
    def __find_jobs(self, text: str, limitation: int = None, keywords: list[str] = None) -> list:
        matches = re.findall(WeWorkRemotelyConfig.REGEX_FOR_JOBS, text)
        logger.debug(f'Jobs: {matches}')
        if not matches:
            logger.warning(f'No jobs found')
            return []

        # For each job URL, extract the job details
        for job_url in matches:
            if not job_url.startswith('/remote-jobs/'):
                continue
            job_page = requests.get(WeWorkRemotelyConfig.BASE_URL + job_url)
            self.check_status_code(job_page.status_code, WeWorkRemotelyConfig.BASE_URL + job_url)
            if not keywords or any(keyword not in job_page.text for keyword in keywords):
                soup = BeautifulSoup(job_page.text, 'html.parser')
                try:
                    job = self.__find_job_details(soup=soup, job_url=job_url)
                    if job.name in ["We Work Remotely: Advanced Remote Job Search",
                                    "Create a new job post",
                                    "We Work Remotely: Advanced Remote Job Search"]:
                        continue

                    self.jobs.append(job)
                    company_page = requests.get(f"{WeWorkRemotelyConfig.BASE_URL}/company/{job.company}")

                    self.check_status_code(company_page.status_code, WeWorkRemotelyConfig.BASE_URL + job_url)

                    soup = BeautifulSoup(company_page.text, 'html.parser')

                    company = self.__find_company_details(soup=soup, company_name=job.company)

                    logger.info(f"Found company: {job.company}")

                    if company.name not in [company_index.name for company_index in self.companies]:

                        self.companies.append({company.name: company})

                    if len(self.jobs) == limitation:
                        return self.jobs


                except Exception as e:
                    # print traceback
                    logger.error(f"Error finding job details with traceback: {traceback.format_exc()}")
        return self.jobs

    # Private method to find job details
    @staticmethod
    def __find_job_details(soup, job_url) -> Job:
        job_title = soup.find('meta', property='og:title')['content']
        job_description = soup.find('meta', property='og:description')['content']
        job_specifics = soup.body.text
        logger.info(f"Found job: {job_title} with description: {job_description} and specifics: {job_specifics}")
        company_name = job_title.split(" at ")[-1]
        job = Job(name=job_title,
                  id=str(uuid.uuid4()),  # Generate a unique id for the job
                  description=job_description,
                  additional_info=job_specifics,
                  company=company_name,
                  url=WeWorkRemotelyConfig.BASE_URL + job_url,
                  )
        return job

    @staticmethod
    def __find_company_details(soup, company_name) -> Company:
        hq_location = soup.find('div', class_='company-card').h3.span.text.strip()
        website = soup.find('div', class_='company-card').find('a')['href']
        company_size = soup.find('div', class_='company-card').find_all('h3')[2].span.text.strip()
        established = soup.find('div', class_='company-card').find_all('h3')[3].span.text.strip()
        years_remote = soup.find('div', class_='company-card').find_all('h3')[5].span.text.strip()
        return Company(name=company_name,
                       id=str(uuid.uuid4()),
                       location=hq_location,
                       website=website,
                       size=company_size,
                       established=established,
                       years_remote=years_remote
                       )
