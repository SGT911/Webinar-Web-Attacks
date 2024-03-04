from flask import Blueprint, current_app, make_response, render_template, session, request

router = Blueprint('posts', __name__)


@router.route('/', methods=['GET'])
def home():
    user = current_app.config['USER_REPOSITORY'].by_id(session['session_id'])
    return make_response(render_template(
        'posts/home.html',
        user=user,
    ))


@router.route('/create', methods=['GET'])
def create_form():
    pass


@router.route('/create', methods=['POST'])
def create_action():
    pass

