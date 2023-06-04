# base class for job searcher modules
import csv

from neo4j import GraphDatabase
from typing import List

from modules.logger.logger import logger
from modules.models.models import Job
from modules.config.config import config, WeWorkRemotelyConfig


class JobSearchers:

    def __init__(self, keywords, category):
        self.keywords = keywords
        self.category = category
        self.jobs = []
        self.companies = []
        self.driver = GraphDatabase.driver(config.DATABASE_URL,
                                           auth=(config.DATABASE_USER,
                                                 config.DATABASE_PASS))

    def get_jobs(self) -> [Job]:
        """Return a list of jobs found in the categories. It has to be implemented in the child class"""
        raise NotImplementedError

    def __str__(self):
        return f"JobSearcher: {self.__class__.__name__}, keywords: {self.keywords}, category: {self.category}"

    def jobs_to_csv(self):
        """Save job data to a CSV file."""
        with open(WeWorkRemotelyConfig.CSV_FILE_NAME, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["id", "name", "description", "company", "url", "additional_info"])
            for job in self.jobs:
                writer.writerow([job.id, job.name, job.description, job.company, job.url, job.additional_info])

    def upload_to_neo4j(self):
        """
        Upload job data to Neo4j database.
        """
        with self.driver.session() as session:
            for company in self.companies:
                session.run(
                    """
                    MERGE (c:Company {id: $id})
                    SET c.name = $name, c.location = $location, c.website = $website, c.size = $size, c.established = $established, c.years_remote = $years_remote
                    """,
                    {'id': company.id, 'name': company.name, 'location': company.location, 'website': company.website,
                     'size': company.size, 'established': company.established, 'years_remote': company.years_remote}
                )

            for job in self.jobs:
                session.run(
                    """
                    MATCH (c:Company {name: $company_name})
                    MERGE (j:Job {id: $id})
                    SET j.name = $name, j.description = $description, j.url = $url, j.additional_info = $additional_info
                    MERGE (j)-[:BELONGS_TO]->(c)
                    """,
                    {'id': job.id, 'name': job.name, 'description': job.description, 'url': job.url,
                     'additional_info': job.additional_info, 'company_name': job.company}
                )
            self.driver.close()
