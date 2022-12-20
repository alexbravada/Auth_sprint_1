import random

import requests

import pytest
from mimesis import Person

from src.db.role_service import RoleService


HOST = 'http://127.0.0.1:80'

@pytest.fixture()
def login() -> dict:
    headers = {"Content-Type": "application/json; charset=utf-8"}
    url = f'{HOST}/api/v1/auth/user/signin'
    data = {'email': 'northeast1802@yahoo.com', 'password': 'test'}
    response = requests.post(url=url,
                             json=data,
                             headers=headers
                             )
    return dict(response.json())


@pytest.fixture()
def login_changeemail() -> dict:
    headers = {"Content-Type": "application/json; charset=utf-8"}
    url = f'{HOST}/api/v1/auth/user/signin'
    data = {'email': 'test', 'password': 'test'}
    response = requests.post(url=url,
                             json=data,
                             headers=headers
                             )
    return dict(response.json())


@pytest.fixture()
def login_admin() -> dict:
    headers = {"Content-Type": "application/json; charset=utf-8"}
    url = f'{HOST}/api/v1/auth/user/signin'
    data = {'email': 'admin', 'password': 'admin'}
    response = requests.post(url=url,
                             json=data,
                             headers=headers
                             )
    return dict(response.json())


@pytest.fixture()
def create_role() -> dict:
    mimerand = Person()
    db = RoleService()
    return db.add_role(name=mimerand.name(), description=mimerand.academic_degree()).as_dict


@pytest.fixture()
def fetch_userid_n_roleid_separate() -> dict:
    db = RoleService()
    response_roles = [x.as_dict for x in db.show_all_roles()]
    role_id = str(response_roles[random.randint(0, len(response_roles) - 1)].get('id'))
    user_id = '1'
    return {'role_id': role_id, 'user_id': user_id}


@pytest.fixture()
def fetch_userid_n_roleid_tuserrole() -> dict:
    db = RoleService()
    responce = [x.as_dict for x in db.user_role_show_all()]
    randomint = random.randint(0, len(responce) - 1)
    role_id = str(responce[randomint].get('role_id'))
    user_id = str(responce[randomint].get('user_id'))
    return {'role_id': role_id, 'user_id': user_id}
