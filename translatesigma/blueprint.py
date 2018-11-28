from flask import Blueprint, request
import json

from . import process_sigma
from shared.errors import InvalidUsage

sigma_bp = Blueprint('sigma', __name__)


@sigma_bp.route('/validate', methods=['POST'])
def validate() -> str:
    """
    :return: str (JSON string)

    Calls the validate function
    """
    if request.data:

        pattern = request.data.decode("utf-8")  # decode the input string
        pattern_object = json.loads(pattern)
        pattern = pattern_object['pattern']
        response = process_sigma(pattern)
        return json.dumps(response)
    else:
        raise InvalidUsage('No Request Data', status_code=400)


@sigma_bp.route('/translate-all', methods=['POST'])
def translate_all() -> str:
    """
    :return: str (JSON string)

    Calls the validate function
    """
    if request.data:

        pattern = request.data.decode("utf-8")  # decode the input string
        pattern_object = json.loads(pattern)
        pattern = pattern_object['pattern']
        response = process_sigma(pattern, True)
        return json.dumps(response)
    else:
        raise InvalidUsage('No Request Data', status_code=400)
