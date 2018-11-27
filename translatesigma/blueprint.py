from flask import Blueprint, request
from . import process_sigma
import json

sigma_bp = Blueprint('sigma', __name__)

class InvalidUsage(Exception):
    """
    Exception class for when the data request is invalid
    """
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@sigma_bp.route('/validate', methods=['POST'])
def validate():
    """
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
def translate_all():
    """
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
