from flask import Blueprint, current_app, make_response, render_template, request, redirect, url_for, session
from domain.models import User
import domain.errors as err_codes
from domain.errors.messages import get_error_message

router = Blueprint('users', __name__)


@router.route('/login', methods=['GET'])
def login_form():
    return make_response(render_template('users/login.html'))


@router.route('/login', methods=['POST'])
def login_action():
    data = request.form.copy()
    message = None
    try:
        User(data['user_name'], 'No Name', data['password'])  # Validate form data

        user, _id = current_app.config['USER_REPOSITORY'].by_login(data['user_name'], data['password'])
    except AssertionError as err:
        message = get_error_message(*err.args)
        message = f'{err.args[0]}: {message}'
    else:
        session['session_id'] = _id

        return make_response(redirect(url_for('home')))

    return make_response(render_template(
        'users/login.html',
        user_name=data['user_name'],
        error=message,
    ))


@router.route('/register', methods=['GET'])
def register_form():
    return make_response(render_template('users/register.html'))


@router.route('/register', methods=['POST'])
def register_action():
    data = request.form.copy()
    message = None
    try:
        user = User(data['user_name'], data['full_name'], data['password'])  # Validate form data

        current_app.config['USER_REPOSITORY'].create(user)
    except AssertionError as err:
        message = get_error_message(*err.args)
        message = f'{err.args[0]}: {message}'
    else:
        return make_response(redirect(url_for('users.login_form')))

    return make_response(render_template(
        'users/register.html',
        user_name=data['user_name'],
        full_name=data['full_name'],
        error=message,
    ))


@router.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return make_response(redirect(url_for('home')))


@router.route('/profile', methods=['GET'])
def profile_form():
    user = current_app.config['USER_REPOSITORY'].by_id(session['session_id'])
    return make_response(render_template('users/profile.html', user=user))


@router.route('/profile', methods=['POST'])
def profile_action():
    data = request.form.copy()
    message = None
    user = current_app.config['USER_REPOSITORY'].by_id(session['session_id'])
    try:
        copy_user = User.load(user.export())
        if 'old_password' in data:
            assert data['new_password'] == data['confirm_new_password'], err_codes.PASSWORD_NOT_MATCH
            copy_user, _ = current_app.config['USER_REPOSITORY'].by_login(user.user_name, data['old_password'])
            copy_user.set_password(data['new_password'], data['old_password'])

        if 'user_name' in data:
            copy_user.user_name = data['user_name']

        if 'full_name' in data:
            copy_user.full_name = data['full_name']

    except AssertionError as err:
        message = get_error_message(*err.args)
        message = f'{err.args[0]}: {message}'
    else:
        current_app.config['USER_REPOSITORY'].update(session['session_id'], copy_user)
        return redirect(url_for('home'))

    return make_response(render_template('users/profile.html', error=message, user=user))


@router.route('/view/<user_name>', methods=['GET'])
def by_id(user_name: str):
    pass
