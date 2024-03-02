from flask import Flask
from dotenv import load_dotenv
from os import environ as env

from domain.providers import PasswordHasher
from infrastructure.providers import PASSWORD_HASHER_PROVIDERS

from infrastructure.repositories.users import MysqlUnsafeRepository as UserMysqlUnsafeRepository
from infrastructure.repositories.posts import MysqlUnsafeRepository as PostMysqlUnsafeRepository

load_dotenv()

app = Flask(__name__)

CONFIG_PASSWORD_HASHER = env.get('DOMAIN_PASSWORD_HASHER', 'MD5')
CONFIG_REPOSITORY_PROVIDER = env.get('REPOSITORY_PROVIDER', None)

assert CONFIG_PASSWORD_HASHER in PASSWORD_HASHER_PROVIDERS, \
    f'unknown password hasher provider: {CONFIG_PASSWORD_HASHER}'
PasswordHasher.provide_hasher(PASSWORD_HASHER_PROVIDERS[CONFIG_PASSWORD_HASHER]())
app.config['PASSWORD_HASHER'] = PasswordHasher

if CONFIG_REPOSITORY_PROVIDER == 'MYSQL_UNSAFE':
    app.config['USER_REPOSITORY'] = UserMysqlUnsafeRepository()
    app.config['POST_REPOSITORY'] = PostMysqlUnsafeRepository()
else:
    raise AssertionError(f'unknown repository provider: {CONFIG_REPOSITORY_PROVIDER}')

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
