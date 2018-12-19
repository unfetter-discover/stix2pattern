import pytest
import json

from translatesigma.blueprint import sigma_bp, InvalidUsage
from .sigma_samples import valid_sigma_samples, valid_yaml_samples, invalid_yaml_samples
from .helpers import post_json, json_of_response, create_app_from_blueprint

app = create_app_from_blueprint(sigma_bp)


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
        for i in range(0, len(translations)):
            assert len(resp_translations[i]) == len(translations[i])
            assert all(v == resp_translations[i][k] for k, v in translations[i].items())


@pytest.mark.parametrize(u"endpoint", [
    ("validate"),
    ("translate-all")
])
def test_no_data(client, endpoint):
    """
    Test when no data is submitted
    """
    url = endpoint
    response = client.post(url, data="", content_type='application/json')
    assert response.status_code == 400
