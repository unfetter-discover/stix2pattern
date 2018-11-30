import sys
import socket
import json
from flask import Flask, request, jsonify
from stix2patterns.validator import validate
from stix2patterns.pattern import Pattern
from stix2patterns import inspector
from stix2patterns_translator import translate, SearchPlatforms, DataModels

from translatesigma.blueprint import sigma_bp
from shared.errors import InvalidUsage

# The API for stix2pattern is found at https://app.swaggerhub.com/apis/unfetter/stix2pattern/1.0.0

""" TODO: return the results in JSON.
    catch errors and render them in JSON back to requestor."""

app: Flask = Flask(__name__.split('.')[0])


def build_translation(request_translation, request_data):
    """
    Function that will convert the REST input and call the appriate translation
    """
    if request_data:
        pattern = request_data.decode("utf-8")  # decode the input string
        pattern_object = json.loads(pattern)
        return_object = {
            'pattern': pattern_object['pattern']
        }
        try:
            return_object['validated'] = pass_test = validate(
                pattern_object['pattern'], ret_errs=False, print_errs=True)
        except Exception as e:
            return_object['validated'] = False
            return json.dumps(return_object)
        for translation in request_translation:
            if translation == "car-elastic":
                output_language = SearchPlatforms.ELASTIC
                output_data_model = DataModels.CAR
            elif translation == "car-splunk":
                output_language = SearchPlatforms.SPLUNK
                output_data_model = DataModels.CAR
            elif translation == "cim-splunk":
                output_language = SearchPlatforms.SPLUNK
                output_data_model = DataModels.CIM
            else:
                raise InvalidUsage('Invalid Request Data', status_code=400)

            try:
                return_object[translation] = None
                return_object[translation] = translate(
                    pattern_object['pattern'], output_language, output_data_model)
            except Exception as e:
                pass

        return json.dumps(return_object)
    else:
        raise InvalidUsage('No Request Data', status_code=400)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    """
    Handler for errors
    """
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/car-elastic', methods=['POST'])
def car_elastic():
    return build_translation(["car-elastic"], request.data)


@app.route('/car-splunk', methods=['POST'])
def car_splunk():
    return build_translation(["car-splunk"], request.data)


@app.route('/cim-splunk', methods=['POST'])
def cim_splunk():
    return build_translation(["cim-splunk"], request.data)


@app.route('/translate-all', methods=['POST'])
def translate_all():
    return build_translation(["car-elastic", "car-splunk", "cim-splunk"], request.data)


@app.route('/get-objects', methods=['POST'])
def get_objects():
    """
    Returns just the objects that are part of the STIX object
    """
    if request.data:
        pattern = request.data.decode("utf-8")  # decode the input string
        pattern_object = json.loads(pattern)
        return_object = {}
        return_object['pattern'] = pattern_object['pattern']
        try:
            return_object['validated'] = validate(
                pattern_object['pattern'], ret_errs=False, print_errs=True)
            compiled_pattern = Pattern(pattern_object['pattern'])

            theinspector = inspector.InspectionListener()
            compiled_pattern.walk(theinspector)
            res = {}
            res_array = []
            for i in list(theinspector.pattern_data().comparisons.items()):
                name = i[0]
                for j in i[1]:
                    object = {}
                    object["name"] = name
                    object["property"] = j[0][0]
                    res_array.append(object)
                return_object['object'] = res_array
            return json.dumps(return_object)

        except Exception as e:
            return_object['validated'] = False
            return json.dumps(return_object)
    else:
        raise InvalidUsage('No Request Data', status_code=400)


@app.route('/validate', methods=['POST'])
def call_validate():
    """
    Calls the validate function
    """
    if request.data:

        pattern = request.data.decode("utf-8")  # decode the input string
        pattern_object = json.loads(pattern)
        return_object = {}
        return_object['pattern'] = pattern_object['pattern']
        try:
            return_object['validated'] = validate(
                return_object['pattern'], ret_errs=False, print_errs=True)
            return json.dumps(return_object)

        except Exception as e:
            return_object['validated'] = False
            return json.dumps(return_object)
    else:
        raise InvalidUsage('No Request Data', status_code=400)


@app.route('/heartbeat')
def heartbeat():
    return json.dumps({'success': True, 'service': 'unfetter-pattern-handler', 'status': 'RUNNING'})


app.register_blueprint(sigma_bp, url_prefix="/sigma")


def main():
    ip = None
    try:
        socket.inet_aton(sys.argv[1])
        ip = sys.argv[1]
    except Exception as e:
        ip = '127.0.0.1'
    finally:
        print(f'IP is {ip}')
        app.run(port=5000, host=ip)


if __name__ == '__main__':
    main()
