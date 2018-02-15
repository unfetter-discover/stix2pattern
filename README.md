# STIX2Pattern Web Service

This project builds a FLASK project around the [stix2-validator](https://www.github.com/oasis-open/cti-stix-validator) and [stix-pattern-translator](https://www.github.com/mitre/stix2pattern_translator) projects.  

The API for the web services can be found at the [Unfetter Swagger Hub](https://app.swaggerhub.com/search?type=API&owner=unfetter) project, called the [stix2pattern api](https://app.swaggerhub.com/apis/unfetter/stix2pattern/1.0.0)


# Build With Docker
You can build and run this docker container with the following commands
* docker build . -t stix-pattern
* docker run -it stix-pattern 


# Run Tests
PyTest is implemented to test the API.  It is recommended you create a python virtual environment first.  You can run those tests by doing the following:

* Install Python 3.6
* RUN pip3 install flask
* RUN pip3 install stix2-validator
* RUN pip3 install stix-pattern-translator
* RUN pytest test.py -sv

