import random
import requests

from mimesis import Person

from conftest import HOST


def test_signup_valid_data():
    '''
    test with valid autogenerate data
    '''
    mimerand = Person()
    headers = {"Content-Type": "application/json; charset=utf-8"}
    url = f'{HOST}/api/v1/auth/user/signup'
    data = {'email': mimerand.email(unique=True), 'password': str(random.randint(0, 65536)),
            'first_name': mimerand.first_name(), 'last_name': mimerand.last_name()}
    response = requests.post(url=url,
                             json=data,
                             headers=headers
                             )
    assert response.status_code == 201


def test_signin_valid_data():
    mimerand = Person()
    headers = {"Content-Type": "application/json; charset=utf-8"}
    url = f'{HOST}/api/v1/auth/user/signin'
    data = {'email': 'test', 'password': 'test'}
    response = requests.post(url=url,
                             json=data,
                             headers=headers
                             )
    assert 'access_token' in response.json()


def test_logout(login):
    headers = {"Content-Type": "application/json; charset=utf-8",
               "Authorization": f"Bearer {login.get('refresh_token')}"}
    url = f'{HOST}/api/v1/auth/user/logout'
    data = {'access_token': login.get('access_token')}
    response = requests.post(url=url,
                             json=data,
                             headers=headers
                             )
    assert response.status_code == 200


def test_logout_all(login):
    headers = {"Content-Type": "application/json; charset=utf-8",
               "Authorization": f"Bearer {login.get('access_token')}"}
    url = f'{HOST}/api/v1/auth/user/logout_all'
    response = requests.post(url=url,
                             headers=headers
                             )
    assert response.status_code == 200


def test_change_password(login):
    mimerand = Person()
    headers = {"Content-Type": "application/json; charset=utf-8",
               "Authorization": f"Bearer {login.get('access_token')}"}
    url = f'{HOST}/api/v1/auth/user/change_password'
    new_pass = mimerand.password()
    data = {
        'email': 'test',
        'old_password': 'test',
        'new_password': new_pass
    }
    response = requests.post(url=url,
                             headers=headers,
                             json=data
                             )

    data_rollback = {
        'email': 'test',
        'old_password': new_pass,
        'new_password': 'test'
    }
    response_rollback = requests.post(url=url,
                                      headers=headers,
                                      json=data_rollback
                                      )
    assert response.status_code == 200


def test_access(login):
    headers = {"Content-Type": "application/json; charset=utf-8",
               "Authorization": f"Bearer {login.get('access_token')}"}
    url = f'{HOST}/api/v1/auth/user/access'
    response = requests.post(url=url,
                             headers=headers,
                             )
    assert response.status_code == 200


def test_get_refresh(login):
    headers = {"Content-Type": "application/json; charset=utf-8",
               "Authorization": f"Bearer {login.get('refresh_token')}"}
    url = f'{HOST}/api/v1/auth/user/refresh'
    data = {'access_token': login.get('access_token')}
    response = requests.post(url=url,
                             json=data,
                             headers=headers
                             )
    assert response.status_code == 200
