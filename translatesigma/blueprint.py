from flask import Blueprint, request, jsonify
from typing import Any

from . import process_sigma
from shared.errors import InvalidUsage

sigma_bp = Blueprint('sigma', __name__)


def handle_req(req: request, translate: bool) -> Any:
    """
    Handles common tasks for both validate and translate routes

    :param req: request
    :param translate: bool
    :return: json
    """
    if req.data:
        req_object = req.get_json()
        if 'pattern' not in req_object:
            raise InvalidUsage('Pattern is required', status_code=400)
        pattern = req_object['pattern']
        response = process_sigma(pattern, translate)
        return jsonify(response)
    else:
        raise InvalidUsage('No Request Data', status_code=400)


@sigma_bp.route('/validate', methods=['POST'])
def validate() -> Any:
    """
    :return: json

    Validates SIGMA
    """
    return handle_req(request, False)


@sigma_bp.route('/translate-all', methods=['POST'])
def translate_all() -> Any:
    """
    :return: json

    Validates and translates SIGMA
    """
    return handle_req(request, True)
