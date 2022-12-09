from abc import abstractmethod
from abc import ABC
from typing import Optional
import requests
import json

from flask import redirect

from config.settings import Settings
from db.user_service import UserService

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

    def callback(self, auth_code) -> dict:
        response = requests.get(url='https://oauth.vk.com/access_token',
                                params={'client_id': self.app_id,
                                        'client_secret': self.secret,
                                        'redirect_uri': self.redirect_uri,
                                        'code': auth_code}).json()
        return UserService().oauth_authorize(email=response['email'], social_id=str(response['user_id']),
                                             social_name='VK')
