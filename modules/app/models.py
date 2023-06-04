from graphene import String, ID, ObjectType


class Company(ObjectType):
    id = ID(required=True)
    name = String(required=True)
    location = String(required=True)
    website = String(required=True)
    size = String(required=True)
    established = String(required=True)
    years_remote = String(required=True)


class Job(ObjectType):
    id = ID(required=True)
    name = String(required=True)
    description = String(required=True)
    url = String(required=True)
    additional_info = String(required=True)
    company = Field(Company, required=True)


class Query(ObjectType):
    companies = List(Company)
    jobs = List(Job)


schema = Schema(query=Query)