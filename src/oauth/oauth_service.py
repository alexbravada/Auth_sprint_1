from abc import abstractmethod
from abc import ABC
from typing import Optional
import requests
import json
import base64
from flask import redirect

from config.settings import Settings
from db.user_service import UserService
from utils.jaeger_wraps import trace
from urllib.parse import urlencode

SETTINGS = Settings()


class OAuthAbstract(ABC):
    @abstractmethod
    def authorize(self):
        pass

    @abstractmethod
    def callback(self, auth_code: Optional):
        pass


class VKOAuth(OAuthAbstract):
    def __init__(self):
        super().__init__()
        self.settings = SETTINGS.VK.dict()
        self.app_id = self.settings.get('id')
        self.secret = self.settings.get('secret')
        self.service_key = self.settings.get('service_key')

        self.redirect_uri = f'{SETTINGS.BASE_URL}/api/v1/oauth/callback/vk'

    def authorize(self):
        '''
        display=page - open VK authorization in separate window
        scope=4194306 - byte mask for 'friends' and 'email' permissions
        response_type=code - required
        '''
        return redirect(
            f'https://oauth.vk.com/authorize?client_id={self.app_id}&redirect_uri={self.redirect_uri}'
            f'&display=page&scope=4194306&response_type=code&v=5.131',
            code=302)

    @trace('VKOAuth.callback')
    def callback(self, auth_code, useragent) -> dict:
        @trace('VKOAuth.callback.token_swap')
        def token_swap() -> dict:
            return requests.get(url='https://oauth.vk.com/access_token',
                                params={'client_id': self.app_id,
                                        'client_secret': self.secret,
                                        'redirect_uri': self.redirect_uri,
                                        'code': auth_code}).json()

        data = token_swap()
        return UserService().oauth_authorize(email=data['email'], social_id=str(data['user_id']),
                                             social_name='VK', useragent=useragent)


class YandexOAuth(OAuthAbstract):
    def __init__(self):
        super().__init__()
        self.settings = SETTINGS.Yandex.dict()
        self.app_id = self.settings.get('id')
        self.secret = self.settings.get('secret')

        self.redirect_uri = f'{SETTINGS.BASE_URL}/api/v1/oauth/callback/yandex'

    def authorize(self):
        '''
        display=popup - open Yandex authorization in separate window
        response_type=code - required
        '''
        return redirect(
            f'https://oauth.yandex.ru/authorize?client_id={self.app_id}'  # &redirect_uri={self.redirect_uri}'
            f'&display=popup&response_type=code',
            code=302)

    @trace('YandexOAuth.callback')
    def callback(self, auth_code, useragent) -> dict:
        response = requests.post(
            'https://oauth.yandex.ru/token',
            urlencode({'grant_type': 'authorization_code',
                       'client_id': self.app_id,
                       'client_secret': self.secret,
                       'code': auth_code})).json()

        access_token = response['access_token']

        response = requests.get(
            'https://login.yandex.ru/info?',
            urlencode({'Authorization': 'OAuth',
                       'oauth_token': access_token})).json()

        return UserService().oauth_authorize(email=response['emails'][0], social_id=str(response['id']),
                                             social_name='YANDEX', useragent=useragent)

class GoogleOAuth(OAuthAbstract):
    def __init__(self):
        super().__init__()
        self.settings = SETTINGS.Google.dict()
        self.client_id = self.settings.get('client_id')
        self.client_secret = self.settings.get('client_secret')
        self.redirect_uri = f'{SETTINGS.BASE_URL}/api/v1/oauth/callback/google'
        self.scope = 'email profile openid'
        self.authorize_url = f'https://accounts.google.com/o/oauth2/auth?client_id={self.client_id}&access_type=offline&response_type=code&redirect_uri={self.redirect_uri}&scope={self.scope}'

    def authorize(self):
        return redirect(self.authorize_url, code=302)

    @trace('GoogleOAuth.callback')
    def callback(self, auth_code, useragent):
        @trace('GoogleOAuth.callback.token_swap')
        def token_swap() -> dict:
            return requests.post('https://oauth2.googleapis.com/token',
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
                                             social_name='GOOGLE', useragent=useragent)
