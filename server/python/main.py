from flask import Flask, url_for, redirect, session
from markupsafe import Markup

from flask_session import Session
from dotenv import load_dotenv
from os import environ as env

from domain.providers import PasswordHasher, FormSecurityProvider
from infrastructure.providers.password import PASSWORD_HASHER_PROVIDERS
from infrastructure.providers.form_security import FORM_SECURITY_PROVIDERS

from infrastructure.repositories.users import (
    MysqlUnsafeRepository as UserMysqlUnsafeRepository,
    MysqlRepository as UserMysqlSafeRepository
)
from infrastructure.repositories.posts import (
    MysqlUnsafeRepository as PostMysqlUnsafeRepository,
    MysqlRepository as PostMysqlSafeRepository
)

from routes.users import router as users_router
from routes.posts import router as posts_router

load_dotenv()

app = Flask(__name__, static_folder=None)
app.secret_key = env.get('SECRET_KEY', 'test')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
Session(app)

CONFIG_PASSWORD_HASHER = env.get('DOMAIN_PASSWORD_HASHER', 'MD5')
CONFIG_FORM_SECURITY = env.get('DOMAIN_FORM_SECURITY', 'CSRF')
CONFIG_REPOSITORY_PROVIDER = env.get('REPOSITORY_PROVIDER', None)

assert CONFIG_PASSWORD_HASHER in PASSWORD_HASHER_PROVIDERS, \
    f'unknown password hasher provider: {CONFIG_PASSWORD_HASHER}'

assert CONFIG_FORM_SECURITY in FORM_SECURITY_PROVIDERS, f'unknown form security provider: {CONFIG_FORM_SECURITY}'

PasswordHasher.provide_hasher(PASSWORD_HASHER_PROVIDERS[CONFIG_PASSWORD_HASHER]())
app.config['PASSWORD_HASHER'] = PasswordHasher

FormSecurityProvider.provide(FORM_SECURITY_PROVIDERS[CONFIG_FORM_SECURITY]())
app.config['FORM_SECURITY_PROVIDER'] = FormSecurityProvider

if CONFIG_REPOSITORY_PROVIDER == 'MYSQL_UNSAFE':
    app.config['USER_REPOSITORY'] = UserMysqlUnsafeRepository()
    app.config['POST_REPOSITORY'] = PostMysqlUnsafeRepository()
elif CONFIG_REPOSITORY_PROVIDER == 'MYSQL_SAFE':
    app.config['USER_REPOSITORY'] = UserMysqlSafeRepository()
    app.config['POST_REPOSITORY'] = PostMysqlSafeRepository()
else:
    raise AssertionError(f'unknown repository provider: {CONFIG_REPOSITORY_PROVIDER}')


@app.context_processor
def template_context():
    return dict(form_security=lambda: Markup(app.config['FORM_SECURITY_PROVIDER'].inject('input')))


@app.route('/', methods=['GET'])
def home():
    if 'session_id' not in session:
        return redirect(url_for('users.login_form'))

    return redirect(url_for('posts.home'))


app.register_blueprint(users_router, url_prefix='/users')
app.register_blueprint(posts_router, url_prefix='/posts')

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
