from flask import Blueprint, current_app, make_response, render_template, session, request, redirect, url_for
from domain.models import Post
from domain.errors.messages import get_error_message

router = Blueprint('posts', __name__)


@router.route('/', methods=['GET'])
def home():
    user = current_app.config['USER_REPOSITORY'].by_id(session['session_id'])
    posts = current_app.config['POST_REPOSITORY'].list()
    return make_response(render_template(
        'posts/home.html',
        user=user,
        posts=posts,
    ))


@router.route('/create', methods=['GET'])
def create_form():
    user = current_app.config['USER_REPOSITORY'].by_id(session['session_id'])
    return make_response(render_template(
        'posts/create.html',
        user=user,
    ))


@router.route('/create', methods=['POST'])
def create_action():
    data = request.form.copy()
    user = current_app.config['USER_REPOSITORY'].by_id(session['session_id'])

    message = None

    try:
        content = data.get('content', None)
        if content == '':
            content = None

        post = Post(title=data['title'], content=content, user_name=user.user_name)
    except AssertionError as err:
        message = get_error_message(*err.args)
        message = f'{err.args[0]}: {message}'
    else:
        current_app.config['POST_REPOSITORY'].create(post)
        return make_response(redirect(url_for('home')))

    return make_response(render_template(
        'posts/create.html',
        error=message,
        user=user,
    ))

