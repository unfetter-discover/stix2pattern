from flask import Flask, jsonify, Blueprint
import json

from shared.errors import InvalidUsage


def post_json(client, url, json_dict):
    """Send dictionary json_dict as a json to the specified url """
    data = {
        'pattern': json_dict
    }
    return client.post(url, data=json.dumps(data), content_type='application/json')


def json_of_response(response):
    """Decode json from response"""
    return json.loads(response.data.decode('utf8'))


def create_app_from_blueprint(blueprint: Blueprint) -> Flask:
    app = Flask(__name__.split('.')[0])
    app.register_blueprint(blueprint)

    @app.errorhandler(InvalidUsage)
    def handle_invalid_usage(error):
        """
        Handler for errors
        """
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    return app
