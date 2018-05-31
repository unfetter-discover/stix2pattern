FROM python:3.6

COPY app.py /opt/stix/app.py
COPY gunicorn_config.py /opt/stix/gunicorn_config.py
#ADD ./ /root/
#RUN python /root/setup.py --help-commands
COPY ./templates/* /opt/stix/templates/
RUN pip3 install flask --default-timeout=100
RUN pip3 install stix2-validator --default-timeout=100
RUN pip3 install stix-pattern-translator --default-timeout=100
RUN pip3 install gunicorn --default-timeout=100
# Start Application
EXPOSE 5000
WORKDIR /opt/stix/

CMD ["gunicorn", "--config", "/opt/stix/gunicorn_config.py", "app:app"]
