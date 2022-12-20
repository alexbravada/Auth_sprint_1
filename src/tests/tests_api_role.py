import random
import requests

from mimesis import Person

from conftest import HOST


def test_add_role_valid(login_admin):
    mimerand = Person()
    headers = {"Content-Type": "application/json; charset=utf-8",
               "Authorization": f"Bearer {login_admin.get('access_token')}"}
    url = f'{HOST}/api/v1/auth/role/add'
    data = {'name': mimerand.name(),
            'description': mimerand.academic_degree()}
    response = requests.post(url=url,
                             json=data,
                             headers=headers
                             )
    assert response.status_code == 201


def test_delete_role(login_admin, create_role):
    headers = {"Content-Type": "application/json; charset=utf-8",
               "Authorization": f"Bearer {login_admin.get('access_token')}"}
    url = f'{HOST}/api/v1/auth/role/delete'
    data = {"id": create_role.get('id')}
    response = requests.delete(url=url,
                               json=data,
                               headers=headers
                               )
    assert response.status_code == 200


def test_show_roles_all(login_admin):
    headers = {"Content-Type": "application/json; charset=utf-8",
               "Authorization": f"Bearer {login_admin.get('access_token')}"}
    url = f'{HOST}/api/v1/auth/role'
    response = requests.get(url=url,
                            headers=headers
                            )
    assert response.status_code == 200


def test_show_role(login_admin, create_role):
    headers = {"Content-Type": "application/json; charset=utf-8",
               "Authorization": f"Bearer {login_admin.get('access_token')}"}
    url = f"{HOST}/api/v1/auth/role/{create_role.get('id')}"
    response = requests.get(url=url,
                            headers=headers
                            )
    assert response.status_code == 200


def test_update_role(login_admin, create_role):
    mimerand = Person()
    headers = {"Content-Type": "application/json; charset=utf-8",
               "Authorization": f"Bearer {login_admin.get('access_token')}"}
    url = f'{HOST}/api/v1/auth/role/update'
    randbool = random.randint(0, 1)
    description = mimerand.academic_degree() if randbool else None
    data = {"id": create_role.get('id'),
            "name": mimerand.name(),
            "description": description}
    response = requests.put(url=url,
                            json=data,
                            headers=headers
                            )
    assert response.status_code == 201
