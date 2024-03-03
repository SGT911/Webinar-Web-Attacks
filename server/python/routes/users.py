from flask import Blueprint, current_app, make_response, render_template, request, redirect, url_for, session
from domain.models import User
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
