from random import choice
from string import ascii_letters, digits, punctuation
from faker import Faker


fake = Faker('ru_RU')


def get_name():
    name = fake.name_nonbinary()
    if len(name) <= 256:
        return name


def get_company():
    company = fake.large_company()
    if len(company) <= 256:
        return company


def get_boundary_name(name_length: int):
    name = fake.name_nonbinary()
    while len(name) < name_length:
        name += f' {fake.name_nonbinary()}'
    return name[:name_length+1]


def get_boundary_company(company_length: int):
    company = fake.large_company()
    while len(company) < company_length:
        company += f' {fake.catch_phrase()}'
    return company[:company_length+1]


def bad_field_generator():
    return ''.join(
        [choice(ascii_letters + digits + punctuation) for n in range(18)]
    )
