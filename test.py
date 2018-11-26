import sys
import socket
import json
import pprint
import pytest
from app import app
import os


# The API for stix2pattern is found at https://app.swaggerhub.com/apis/unfetter/stix2pattern/1.0.0

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

#  I can't get this to run on the command line

# want to use paraemeterization, but how do I do the fixture?
# need to add the bad, and then run the tests from the


# Test the "validated"
VALIDATE_PASS_RESPONSE = [
    ("[file:size = 1280]", True),
    ("[file:size != 1280]", True),
    ("[file:size < 1024]", True),
    ("[file:size <= 1024]", True),
    ("[file:size > 1024]", True),
    ("[file:size >= 1024]", True),
    ("[file:file_name = 'my_file_name']", True),
    ("[file:extended_properties.'ntfs-ext'.sid = '234']", True),
    ("[ipv4addr:value ISSUBSET '192.168.0.1/24']", True),
    ("[ipv4addr:value NOT ISSUBSET '192.168.0.1/24']", True),
    ("[user-account:value = 'Peter'] AND [user-account:value != 'Paul'] AND [user-account:value = 'Mary'] WITHIN 5 SECONDS", True),
    ("[file:file_system_properties.file_name LIKE 'name%']", True),
    ("[file:file_name IN ('test.txt', 'test2.exe', 'README')]", True),
    ("[file:size IN (1024, 2048, 4096)]", True),
    ("[network-connection:extended_properties[0].source_payload MATCHES 'dGVzdHRlc3R0ZXN0']", True),
    ("[win-registry-key:key = 'hkey_local_machine\\\\foo\\\\bar'] WITHIN 5 SECONDS", True)
]


@pytest.mark.parametrize(u"pattern,validated", VALIDATE_PASS_RESPONSE)
def test_validate(client, pattern, validated):
    """
    Test the Validate endpoint
    """
    response = post_json(client, '/validate', pattern)
    assert response.status_code == 200
    expectedValue = {}
    expectedValue['pattern'] = pattern
    expectedValue['validated'] = validated
    assert response.data.decode('utf8') == json.dumps(
        expectedValue, sort_keys=True)

# Test only the CAR-Elastic translation


CAR_ELASTIC_PASS = [
    ("[file:hashes.MD5 = '79054025255fb1a26e4bc422aef54eb4']",
     'data_model.object:file AND data_model.fields.md5_hash:"79054025255fb1a26e4bc422aef54eb4"'),
    ("[process:pid NOT IN (1, 2, 3) AND process:name = 'wsmprovhost.exe']",
     '(data_model.object:process AND data_model.fields.exe:\"wsmprovhost.exe\") AND (data_model.object:process AND NOT(data_model.fields.pid:(1 OR 2 OR 3)))'),
]


@pytest.mark.parametrize(u"pattern,translation", CAR_ELASTIC_PASS)
def test_car_splunk(client, pattern, translation):
    """
    Test the car-splunk endpoint
    """
    response = post_json(client, '/car-elastic', pattern)
    assert response.status_code == 200
    expectedValue = {}
    expectedValue['pattern'] = pattern
    expectedValue['validated'] = True
    expectedValue['car-elastic'] = translation
    assert response.status_code == 200
    assert json.dumps(json.loads(response.data.decode('utf8')),
                      sort_keys=True) == json.dumps(expectedValue, sort_keys=True)


# This will test against all translations.  The parameter is (stix-pattern, expected validated value (True/False),
# [car-elastic result, car-splunk result, cim-splunk result, get objects]
TRANSLATE_SUCESS = [
    ("[file:hashes.MD5 = '79054025255fb1a26e4bc422aef54eb4']", True,
     ['data_model.object:file AND data_model.fields.md5_hash:"79054025255fb1a26e4bc422aef54eb4"',
      '|where (match(tag, "dm-file-.*") AND md5_hash = "79054025255fb1a26e4bc422aef54eb4")',
      '|where (tag="endpoint" AND file_hash = "79054025255fb1a26e4bc422aef54eb4")']),

    ("[process:pid NOT IN (1, 2, 3) AND process:name = 'wsmprovhost.exe']", True,
     ['(data_model.object:process AND data_model.fields.exe:\"wsmprovhost.exe\") AND (data_model.object:process AND NOT(data_model.fields.pid:(1 OR 2 OR 3)))',
      '|where ((match(tag, "dm-process-.*") AND exe = "wsmprovhost.exe") AND (match(tag, "dm-process-.*") AND NOT (pid IN (1, 2, 3))))',
      '|where ((tag="process" AND process = "wsmprovhost.exe") AND (tag="process" AND NOT (pid IN (1, 2, 3))))']),
    ("[process:name NOT LIKE '%.exe' AND process:pid >= 4]", True,
     [
         '(data_model.object:process AND data_model.fields.pid:>=4) AND (data_model.object:process AND NOT(data_model.fields.exe:*.exe))',
         '|where ((match(tag, "dm-process-.*") AND pid >= 4) AND (match(tag, "dm-process-.*") AND NOT (match(exe, \"^%\\.exe$\"))))',
         '|where ((tag="process" AND pid >= 4) AND (tag="process" AND NOT (match(process, \"^%\\.exe$\"))))',
     ])
]


