from abc import abstractmethod
from abc import ABC
from typing import Optional
import requests
import json

from flask import redirect

from config.settings import Settings
from db.user_service import UserService
from utils.jaeger_wraps import trace

#import google.oauth2.credentials
#import google_auth_oauthlib.flow
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
            f'https://oauth.yandex.ru/authorize?client_id={self.app_id}&redirect_uri={self.redirect_uri}'
            f'&display=popup&scope=4194306&response_type=code',
            code=302)

    def callback(self, auth_code, useragent) -> dict:
        response = requests.get(
            url='https://yandex.ru/dev/id/doc/dg/oauth/reference/auto-code-client.html#auto-code-client__get-token',
            params={'client_id': self.app_id,
                    'client_secret': self.secret,
                    'redirect_uri': self.redirect_uri,
                    'code': auth_code}).json()
        return UserService().oauth_authorize(email=response['email'], social_id=str(response['user_id']),
                                             social_name='YANDEX', useragent=useragent)


class GoogleOAuth(OAuthAbstract):
    def __init__(self):
        super().__init__()
        self.settings = SETTINGS.Google.dict()
        self.client_id = self.settings.get('client_id')
        self.client_secret = self.settings.get('client_secret')
        self.redirect_uri = f'{SETTINGS.BASE_URL}/api/v1/oauth/callback/google'
        self.authorize_url = 'https://accounts.google.com/o/oauth2/v2/auth?client_id={self.client_id}&access_type=offline&response_type=code&redirect_uri={self.redirect_uri}'

    def authorize(self):
        #return redirect()
        # https://accounts.google.com/o/oauth2/v2/auth
        #.../auth/userinfo.profile
        # .../auth/userinfo.email
        # /openid
        
        return redirect(self.authorize_url, code=302)

    def callback(self, auth_code, useragent):
        params = {'code': auth_code,
                  'client_id': self.client_id,
                  'client_secret': self.client_secret,
                  'redirect_uri': self.redirect_uri,
                  'grant_type': 'authorization_code'
                  }
        response = requests.post('https://oauth2.googleapis.com/token', data=params)
        return UserService().oauth_authorize(email=response['email'], social_id=str(response['user_id']),
                                             social_name='Google', useragent=useragent)
