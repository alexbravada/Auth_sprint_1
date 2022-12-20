import requests


def sign_up(email, password):
    #curl -X POST -H "Content-Type: application/json" -d '{"email":"test_user", "password":"123"}' http://127.0.0.1:5000/auth/signup
    url = "http://127.0.0.1:5000/auth/signup"
    data = {"email": email, "password":password}
    headers = {'Content-type': 'application/json'}
    response = requests.post(url, json=data, headers=headers)
    return f'sing_up status: {response.status_code}'


def sign_in(email, password):
    #curl -X POST -H "Content-Type: application/json" -d '{"email":"test_user", "password":"123"}' http://127.0.0.1:5000/auth/signin
    url = "http://127.0.0.1:5000/auth/signin"
    data = {"email": email, "password":password}
    headers = {'Content-type': 'application/json'}
    response = requests.post(url, json=data, headers=headers)
    return f'sing_in status: {response.status_code}'


def refresh():
    headers = {"Authorization": "Bearer ayJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY2Njg4MTgxMiwianRpIjoiNDU0ODdkZmItYjE4NS00NmVmLTkxNDMtY2Y0OTYxZmIwNDNhIiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiI5NzQ1NzZ1aTRkZ2ZnZGZnZCIsIm5iZiI6MTY2Njg4MTgxMiwiZXhwIjoxNjY5NDczODEyfQ.vQrs7N3p-QIFBFidL4jrdzqvnOnbhX7ARW0aiAXfVzs"}
    data = {"login":"NOtoken", "password": "ssss", "access_token":"fsdfsd" }
    url = 'http://127.0.0.1:5000/auth/refresh'
    response = requests.post(url, json=data, headers=headers)


def start_test():
    which = input('1 - reg and loging\n2 - login\nInput: ')
    email=input('email: ')
    password=input('password: ')
    if int(which) < 2:
        test1 = sign_up(email, password)
    test2 = sign_in(email, password)


refresh()