@pytest.mark.parametrize(u"pattern, validated, translatedResults", TRANSLATE_SUCESS)
def test_every_translate(client, pattern, validated, translatedResults):
    """
    Test each of the car-elastic, car-splunk and cim-splunk endpoints
    This test makes it easier to document multiple translations for a given pattern
    """
    for i, endpoint in enumerate(["car-elastic", "car-splunk", "cim-splunk"]):
        response = post_json(client, '/'+endpoint, pattern)
        expectedValue = {}
        expectedValue['pattern'] = pattern
        expectedValue['validated'] = validated
        expectedValue[endpoint] = translatedResults[i]
        assert response.status_code == 200
        assert json.dumps(json.loads(response.data.decode(
            'utf8')), sort_keys=True) == json.dumps(expectedValue, sort_keys=True)


@pytest.mark.parametrize(u"pattern, validated, translatedResults", TRANSLATE_SUCESS)
def test_translate_all(client, pattern, validated, translatedResults):
    """
    Test the translate-all endpoint
    """
    response = post_json(client, '/translate-all', pattern)
    assert response.status_code == 200
    expectedValue = {}
    expectedValue['pattern'] = pattern
    expectedValue['validated'] = validated
    for i, endpoint in enumerate(["car-elastic", "car-splunk", "cim-splunk"]):
        expectedValue[endpoint] = translatedResults[i]
    assert json.dumps(json.loads(response.data.decode('utf8')),
                      sort_keys=True) == json.dumps(expectedValue, sort_keys=True)


CAR_SPLUNK_PASS = [
    ("[process:pid NOT IN (1, 2, 3) AND process:name = 'wsmprovhost.exe']",
     '|where ((match(tag, \"dm-process-.*\") AND exe = \"wsmprovhost.exe\") AND (match(tag, \"dm-process-.*\") AND NOT (pid IN (1, 2, 3))))')
]


@pytest.mark.parametrize(u"pattern,translation", CAR_SPLUNK_PASS)
def test_car_splunk(client, pattern, translation):
    response = post_json(client, '/car-splunk', pattern)
    assert response.status_code == 200
    expectedValue = {}
    expectedValue['pattern'] = pattern
    expectedValue['validated'] = True
    expectedValue['car-splunk'] = translation
    assert response.status_code == 200
    assert json.dumps(json.loads(response.data.decode('utf8')),
                      sort_keys=True) == json.dumps(expectedValue, sort_keys=True)


@pytest.mark.parametrize(u"endpoints", [
    ("validate"),
    ("get-objects"),
    ("cim-splunk"),
    ("car-elastic"),
    ("car-splunk"),
    ("translate-all")
])
def test_nodata(client, endpoints):
    """
    Test when no data is submitted
    """
    url = endpoints
    response = client.post(url, data="", content_type='application/json')
    assert response.status_code == 400


GET_OBJECTS = [
    ("[file:hashes.MD5 = '79054025255fb1a26e4bc422aef54eb4']",
     '[{"name": "file", "property": "hashes"}]'),
    ("[process:pid NOT IN (1, 2, 3) AND process:name = 'wsmprovhost.exe']",
     '[{"name": "process", "property": "pid"}, {"name": "process", "property": "name"}]')
]


@pytest.mark.parametrize(u"pattern, objects", GET_OBJECTS)
def test_get_object(client, pattern, objects):
    """
    Tests the "get_objects" endpoint
    """
    response = post_json(client, '/get-objects', pattern)
    expectedValue = {}
    expectedValue['pattern'] = pattern
    expectedValue['validated'] = True
    expectedValue['object'] = json.loads(objects)
    assert response.status_code == 200
    assert json.dumps(json.loads(response.data.decode('utf8')),
                      sort_keys=True) == json.dumps(expectedValue, sort_keys=True)
