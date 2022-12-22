from abc import ABC
from abc import abstractmethod
from urllib.parse import urlencode

import requests
from flask import redirect

from config.settings import Settings
from db.user_service import UserService
from utils.jaeger_wraps import trace

SETTINGS = Settings()


class OAuthAbstract(ABC):
    @abstractmethod
    def authorize(self):
        pass

    @abstractmethod
    def callback(self, auth_code: str, useragent: str, state: str):
        pass


class VKOAuth(OAuthAbstract):
    def __init__(self):
        super().__init__()
        self.app_id = SETTINGS.VK.id
        self.secret = SETTINGS.VK.secret
        self.service_key = SETTINGS.VK.service_key
        self.redirect_uri = f'{SETTINGS.BASE_URL}/api/v1/oauth/callback/vk'
        self.authorize_url = f'https://oauth.vk.com/authorize?client_id={self.app_id}' \
                             f'&redirect_uri={self.redirect_uri}' \
                             f'&display=page&scope=4194306&response_type=code&v=5.131&state=vk'

    def authorize(self):
        return redirect(self.authorize_url, code=302)

    @trace('VKOAuth.callback')
    def callback(self, auth_code, useragent, state: str) -> dict:
        @trace('VKOAuth.callback.token_swap')
        def token_swap() -> dict:
            return requests.get(url='https://oauth.vk.com/access_token',
                                params={'client_id': self.app_id,
                                        'client_secret': self.secret,
                                        'redirect_uri': self.redirect_uri,
                                        'code': auth_code}).json()

        data = token_swap()
        return UserService().oauth_authorize(email=data['email'], social_id=str(data['user_id']),
                                             social_name=state.upper(), useragent=useragent)


class YandexOAuth(OAuthAbstract):
    def __init__(self):
        super().__init__()
        self.app_id = SETTINGS.Yandex.id
        self.secret = SETTINGS.Yandex.secret
        self.redirect_uri = f'{SETTINGS.BASE_URL}/api/v1/oauth/callback/yandex'
        self.authorize_url = f'https://oauth.yandex.ru/authorize?client_id={self.app_id}' \
                             f'&display=popup&response_type=code&state=yandex'


    def authorize(self):
        return redirect(self.authorize_url, code=302)


    @trace('YandexOAuth.callback')
    def callback(self, auth_code, useragent, state) -> dict:
        @trace('YandexOAuth.token_swap')
        def token_swap() -> dict:
            return requests.post(url='https://oauth.yandex.ru/token',
                                 data=urlencode({'grant_type': 'authorization_code',
                                                   'client_id': self.app_id,
                                                   'client_secret': self.secret,
                                                   'code': auth_code})).json()

        @trace('YandexOAuth.request_data')
        def request_data(swap_response_json: dict) -> dict:
            return requests.get(url='https://login.yandex.ru/info?',
                                params=urlencode({'Authorization': 'OAuth',
                                                  'oauth_token': swap_response_json['access_token']})).json()

        response = request_data(token_swap())
        return UserService().oauth_authorize(email=response['emails'][0], social_id=str(response['id']),
                                             social_name=state.upper(), useragent=useragent)


class GoogleOAuth(OAuthAbstract):
    def __init__(self):
        super().__init__()
        self.client_id = SETTINGS.Google.client_id
        self.client_secret = SETTINGS.Google.client_secret
        self.redirect_uri = f'{SETTINGS.BASE_URL}/api/v1/oauth/callback/google'
        self.scope = 'email profile openid'
        self.authorize_url = f'https://accounts.google.com/o/oauth2/auth?client_id={self.client_id}&' \
                             f'access_type=offline&response_type=code&redirect_uri={self.redirect_uri}&' \
                             f'scope={self.scope}&state=google'

    def authorize(self):
        return redirect(self.authorize_url, code=302)

    @trace('GoogleOAuth.callback')
    def callback(self, auth_code, useragent, state):
        @trace('GoogleOAuth.callback.token_swap')
        def token_swap() -> dict:
            return requests.post(url='https://oauth2.googleapis.com/token',
                                 data={'code': auth_code,
                                       'client_id': self.client_id,
                                       'client_secret': self.client_secret,
                                       'redirect_uri': self.redirect_uri,
                                       'grant_type': 'authorization_code'
                                       }).json()

        @trace('GoogleOAuth.callback.request_data')
        def request_data(data: dict) -> dict:
            return requests.get(url='https://www.googleapis.com/userinfo/v2/me',
                                headers={'Authorization': f"""{data['token_type']} {data['access_token']}"""}).json()

        response = request_data(token_swap())
        return UserService().oauth_authorize(email=response.get('email'), social_id=str(response.get('id')),
                                             social_name=state.upper(), useragent=useragent)
