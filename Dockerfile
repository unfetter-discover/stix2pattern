FROM python:3.6

COPY app.py /opt/stix/app.py
#ADD ./ /root/
#RUN python /root/setup.py --help-commands
RUN pip3 install flask
RUN pip3 install stix2-validator
RUN pip3 install stix-pattern-translator
# Start Application
EXPOSE 5000
WORKDIR /opt/stix/

CMD ["python3","app.py","0.0.0.0"]