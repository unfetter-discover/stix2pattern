import pytest
from translatesigma.blueprint import sigma_bp, InvalidUsage
from .sigma_samples import valid_sigma_samples, valid_yaml_samples, invalid_yaml_samples
import json
from flask import Flask, jsonify

app = Flask(__name__.split('.')[0])
app.register_blueprint(sigma_bp)

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    """
    Handler for errors
    """
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@pytest.fixture
def client(request):
    """
    Fixture to help manage creation and teardown of the Flask App
    """
    test_client = app.test_client()

    def teardown():
        """
        Holder function for teardown of the Flask App
        """
        pass  # databases and resourses have to be freed at the end. But so far we don't have anything

    request.addfinalizer(teardown)
    return test_client


def post_json(client, url, json_dict):
    """Send dictionary json_dict as a json to the specified url """
    data = {}
    data['pattern'] = json_dict
    return client.post(url, data=json.dumps(data), content_type='application/json')


def json_of_response(response):
    """Decode json from response"""
    return json.loads(response.data.decode('utf8'))


VALIDATE_SAMPLES = [
    (pattern, validated) for pattern, validated, _ in valid_sigma_samples + valid_yaml_samples + invalid_yaml_samples
]


@pytest.mark.parametrize(u"pattern, validated", VALIDATE_SAMPLES)
def test_validate(client, pattern, validated):
    response = post_json(client, 'validate', pattern)
    assert response.status_code == 200
    resp_data = json.loads(response.data.decode('utf8'))
    assert resp_data['validated'] == validated


TRANSLATE_ALL_SAMPLES = valid_sigma_samples + valid_yaml_samples + invalid_yaml_samples

@pytest.mark.parametrize(u"pattern, validated, translations", TRANSLATE_ALL_SAMPLES)
def test_translate_all(client, pattern, validated, translations):
    response = post_json(client, 'translate-all', pattern)
    assert response.status_code == 200
    resp_data = json.loads(response.data.decode('utf8'))
    if translations is None:
        assert 'translations' not in resp_data
    else:
        resp_translations = resp_data['translations']
        for translation in translations:
            filtered = list(filter(lambda x: x['tool'] == translation['tool'], resp_translations))
            assert len(filtered) > 0
            assert filtered[0]['query'] == translation['query']

@pytest.mark.parametrize(u"endpoint", [
    ("validate"),
    ("translate-all")
])
def test_nodata(client, endpoint):
    """
    Test when no data is submitted
    """
    url = endpoint
    response = client.post(url, data="", content_type='application/json')
    assert response.status_code == 400
