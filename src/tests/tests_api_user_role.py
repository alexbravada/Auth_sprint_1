import random

import requests
from mimesis import Person


def test_show_user_role(login_admin):
    headers = {"Content-Type": "application/json; charset=utf-8",
               "Authorization": f"Bearer {login_admin.get('access_token')}"}
    url = 'http://127.0.0.1:5000/api/v1/auth/user/role'
    response = requests.get(url=url,
                            headers=headers
                            )
    assert response.status_code == 200


def test_user_add_role(login_admin, fetch_userid_n_roleid_separate):
    headers = {"Content-Type": "application/json; charset=utf-8",
               "Authorization": f"Bearer {login_admin.get('access_token')}"}
    url = 'http://127.0.0.1:5000/api/v1/auth/user/role/user_role_add'
    data = {'user_id': fetch_userid_n_roleid_separate.get('user_id'),
            'role_id': fetch_userid_n_roleid_separate.get('role_id')}
    response = requests.post(url=url,
                             json=data,
                             headers=headers
                             )
    assert response.status_code == 200


def test_user_check_role(login_admin):
    headers = {"Content-Type": "application/json; charset=utf-8",
               "Authorization": f"Bearer {login_admin.get('access_token')}"}
    url = f"http://127.0.0.1:5000/api/v1/auth/user/role/user_role_show/{random.randint(1, 2)}"
    response = requests.get(url=url,
                            headers=headers
                            )
    assert response.status_code == 200


def test_role_check_user(login_admin, fetch_userid_n_roleid_separate):
    headers = {"Content-Type": "application/json; charset=utf-8",
               "Authorization": f"Bearer {login_admin.get('access_token')}"}
    url = f"http://127.0.0.1:5000/api/v1/auth/user/role/role_user_show/{fetch_userid_n_roleid_separate.get('role_id')}"
    response = requests.get(url=url,
                            headers=headers
                            )
    assert response.status_code == 200


def test_user_role_remove(login_admin, fetch_userid_n_roleid_tuserrole):
    headers = {"Content-Type": "application/json; charset=utf-8",
               "Authorization": f"Bearer {login_admin.get('access_token')}"}
    url = 'http://127.0.0.1:5000/api/v1/auth/user/role/user_role_delete'
    data = {'user_id': fetch_userid_n_roleid_tuserrole.get('user_id'),
            'role_id': fetch_userid_n_roleid_tuserrole.get('role_id')}
    response = requests.delete(url=url,
                             json=data,
                             headers=headers
                             )
    assert response.status_code == 200