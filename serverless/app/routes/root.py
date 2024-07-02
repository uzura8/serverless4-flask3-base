from flask import Blueprint, jsonify

bp = Blueprint('root', __name__)


@bp.get('/')
def index():
    return jsonify({'message': 'This is content-api'})


@bp.get('/<path:path>')
def any_path(path):
    return jsonify({'message': 'Here: /' + path})
