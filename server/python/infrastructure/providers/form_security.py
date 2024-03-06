import datetime
from typing import Union, Literal

from flask import session, current_app, request
from domain.providers import FormSecurityProvider
from infrastructure.utils import create_salt
from os import environ as env
import jwt
import httpx

FORM_SECURITY_PROVIDERS = {
    'NULL': lambda: NullFormSecurityProvider(),
    'CSRF': lambda: CSFRFormSecurityProvider(),
    'JWT_HEADLESS': lambda: HeadlessJWTFormSecurityProvider(),
    'CF_TURNSTILE': lambda: TurnStileFormSecurityProvider(env['CF_TURNSTILE_KEY'], env['CF_TURNSTILE_SECRET']),
}


class NullFormSecurityProvider(FormSecurityProvider):
    """
    Null provider, always sent true
    """
    target_key = 'none'

    def do_inject(self, ret_type: Union[Literal['input'], Literal['code']]) -> str:
        if ret_type == 'input':
            return f'<input type="hidden" name="{self.target_key}" value="">'

        return ''

    def do_validate(self, code: str) -> bool:
        return True


class CSFRFormSecurityProvider(FormSecurityProvider):
    """
    CSFR Form Security Provider
    """
    target_key = 'csfr'

    def do_inject(self, ret_type: Union[Literal['input'], Literal['code']]) -> str:
        token = create_salt(128)
        session[self.target_key] = token
        if ret_type == 'input':
            return f'<input type="hidden" name="{self.target_key}" value="{token}">'

        return token

    def do_validate(self, code: str) -> bool:
        return self.target_key in session and session[self.target_key] == code


class HeadlessJWTFormSecurityProvider(FormSecurityProvider):
    """
    Headless JWT Form Security Provider
    """
    target_key = 'jwt'

    @staticmethod
    def _create_payload():
        if request.headers.getlist("X-Forwarded-For"):
            ip = request.environ['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.remote_addr
        return {
            'user_agent': str(request.user_agent),
            'ip': ip,
        }

    @staticmethod
    def _expiration_time():
        return (datetime.datetime.utcnow() + datetime.timedelta(minutes=15)).timestamp()

    def do_inject(self, ret_type: Union[Literal['input'], Literal['code']]) -> str:
        token = jwt.encode(
            self._create_payload(),
            current_app.secret_key,
            algorithm='HS256',
            headers={'exp': self._expiration_time()},
        )

        session[self.target_key] = token
        if ret_type == 'input':
            return f'<input type="hidden" name="{self.target_key}" value="{token}">'

        return token

    def do_validate(self, code: str) -> bool:
        if self.target_key in session:
            try:
                payload = jwt.decode(code, current_app.secret_key, algorithms=['HS256'], verify=True)
            except jwt.DecodeError:
                return False
            else:
                target = self._create_payload()
                for k, v in payload.items():
                    if v != target[k]:
                        return False

                return True

        return False


class TurnStileFormSecurityProvider(FormSecurityProvider):
    """
    CloudFlare TurnStile Security Provider
    """
    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key

    target_key = 'cf-turnstile-response'

    def do_inject(self, ret_type: Union[Literal['input'], Literal['code']]) -> str:
        return f'''
        <script src="https://challenges.cloudflare.com/turnstile/v0/api.js" defer></script>
        <div class="cf-turnstile is-center" data-sitekey="{self.api_key}"></div>
        '''

    def do_validate(self, code: str) -> bool:
        response = httpx.post('https://challenges.cloudflare.com/turnstile/v0/siteverify', json={
            'secret': self.secret_key,
            'response': code,
        }).json()

        return response.get('success', False)
