import sys
import socket
import json

from flask import render_template

from stix2patterns.validator import validate
from stix2patterns.inspector import INDEX_STAR
from stix2patterns.pattern import Pattern
from stix2patterns import inspector
from flask import Flask, request, render_template, jsonify
from stix2patterns_translator import translate, SearchPlatforms, DataModels

# EXAMPLE Usage - accepts a STIX2 string as input via POST:
#    curl -X POST
#         -H "Content-Type:text/plain"
#         -d "[process:pid <= 5]"
#         http://127.0.0.1:5000/car-elastic

""" TODO: return the results in JSON.
    catch errors and render them in JSON back to requestor."""

app = Flask(__name__.split('.')[0])

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

def run_server(): # used only by test module to start dev server
    app.run(debug=True, port=5000, host=IP)


def buildTranslation(requestTranslation, requestData):
    """
    Function that will convert the REST input and call the appriate translation
    """    
    if requestData:
        pattern = requestData.decode("utf-8")  # decode the input string
        patternObject = json.loads(pattern)
        returnObject = {}
        returnObject['pattern'] = patternObject['pattern']
        try:
            returnObject['validated'] = pass_test = validate(patternObject['pattern'], ret_errs=False, print_errs=True)
        except (EOFError, KeyboardInterrupt):
            returnObject['validated'] = False
            return json.dumps(returnObject)
        except:
            returnObject['validated'] = False
            return json.dumps(returnObject)
        for translation in requestTranslation:
            if translation == "car-elastic":
                outputLanguage = SearchPlatforms.ELASTIC
                outputDataModel = DataModels.CAR
            elif translation == "car-splunk":
                outputLanguage = SearchPlatforms.SPLUNK
                outputDataModel = DataModels.CAR
            elif translation == "cim-splunk":
                outputLanguage = SearchPlatforms.SPLUNK
                outputDataModel = DataModels.CIM
            else:
                raise InvalidUsage('Invalid Request Data', status_code=400)
        
            try:
                returnObject[translation] = None
                returnObject[translation] = translate(
                    patternObject['pattern'], outputLanguage, outputDataModel)
            except:
                pass

        return json.dumps(returnObject)
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
    return buildTranslation(["car-elastic"], request.data)

@app.route('/car-splunk', methods=['POST'])
def car_splunk():
    return buildTranslation(["car-splunk"], request.data)


@app.route('/cim-splunk', methods=['POST'])
def cim_splunk():
    return buildTranslation(["cim-splunk"], request.data)    
    
@app.route('/translate-all', methods=['POST'])
def translate_ll():
    return buildTranslation(["car-elastic", "car-splunk", "cim-splunk"], request.data)    
    



@app.route('/get-objects', methods=['POST'])
def getObjects():
    """
    Returns just the objects that are part of the STIX object
    """    
    if request.data:
        pattern = request.data.decode("utf-8")  # decode the input string
        patternObject = json.loads(pattern)
        returnObject = {}
        returnObject['pattern'] = patternObject['pattern']
        try:
            returnObject['validated'] = validate(pattern, ret_errs=False, print_errs=False)
            compiled_pattern = Pattern(pattern)

            theinspector = inspector.InspectionListener()
            compiled_pattern.walk(theinspector)
            res={}
            resArray = []
            for i in list(theinspector.pattern_data().comparisons.items()):
                name = i[0]
                for j in i[1]:
                        object = {}
                        object["name"] = name
                        object["property"] = j[0][0]
                        resArray.append(object)
                returnObject['object']=resArray
            return json.dumps(returnObject)

        except (EOFError, KeyboardInterrupt):
            returnObject['validated'] = False
            return json.dumps(returnObject)
        except:
            returnObject['validated'] = False
            return json.dumps(returnObject)
    else:
        raise InvalidUsage('No Request Data', status_code=400)


@app.route('/validate', methods=['POST'])
def callValidate():
    """
    Calls the validate function
    """  
    if request.data:

        pattern = request.data.decode("utf-8")  # decode the input string
        patternObject = json.loads(pattern)
        returnObject = {}
        returnObject['pattern'] = patternObject['pattern']
        try:
            returnObject['validated'] = validate(returnObject['pattern'], ret_errs=False, print_errs=False)
            return json.dumps(returnObject)

        except (EOFError, KeyboardInterrupt):
            returnObject['validated'] = False
            return json.dumps(returnObject)
        except:
            returnObject['validated'] = False
            return json.dumps(returnObject)
    else:
        raise InvalidUsage('No Request Data', status_code=400)

def main():
    
    try:
        socket.inet_aton(sys.argv[1])
        IP  = sys.argv[1]
    except:
        IP = '127.0.0.1'
    finally:
        print("IP is "+IP)
        app.run(port=5000, host=IP)

if __name__ == '__main__':
    #### DEVELOPMENT Settings, change for production!!!
    main()
