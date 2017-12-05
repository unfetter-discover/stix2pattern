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

def run_server(): # used only by test module to start dev server
    
    app.run(debug=True, port=5000, host=IP)

@app.route('/')
def welcome(results=None):
    return render_template('webform.html', results=results)

@app.route('/action-page', methods=['POST'])
def action():
    pattern = request.form['pattern']
    route = request.form['function']
    if route == "car-elastic":
        outputLanguage = SearchPlatforms.ELASTIC
        outputDataModel = DataModels.CAR
        returnObject = {}
        returnObject['stix-pattern'] = pattern
        returnObject['car-elastic'] = translate(
            pattern, outputLanguage, outputDataModel)
        return json.dumps(returnObject)
    elif route == "validate":
        try:
            pass_test = validate(pattern, ret_errs=False, print_errs=False)
            return '{"validated":"true"}'
        except (EOFError, KeyboardInterrupt):
            return '{"validated":"false"}'
        except:
            return '{"validated":"false"}'

@app.route('/car-elastic', methods=['POST'])
def car_elastic():
    outputLanguage = SearchPlatforms.ELASTIC
    outputDataModel = DataModels.CAR
    if request.data:
        pattern = request.data.decode("utf-8")  # decode the input string
        returnObject = {}
        returnObject['stix-pattern'] = pattern
        returnObject['car-elastic'] = translate(
            pattern, outputLanguage, outputDataModel)
        return json.dumps(returnObject)
    else:
        print("No Request Data")  # when issues with input data
        return "No Request Data"


@app.route('/car-splunk', methods=['POST'])
def car_splunk():
    outputLanguage = SearchPlatforms.SPLUNK
    outputDataModel = DataModels.CAR
    if request.data:
        pattern = request.data.decode("utf-8")  # decode the input string
        output = translate(
            pattern, outputLanguage, outputDataModel)
        returnObject = {}
        returnObject['stix-pattern'] = pattern
        returnObject['car_splunk'] = output

        return json.dumps(returnObject)
    else:
        print("No Request Data")  # when issues with input data
        return "No Request Data"

@app.route('/cim-splunk', methods=['POST'])
def cim_splunk():
    outputLanguage = SearchPlatforms.SPLUNK
    outputDataModel = DataModels.CIM
    if request.data:
        pattern = request.data.decode("utf-8") # decode the input string
        output = translate(
            pattern, outputLanguage, outputDataModel
        )
        returnObject = {}
        returnObject['stix-pattern'] = pattern
        returnObject['cim-splunk'] = output

        return json.dumps(returnObject)
    else:
        print("No Request Data") # when issues with input data
        return "No Request Data"



@app.route('/get-objects', methods=['POST'])
def getObjects():
    if request.data:
        pattern = request.data.decode("utf-8")  # decode the input string
        print(pattern)
        try:
            pass_test = validate(pattern, ret_errs=False, print_errs=False)
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
                res['object']=resArray
            return json.dumps(res)

        except (EOFError, KeyboardInterrupt):
            return '{"validated":"false"}'
        except:
            return '{"validated":"false"}'
    else:
        print("No Request Data")  # when issues with input data
        return "No Request Data"


@app.route('/validate', methods=['POST'])
def callValidate():
    if request.data:
        pattern = request.data.decode("utf-8")  # decode the input string
        print(pattern)
        try:
            pass_test = validate(pattern, ret_errs=False, print_errs=False)
            return '{"validated":"true"}'

        except (EOFError, KeyboardInterrupt):
            return '{"validated":"false"}'
        except:
            return '{"validated":"false"}'
    else:
        print("No Request Data")  # when issues with input data
        return "No Request Data"

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
