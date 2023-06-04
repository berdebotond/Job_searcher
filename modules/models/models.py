from dataclasses import dataclass


@dataclass
class Company:
    id: str
    name: str
    location: str
    website: str
    size: str
    established: str
    years_remote: str


@dataclass
class Job:
    id: str
    name: str
    description: str
    url: str
    additional_info: str
    company: str
